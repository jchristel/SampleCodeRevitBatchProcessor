"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions for the file selection GUI.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# this sample shows how to write out a number of task files using bucket distribution by file size

import clr
import System
import os


# import file item class
from duHast.UI.Objects import file_item as fi

# import workloader utils
from duHast.UI import workloader as wl

# custom result class
from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_io import (
    is_back_up_file,
    get_file_size as files_io_get_file_size,
    FILE_SIZE_IN_KB,
)
from duHast.Utilities.files_get import (
    get_files,
    get_files_from_directory_walker_with_filters_simple,
)
from duHast.Utilities.files_csv import get_first_row_in_csv_file, read_csv_file
from duHast.Utilities.files_tab import get_first_row_in_file_no_strip
from duHast.Revit.BIM360.util_bim_360 import get_bim_360_file_data


# -------------
# my code here:
# -------------


def get_revit_files_for_processing(location, include_sub_dirs, file_extension):
    """
    Extracts file data from varies sources:
        - bim 360 task text file
        - files on a local server directory
        - files on a local server directory and it's subdirectories
        - local server based files provided through a task text file

    :param location: Can either be a directory, or a fully qualified file path.
    :type location: str
    :param includeSubDirs: If true and location is a directory, subdirectories will be included in file search.
    :type includeSubDirs: bool
    :param fileExtension: File type filter in '.ext'
    :type fileExtension: str

    :return: List of MyFileItem objects.
    :rtype: :class:`.MyFileItem`
    """

    revit_files = []
    try:
        if os.path.isfile(location):
            # got a text file...could either be BIM360 data or a file task list
            revit_files = _get_file_data_from_text_file(location)
        elif os.path.isdir(location):
            # check a to search for files is to include sub dirs
            revit_files_unfiltered = []
            if include_sub_dirs:
                # get revit files in input dir and subdirs (with backup files removed already)
                revit_files_unfiltered = get_revit_files_incl_sub_dirs(
                    location, file_extension
                )
            else:
                # get revit files in input dir (with backup files removed already)
                revit_files_unfiltered = get_revit_files(location, file_extension)
            # check for max path violations!
            # The specified path, file name, or both are too long. The fully qualified file name must be less than 260 characters, \
            # and the directory name must be less than 248 characters.
            for revit_file in revit_files_unfiltered:
                # remove any back up files from selection
                if (
                    len(os.path.dirname(os.path.abspath(revit_file.name))) < 248
                    and len(revit_file.name) < 260
                ):
                    revit_files.append(revit_file)
    except Exception as e:
        # return an empty list which will cause this script to abort
        revit_files = []
    return revit_files


def _get_files_from_list_file(file_path_csv):
    """
    Reads server based file data, the fully qualified file path, from a task file list file in csv format.

    :param filePathCSV: The fully qualified file path to the task list file.
    :type filePathCSV: str

    :return: A list of MyFileitem objects. If an exception occured an empty list will be returned.
    :rtype: :class:`.MyFileItem`
    """

    revit_files = []
    try:
        # read the CSV into rows
        rows = read_csv_file(file_path_csv)
        # check whether anything came back
        if len(rows) > 0:
            # process rows
            for row_data in rows:
                if len(row_data) > 0:
                    file_size = files_io_get_file_size(row_data[0], FILE_SIZE_IN_KB)
                    dummy = fi.MyFileItem(row_data[0], file_size)
                    revit_files.append(dummy)
    except Exception as e:
        # return an empty list which will cause this script to abort
        revit_files = []
    return revit_files


def get_files_from_csv_list_file(file_path_csv, file_extension):
    """
    Reads server based file data, the fully qualified file path, from a task file list file in csv format.

    :param filePathCSV: The fully qualified file path to the task list file.
    :type filePathCSV: str
    :param fileExtension: The file extension filter in format '.ext'
    :type fileExtension: str
    :return: A list of MyFileitem objects. If an exception occured an empty list will be returned.
    :rtype: :class:`.MyFileItem`
    """

    revit_files = _get_files_from_list_file(file_path_csv)
    # filter out files with wrong extension
    revit_files = [f for f in revit_files if f.name.lower().endswith(file_extension)]
    return revit_files


def _get_file_data_from_text_file(file_path):
    """
    Reads a file server based task list file. This file can either be a BIM360 task list file or \
        a task list file containing file server based file path in a single column.

    :param filePath: The fully qualified file path to the task list file.
    :type filePath: str
    :return: A list of MyFileitem objects.
    :rtype: :class:`.MyFileItem`
    """

    files = []

    # if file is empty an empty list will be returned
    # also need to check whether this is a csv file...
    if file_path.lower().endswith(".csv"):
        # list of entries in first row
        row = get_first_row_in_csv_file(file_path)
    else:
        row = get_first_row_in_file_no_strip(file_path)
        # make sure we get a list of entries
        if row is not None:
            row = row.split("\t")
    if row is not None:
        # bim 360 or autodesk construction cloud files have at least 3 entries
        if len(row) > 2:
            files = get_bim_360_file_data(file_path)
        else:
            files = _get_files_from_list_file(file_path)
    return files


def get_revit_files(directory, file_extension):
    """
    Returns files in a given directory and of a given file extension.

    :param directory: The fully qualified directory path.
    :type directory: str
    :param file_extension: The file extension filter in format '.ext'
    :type file_extension: str

    :return: List of file items
    :rtype: [:class:`.FileItem`]
    """

    files = []
    list_of_files = get_files(directory, file_extension)
    for f in list_of_files:
        # check if this is a back up file
        if is_back_up_file(f) == False:
            # Get size and add to list of files.
            size = os.path.getsize(f)
            files.append(fi.MyFileItem(f, size))
    return files


def get_revit_files_incl_sub_dirs(directory, file_extension):
    """
    Returns files in a given directory and its sub directories of a given file extension.

    :param directory: The fully qualified directory path.
    :type directory: str
    :param file_extension: The file extension filter in format '.ext'
    :type file_extension: str

    :return: List of file items
    :rtype: [:class:`.FileItem`]
    """

    files = []
    # Get the list of all files in directory tree at given path
    list_of_files = get_files_from_directory_walker_with_filters_simple(
        directory, file_extension
    )

    for f in list_of_files:
        # check if this is a back up file,
        if is_back_up_file(f) == False:
            # Get size and add to list of files.
            size = os.path.getsize(f)
            files.append(fi.MyFileItem(f, size))
    return files


def get_file_size(item):
    """
    Helper used to define workload size (same as file size)

    :param item: A file item object instance.
    :type item: :class:`.FileItem`

    :return: The file size.
    :rtype: int
    """

    return item.size


def bucket_to_task_list_file_system(item):
    """
    Default task list content for files on a file server location.

    :param item: A file item object instance.
    :type item: :class:`.FileItem`

    :return: The item name.(fully qualified file path)
    :rtype: str
    """

    return item.name


def bucket_to_task_list_bim_360(item):
    """
    Default task list content for files on a BIM 360 cloud drive.

    :param item: A file item object instance.
    :type item: :class:`.FileItem`

    :return: The revit version, project guid, file guid separated by a space ' '
    :rtype: str
    """

    return " ".join(
        [item.bim_360_revit_version, item.bim_360_project_guid, item.bim_360_file_guid]
    )


def write_revit_task_file(file_name, bucket, get_data=bucket_to_task_list_file_system):
    """
    Writes out a task list file.

    :param file_name: Fully qualified file path of the task file name including extension.
    :type file_name: str
    :param bucket: Workload bucket object instance.
    :type bucket: :class:`.WorkloadBucket`
    :param get_data: Returns data from file item object to be written to file, defaults to BucketToTaskListFileSystem
    :type get_data: func(:class:`.FileItem`) -> str, optional

    :return:
        Result class instance.

        - Write file status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message property contains fully qualified file path to task list file.

        On exception:

        - .status (bool) will be False.
        - .message will contain the exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        f = open(file_name, "w")
        row_counter = 0
        for p in bucket.items:
            data = get_data(p)
            # check whether first row
            if row_counter != 0:
                # if not first row add line feed character before data written
                data = "\n" + data
            else:
                row_counter += 1
            # this looks horrible: but:
            # string.encode('utf-8') returns a byte string b''
            # so it needs to be converted to an actual string again
            f.write(data.encode("utf-8").decode("utf-8"))
        f.close()
        return_value.append_message("wrote task list: {} [TRUE]".format(file_name))
        return_value.result.append(file_name)
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write task list: {} with exception {}".format(file_name, e),
        )
    return return_value


def write_file_list(
    directory_path,
    file_extension,
    task_list_directory,
    task_files_number,
    file_getter,
    file_data_processor=bucket_to_task_list_file_system,
):
    """
    Writes out all task list(s) to file(s).

    :param directory_path: Fully qualified directory path containing files to be added to task lists.
    :type directory_path: str
    :param file_extension: A file extension filter in format '.ext'
    :type file_extension: str
    :param task_list_directory: The fully qualified directory path where the task files will be written .
    :type task_list_directory: str
    :param task_files_number: The number of task files to be written.
    :type task_files_number: int
    :param file_getter: Function accepting a directory and file extension filter and returns file items from directory.
    :type file_getter: func(str, str) -> :class:`.FileItem`
    :param file_data_processor: Function processing file item and returns a string to be written to task list file, defaults to BucketToTaskListFileSystem
    :type file_data_processor: func(:class:`.FileItem`) -> str, optional

    :return:
        Result class instance.

        - Write file status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message property contains fully qualified file path for each task list file.

        On exception:

        - .status (bool) will be False.
        - .message will contain the exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    return_value.status = True
    # get revit files in input dir
    revit_files = file_getter(directory_path, file_extension)
    # build bucket list
    buckets = wl.distribute_workload(task_files_number, revit_files, get_file_size)
    try:
        # write out file lists
        counter = 0
        for bucket in buckets:
            file_name = os.path.join(
                task_list_directory, "Tasklist_" + str(counter) + ".txt"
            )
            status_write = write_revit_task_file(file_name, bucket, file_data_processor)
            return_value.update(status_write)
            counter += 1
        return_value.append_message("Finished writing out task files")
    except Exception as e:
        return_value.update_sep(False, "Failed to save file list! " + str(e))
    return return_value


def get_task_file_name(task_list_directory, counter):
    """
    Builds a fully qualified task file path.

    :param taskListDirectory: The fully qualified directory where the task file is (to be) located
    :type taskListDirectory: str
    :param counter: A counter to be added to the task file name
    :type counter: int

    :return: A fully qualified task file path
    :rtype: str
    """

    file_name = os.path.join(task_list_directory, "Tasklist_" + str(counter) + ".txt")
    return file_name


def write_empty_task_list(file_name):
    """
    Writes out an empty task list.

    :param fileName: Fully qualified file path of the task file name including extension.
    :type fileName: str

    :return:
        Result class instance.

        - Write file status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message property contains fully qualified file path to empty task list file.

        On exception:

        - .status (bool) will be False.
        - .message will contain the exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        f = open(file_name, "w")
        f.close()
        return_value.append_message(
            "wrote empty task list: {} [TRUE]".format(file_name)
        )
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write empty task list: {} with exception: {}".format(
                file_name, e
            ),
        )
    return return_value
