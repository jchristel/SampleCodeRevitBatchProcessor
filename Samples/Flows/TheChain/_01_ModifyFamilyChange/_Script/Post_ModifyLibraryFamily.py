"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a post - processing module combining temp files, cleaning up temp files, moving 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Combining temp files:
    - marker files helping to copy family files back to their origin
    - changed family marker files to be used in reload action

- Moving family files back to their origin location.

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

# this sample processes log files and displays results indicating whether any revit files failed to process with a
# time out warning
# exception which caused the process to be aborted


# --------------------------
# default file path locations
# --------------------------

import os
import sys

import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.console_out import output
from duHast.Utilities.files_io import file_delete, get_file_name_without_ext, copy_file
from duHast.Utilities.files_get import get_files_with_filter
from duHast.Utilities.files_combine import combine_files
from duHast.Utilities.files_csv import write_report_data_as_csv, read_csv_file
from duHast.Utilities.batch_processor_log_utils import process_log_files
# -------------
# my code here:
# -------------

# temp files to combine
FILE_DATA_TO_COMBINE = [
    ["_marker_", "CopyFilesTaskList" + settings.REPORT_FILE_EXTENSION],
    ["_changed_", "ChangedFilesTaskList" + settings.REPORT_FILE_EXTENSION],
]


def delete_files(directory, file_extension, filter="*", keep_files=[]):
    """
    Deletes all files in a given directory with a given file extension.

    :param directory: Fully qualified directory path.
    :type directory: str

    :param file_extension: File extension to filter for.
    :type file_extension: str

    :param filter: Filter to apply to file names.
    :type filter: str

    :param keep_files: List of files not to delete (fully qualified file path)
    :type keep_files: [str]

    :return: True if all files where deleted or none existed in the first place, otherwise False
    :rtype: bool
    """

    flag_over_all = True
    task_list_files = get_files_with_filter(directory, file_extension, filter)
    output("Looking for files in: {}".format(directory))
    if len(task_list_files) > 0:
        for f in task_list_files:
            if f not in keep_files:
                flag = file_delete(f)
                output(
                    "Deleted file: {} status: [{}]".format(
                        get_file_name_without_ext(f), flag
                    )
                )
                flag_over_all = flag_over_all and flag
    else:
        output("No files found to be deleted.")
    return flag_over_all


def delete_temp_files(keep_files):
    """
    Deletes all temp file.

    :param keep_files: List of files not to delete (fully qualified file path)
    :type keep_files: [str]

    :return: True if all files got deleted successfully, otherwise False.
    :rtype: bool
    """

    flag_deleted_all = True
    for to_delete in FILE_DATA_TO_COMBINE:
        flag_delete = delete_files(
            settings.WORKING_DIRECTORY, ".temp", "*" + to_delete[0], keep_files
        )
        flag_deleted_all = flag_deleted_all & flag_delete
    return flag_deleted_all


def combine_data_files():
    """
    Combines varies report files into single text file.

    Files are filter based on FILE_DATA_TO_COMBINE list.
    """

    for to_combine in FILE_DATA_TO_COMBINE:
        output("Combining {}  report files.".format(to_combine[0]))
        # combine files
        combine_files(
            settings.WORKING_DIRECTORY, "", to_combine[0], ".temp", to_combine[1]
        )


def move_files():
    """
    Move family files back to original location.
    This is a work around to the fact that I'm unable to save family files after processing!
    """

    file_copy_task_list = read_csv_file(
        os.path.join(settings.WORKING_DIRECTORY, FILE_DATA_TO_COMBINE[0][1])
    )

    row_counter = 0
    for copy_row in file_copy_task_list:
        if row_counter != 0:
            flag_copy = copy_file(copy_row[0], copy_row[1])
            output("Copied file: {} status: [{}]".format(copy_row[0], flag_copy))
            if flag_copy:
                flag_delete = file_delete(copy_row[0])
                output("Deleted file: {} status: [{}]".format(copy_row[0], flag_delete))
        row_counter = row_counter + 1


def create_follow_up_report_data_file():
    """
    writes out changed file list in format for follow up reporting

    :return: true if successfully written list to file, otherwise False
    :rtype: bool
    """
    rows = read_csv_file(
        os.path.join(settings.WORKING_DIRECTORY, FILE_DATA_TO_COMBINE[1][1])
    )
    data_file = []
    for r in rows:
        data = r[1]
        data_file.append(data)

    # write out file list without header
    header = []

    try:
        # write data
        write_report_data_as_csv(
            os.path.join(
                settings.WORKING_DIRECTORY, settings.FOLLOW_UP_REPORT_FILE_NAME
            ),
            header,
            data_file,
        )
        return True
    except Exception:
        return False


# -------------
# main:
# -------------

# combine marker files (copy instructions)
output("Combining report files:")
combine_data_files()

# delete marker files
flag_delete_all = delete_temp_files([])
output("Deleted all temp files: [{}]".format(flag_delete_all))

# move family files back to source location
move_files()

# delete move task file
flag_delete_move_task = file_delete(
    os.path.join(settings.WORKING_DIRECTORY, FILE_DATA_TO_COMBINE[0][1])
)
output("Deleted move families task file: [{}]".format(flag_delete_move_task))

# delete any task list files
flag_delete_move_task = delete_files(
    settings.PREDEFINED_TASK_FILE_DIRECTORY, settings.PREDEFINED_TASK_FILE_EXTENSION
)
output("Deleted families task file: [{}]".format(flag_delete_move_task))

# delete any files in the \_Input directory
flag_delete_files_in_input = delete_files(
    settings.INPUT_DIRECTORY, settings.REPORT_FILE_EXTENSION
)
output("Deleted file in _Input directory: [{}]".format(flag_delete_files_in_input))

# create follow up list file
flag_follow_up = create_follow_up_report_data_file()
if flag_follow_up:
    output(
        "Created follow up list file: [{}]".format(
            os.path.join(
                settings.WORKING_DIRECTORY, settings.FOLLOW_UP_REPORT_FILE_NAME
            )
        )
    )
else:
    output(
        "Failed to created follow up list file: [{}]".format(
            os.path.join(
                settings.WORKING_DIRECTORY, settings.FOLLOW_UP_REPORT_FILE_NAME
            )
        )
    )

processing_results = process_log_files(settings.LOG_MARKER_DIRECTORY)
output("LogResults.... status: [{}]".format(processing_results.status))
output("LogResults.... message: {}".format(processing_results.message))
