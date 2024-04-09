"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing post processing script which runs outside the revit batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- runs at the very end of the flow in iron python 2.7 in context of the script directory on the network drive
- deletes 
    - log marker files
    - revit work sharing monitor marker files
    - temp files

    - copies log files
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


# import clr
# import System
import os

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output_with_time_stamp as output
from duHast.Utilities import batch_processor_log_utils as bpLogUtils
from duHast.Utilities.files_io import (
    copy_file,
    file_delete,
    get_file_name_without_ext,
)
from duHast.Revit.ModelHealth.Reporting import report_file_names as rFns
from duHast.Utilities.files_get import get_files_with_filter

# -------------
# my code here:
# -------------

def delete_temp_files(keep_files):
    """
    Deletes all temp files in the report out folder.

    :param keep_files: List of file (fully qualified file path) to keep.
    :type keep_files: []

    :return: True if all files where deleted successfully, otherwise false.
    :rtype: bool
    """

    flag_delete_all = True
    for file_name_filter in rFns.PARAM_ACTIONS_FILENAMES:
        files_matching = get_files_with_filter(
            settings.OUTPUT_FOLDER,
            settings.TEMP_FILE_NAME_EXTENSION,
            "*" + file_name_filter,
        )
        for file_matched in files_matching:
            if file_matched not in keep_files:
                flag_delete = file_delete(file_matched)
                output(
                    "Deleting: {} status: [{}]".format(
                        get_file_name_without_ext(file_matched), flag_delete
                    )
                )
                flag_delete_all = flag_delete_all & flag_delete
    return flag_delete_all


def copy_log_files():
    """
    Copies log files from local app data folder to provided folder.

    :return: True if copy successful, otherwise False
    :rtype: bool
    """

    flag_copy_logs = True
    if os.path.exists(settings.LOG_MARKER_DIRECTORY):
        if os.path.exists(settings.LOGFILE_COPY_TO_DIRECTORY):
            # get log marker files
            marker_file_ids = bpLogUtils.get_current_session_ids(
                settings.LOG_MARKER_DIRECTORY
            )
            # check if any ids where retrieved
            if len(marker_file_ids) > 0:
                # find log files matching markers
                log_files = bpLogUtils.get_log_files(marker_file_ids)
                # copy log files over
                for log_file_path in log_files:
                    # get the file name of the path
                    log_file_name = os.path.basename(log_file_path)
                    # build the destination file path
                    new_log_file_path = os.path.join(
                        settings.LOGFILE_COPY_TO_DIRECTORY, log_file_name
                    )
                    # copy the log file
                    copy_file(log_file_path, new_log_file_path)
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
                    settings.LOGFILE_COPY_TO_DIRECTORY
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


# execute clean up
try:
    flag_delete_all_ = delete_temp_files([])
    output("Deleted all temp files: [{}]".format(flag_delete_all_))
except Exception as e:
    output("Failed to delete temp files: [{}]".format(e))

try:
    copy_logs_ = copy_log_files()
    output("Copied log files: [{}]".format(copy_logs_))
except Exception as e:
    output("Failed to copy log files: [{}]".format(e))
