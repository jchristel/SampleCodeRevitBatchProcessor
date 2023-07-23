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
# Copyright (c) 2021  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

# this sample shows how to write out a number of task files using bucket distribution by file size

import clr
import System
import os


# import file item class
from duHast.UI import file_item as fi

# import workloader utils
from duHast.UI import workloader as wl

# custom result class
from duHast.Utilities.Objects import result as res

# -------------
# my code here:
# -------------


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
    list_of_files = os.listdir(directory)
    for f in list_of_files:
        # check for file extension match
        if f.lower().endswith(file_extension.lower()):
            # check if this is a back up file
            if is_back_up_file(f) == False:
                # Use join to get full file path.
                location = os.path.join(directory, f)
                # Get size and add to list of files.
                size = os.path.getsize(location)
                files.append(fi.MyFileItem(location, size))
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
    list_of_files = list()
    for (dirpath, dirnames, filenames) in os.walk(directory):
        list_of_files += [os.path.join(dirpath, file) for file in filenames]
    for f in list_of_files:
        # check for file extension match
        if f.lower().endswith(file_extension.lower()):
            # check if this is a back up file,
            if is_back_up_file(f) == False:
                # Get size and add to list of files.
                size = os.path.getsize(f)
                files.append(fi.MyFileItem(f, size))
    return files


def is_back_up_file(file_path):
    """
    Checks whether a file is a Revit back up file.

    Backup files are usually in format 'filename.01234.ext'

    Method of checking:

    - splitting file name at every full stop
    - check whether a list with more more then 2 entries came back ?

        - no:
            - not a back up
        - yes:
            - check last list entry whether it is 4 characters in length and can it be convert it into an integer?

                - yes:
                    - backup file
                - no
                    - normal file

    :param file_path: A fully qualified file path.
    :type file_path: str

    :return: True if a back up file, otherwise False.
    :rtype: bool
    """

    is_backup = False
    chunks = file_path.split(".")
    if len(chunks) > 2:
        last_chunk = chunks[len(chunks) - 2]
        try:
            converted_num = int(last_chunk)
            is_backup = True
        except Exception:
            pass
    return is_backup


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
