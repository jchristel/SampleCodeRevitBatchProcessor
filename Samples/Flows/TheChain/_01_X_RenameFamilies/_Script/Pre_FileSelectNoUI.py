"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a pre - processing module creating task files for revit batch processor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module generates batch processor task files by :

- Combining any number of task files.

    - comma separated text files
    - file extension .task 
    - first colum contains the fully qualified file path to a Revit family file which requires processing
    - no header row

or if no pre defined list is provided:

-   generates batch processor task files including all Revit family files in a given library directory and its sub directories.

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

# --------------------------
# default file path locations
# --------------------------
# directory containing families to be processed
PROCESS_PATH = ""

import sys, os

import settings as settings  # sets up all commonly used variables and path locations!

# import file list module
from duHast.UI.file_list import (
    write_file_list,
    get_file_size,
    write_revit_task_file,
    bucket_to_task_list_file_system,
    get_revit_files_incl_sub_dirs,
)
from duHast.UI.workloader import distribute_workload
from duHast.UI.Objects.file_item import MyFileItem
from duHast.Utilities.console_out import output
from duHast.Utilities.files_io import file_exist
from duHast.Utilities.files_get import get_files_with_filter
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.Objects.result import Result


# -------------
# my code here:
# -------------


def get_task_list_files(directory_path):
    """
    Get any pre defined task files containing the path to a subset of families in the library. This is done as to not having to process all\
        families in the library for the task at hand.

    :return: List of file path
    :rtype: list of str
    """

    task_list_files = get_files_with_filter(
        directory_path, settings.PREDEFINED_TASK_FILE_EXTENSION
    )
    return task_list_files


def combine_task_list_files(files):
    """
    Reads the content of each pre defined task file.
    Expected format is : csv separated text file where first column is a file path to a revit family.

    :param files: List of predefined task files
    :type files: [str]
    :return: List of file items
    :rtype: [:class:`.FileItem`]
    """

    revit_files = []
    for task_file_path in files:
        rows = read_csv_file(task_file_path)
        for row in rows:
            # make sure row contains at least one column (hopefully containing a file path)
            if len(row) >= 1:
                # does the file still exists?
                if file_exist(row[0]):
                    size = os.path.getsize(row[0])
                    my_file_item = MyFileItem(row[0], size)
                    # make sure list is of unique files
                    if my_file_item not in revit_files:
                        revit_files.append(my_file_item)
    return revit_files


# -------------
# main:
# -------------

result_ = Result()
output("Python pre process script Generate Task list ...")
# check if a folder path was past in...otherwise check  for a task list file ... if neither go with default
if len(sys.argv) == 2:
    PROCESS_PATH = sys.argv[1]
    output("Collecting files from past in path: {}".format(PROCESS_PATH))
elif len(get_task_list_files(settings.PREDEFINED_TASK_FILE_DIRECTORY)) > 0:
    # check if any task files are present
    PROCESS_PATH = settings.PREDEFINED_TASK_FILE_DIRECTORY
    output("Collecting files from task list located: {}".format(PROCESS_PATH))
else:
    PROCESS_PATH = settings.REVIT_LIBRARY_PATH
    output("Using default library directory path: {}".format(PROCESS_PATH))

# check whether folder contains any task files
# if not process files in entire library
task_list_files = get_task_list_files(PROCESS_PATH)
if len(task_list_files) > 0:
    output("Found overall task files: {}".format(len(task_list_files)))
    revit_files = combine_task_list_files(task_list_files)

    # build bucket list
    buckets = distribute_workload(settings.TASK_FILE_NO, revit_files, get_file_size)

    # write out file lists
    counter = 0
    for bucket in buckets:
        file_name = os.path.join(
            settings.TASK_FILE_DIRECTORY, "Tasklist_{}.txt".format(counter)
        )
        status_write = write_revit_task_file(
            file_name, bucket, bucket_to_task_list_file_system
        )
        result_.update(status_write)
        output(status_write.message)
        counter += 1
    output("Finished writing out task files")
else:
    output("No task files found, using directory instead:")
    output("Collecting files from: {}".format(settings.REVIT_LIBRARY_PATH))
    # get file data
    output("Writing file Data.... start")
    result_ = write_file_list(
        settings.REVIT_LIBRARY_PATH,
        settings.FILE_EXTENSION_OF_FILES_TO_PROCESS,
        settings.TASK_FILE_DIRECTORY,
        settings.TASK_FILE_NO,
        get_revit_files_incl_sub_dirs,
    )
    output(result_.message)
    output("Writing file Data.... status: [{}]".format(result_.status))
if result_.status:
    sys.exit(0)
else:
    output(result_.message)
    sys.exit(2)
