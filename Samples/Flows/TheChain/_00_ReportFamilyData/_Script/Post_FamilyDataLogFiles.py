"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains post reporting functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- check if anything was reported: do any temp files exists?
- if so:
    - Combine temp report files per family into single report file per report type.
    - Delete temp folders
    - Copy report files and log files into analysis folders.
    - Check Family base data report file for:

        - missing families 
        - host families which contain missing families
        - circular references in family nesting

    - Check log files for:

        - any exceptions which may have occured during processing
- if not:
    - dont do anything...


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
# Imports
# --------------------------
import os

import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.console_out import output

# import common library
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.files_io import copy_file
from duHast.Utilities.directory_io import directory_exists
from duHast.Utilities.utility import pad_single_digit_numeric_string
from duHast.Utilities.batch_processor_log_utils import (
    get_current_session_ids,
    get_log_files,
)


# -------------
# my code here:
# -------------

# list containing file name prefixes and the associated combined report file names
FILE_DATA_TO_COMBINE = [
    ["Category", "FamilyCategoriesCombinedReport" + settings.REPORT_FILE_EXTENSION],
    [
        "SharedParameter",
        "FamilySharedParametersCombinedReport" + settings.REPORT_FILE_EXTENSION,
    ],
    [
        "LinePattern",
        "FamilyLinePatternsCombinedReport" + settings.REPORT_FILE_EXTENSION,
    ],
    ["FamilyBase", "FamilyBaseDataCombinedReport" + settings.REPORT_FILE_EXTENSION],
    ["Warnings", "FamilyWarningsCombinedReport" + settings.REPORT_FILE_EXTENSION],
]

# looking for message indicating one of the data processors failed
CUSTOM_EXCEPTION_MESSAGES_TO_BE_FLAGGED = ["status: False"]


# ------------------------------------------- log file processing -------------------------------------------


def write_out_re_process_data(data, file_name, header=[]):
    """
    Writes out a CSV file which can be used to re-process families which did not process correctly the first time around.

    :param data: _description_
    :type data: [[str]]
    :param file_name: The file name.
    :type file_name: str
    :param header: header row, defaults to []
    :type header: [str]
    """

    if len(data) > 0:
        # show user any issues
        for d in data:
            output("::".join(d))
        # write data out to file
        write_report_data_as_csv(
            file_name=os.path.join(
                settings.OUTPUT_FOLDER, file_name
            ),  # report full file name
            header=header,  # empty header by default
            data=data,
        )
    else:
        output(
            "{}: Result did not contain any data to be written to file.".format(
                file_name
            )
        )
        # write out empty re-process file
        write_report_data_as_csv(
            file_name=settings.OUTPUT_FOLDER + "\\" + file_name,
            header=header,
            data=[],
        )
        output("{}: Empty file written.".format(file_name))


# ------------------------------------------- copy log files -------------------------------------------


def copy_log_worker(log_files, target_directory, extension):
    """
    Copies log files and renames them

    :param logfiles: A list of fully qualified log file path.
    :type logfiles: [str]
    :param targetFolder: The destionation directory to where files will be copied to.
    :type targetFolder: str
    :param extension: File extension in format: '.extension'
    :type extension: str
    """

    flag = True
    # copy log files over
    log_counter = 1
    for log_file_path in log_files:
        # get the file name of the path
        log_file_name = (
            "BatchRvt_" + pad_single_digit_numeric_string(str(log_counter)) + extension
        )
        # build the destination file path
        new_log_file_path = os.path.join(target_directory, log_file_name)
        # copy the log file
        flag_copy = copy_file(old_name=log_file_path, new_name=new_log_file_path)
        flag = flag and flag_copy
        log_counter = log_counter + 1
    return flag


def copy_log_files_to_marker_dir(target_directory):
    """
    Copies log files (.log and .txt) from local app data folder to provided folder and renames them:\
        'BatchRvt_' + counter
    """

    flag_copy_logs = True
    if directory_exists(settings.LOG_MARKER_DIRECTORY):
        if directory_exists(target_directory):
            # get log marker files
            marker_file_ids = get_current_session_ids(
                folder_path=settings.LOG_MARKER_DIRECTORY,
                delete_marker_files=False,  # keep markers for processing later on
            )
            # check if any ids where retrieved
            if len(marker_file_ids) > 0:
                # copy .log files
                log_files = get_log_files(marker_file_ids)
                copy_log = copy_log_worker(log_files, target_directory, ".log")
                # copy .txt files
                log_files = get_log_files(
                    list_of_session_ids=marker_file_ids, file_extension=".txt"
                )
                copy_text_log = copy_log_worker(log_files, target_directory, ".txt")
                # combine copy results
                flag_copy_logs = copy_log and copy_text_log
            else:
                output(
                    "\nNo log marker files found in: {}".format(
                        settings.LOG_MARKER_DIRECTORY
                    )
                )
                flag_copy_logs = False
        else:
            output(
                "\nLog file destination directory does not exist: {}".format(
                    target_directory
                )
            )
            flag_copy_logs = False
    else:
        output(
            "\nLog marker directory does not exist: {}".format(
                settings.LOG_MARKER_DIRECTORY
            )
        )
        flag_copy_logs = False
    return flag_copy_logs
