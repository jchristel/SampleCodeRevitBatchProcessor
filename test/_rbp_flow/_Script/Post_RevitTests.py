"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing post processing script which runs outside the revit batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- runs at the very end of the flow
- processes log files ( did any exception occur?)
- deletes marker files

    - log marker files
    - revit work sharing monitor marker files
    
"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

# --------------------------
# Imports
# --------------------------

import sys
import settings as settings  # sets up all commonly used variables and path locations!

# import log utils
from duHast.Utilities import batch_processor_log_utils as logUtils
from duHast.Utilities import worksharing_monitor_process as wsmp
from duHast.Utilities.console_out import output_with_time_stamp as output
from duHast.Utilities.files_get import (
    get_files_from_directory_walker_with_filters_simple,
)
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.utility import parse_string_to_bool


# -------------
# my code:
# -------------


def check_failed_tests(rows):
    """
    Checks whether any row from log files contains a false as test result. 

    Note: Field with index 1 contains test result as boolean ( in string format)

    :param rows: Rows from a log file
    :type rows: [[str]]
    :return: True if all tests past, otherwise False
    :rtype: Boolean
    """
    for row in rows:
        if parse_string_to_bool(row[1]) == False:
            return False
    return True


def read_revit_test_log_files(log_files):
    """
    Checks all revit test log files in /Output directory for failed tests.

    :param log_files: Directory containing revit test log files
    :type log_files: str
    :return: True if all tests recorded in log files past, otherwise False
    :rtype: bool
    """
    overall_results = True
    for log_file in log_files:
        rows = read_csv_file(log_file)
        log_result = check_failed_tests(rows=rows)
        output("{}: [{}]".format(log_file, log_result))
        overall_results = overall_results & log_result
    return overall_results


# -------------
# main:
# -------------


PROCESSING_RESULTS = logUtils.process_log_files(settings.LOG_MARKER_DIRECTORY)
output("Log results.... message(s): \n[{}]".format(PROCESSING_RESULTS.status))
output(PROCESSING_RESULTS.message)
# remove old log marker files
flag_delete_log_markers = logUtils.delete_log_data_files(settings.LOG_MARKER_DIRECTORY)
output("Log marker deletion.: [{}]".format(flag_delete_log_markers))

# WSMP marker files clean up
cleanUpWSMFiles_ = wsmp.clean_up_wsm_data_files(settings.WSM_MARKER_DIRECTORY)
output(
    "WSM files clean up.... status: [{}]\nWSM files clean up.... message: \n\t{}".format(
        cleanUpWSMFiles_.status, cleanUpWSMFiles_.message
    )
)

# read logs and check for any False flags indicating a failed test
# get log files
revit_test_log_files = get_files_from_directory_walker_with_filters_simple(
    settings.OUTPUT_FOLDER, ".csv"
)
did_all_revit_test_pass = read_revit_test_log_files(revit_test_log_files)

# pass the results back to the calling powershell script
if (did_all_revit_test_pass):
    sys.exit(0)
else:
    sys.exit(1)