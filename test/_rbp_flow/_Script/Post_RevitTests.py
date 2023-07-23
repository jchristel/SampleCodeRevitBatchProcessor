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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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