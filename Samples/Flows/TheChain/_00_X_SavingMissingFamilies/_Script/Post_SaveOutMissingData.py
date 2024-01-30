"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains post saving out missing families functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Write all path of families saved out into a file used in a follow up report flow.
- Copy report files and log files into analysis folders.
- Check log files for:

    - any exceptions which may have occured during processing


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
import clr
import System
import os
import sys


import settings as settings  # sets up all commonly used variables and path locations!
from utility import save_out_missing_families_check

from duHast.Utilities.console_out import output
from duHast.Utilities.batch_processor_log_utils import process_log_files
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.files_io import file_delete
from duHast.Utilities.files_get import get_files_single_directory
from duHast.UI.file_list import get_revit_files


# import common library
import Utility as util

# -------------
# my code here:
# -------------

# ------------------------------------------- user feed back and report to disk -------------------------------------------


def _UserOutAndLogFile(processing_results, file_name, header=[]):
    """
    Show user feed back and write to report file

    :param processingResults: Result class instance.

        - result.status. bool. (not used)
        - result.message string (not used)
        - result.result A list of lists of string containing the data to be written to file.

    :type processingResults: class:`.Result`
    """

    if processing_results.result != None:
        # show user any issues
        for m in processing_results.result:
            output("::".join(m))
        # write data out to file
        write_report_data_as_csv(
            os.path.join(settings.OUTPUT_FOLDER ,file_name),  # report full file name
            header,  # empty header
            processing_results.result,
            writeType="w",
        )
    else:
        output("Result did not contain any data to be written to file.")


# ------------------------------------------- clean up -------------------------------------------


def delete_file_in_input_dir():
    """
    Deletes any files in the input directory.
    """
    files = get_files_single_directory(
        settings.INPUT_DIRECTORY, "", "", settings.REPORT_FILE_EXTENSION
    )
    if len(files) > 0:
        for f in files:
            flag_delete = file_delete(f)
            output("Deleted marker file: {} [{}]".format(f, flag_delete))
    else:
        output("Input directory did not contain any files.")


# ------------------------------------------- log file processing -------------------------------------------


def process_log_files():
    """
    Checks log files for any warnings or exceptions and writes out a report file containing any issues in format\
        filepath exception description
    """

    # process logs
    processing_results_ = process_log_files(
        settings.LOG_MARKER_DIRECTORY,
    )

    output("LogResults.... status: {}".format(processing_results_.status))

    # write any files with exceptions out to file:
    if processing_results_.result != None:
        # re-format output data
        data_to_file = []
        for data in processing_results_.result:
            row = [data[0], data[2]]
            data_to_file.append(row)
        processing_results_.result = data_to_file
        _UserOutAndLogFile(processing_results_, settings.FILE_NAME_EXCEPTIONS_REPORT)


# -------------
# main:
# -------------

# check log files for any exceptions or warnings
process_log_files()

# get the folder in which families have been saved to:
(
    save_out_missing_families,
    base_data_report_file_path,
    family_out_root_directory,
) = save_out_missing_families_check()

# collect data and write to processing file
if save_out_missing_families:
    # get all families located in combined out folder
    files = get_revit_files(
        settings.OUTPUT_FOLDER_COMBINED_FAMILIES, ".rfa"
    )

    if len(files) > 0:
        # needs to be a list of lists
        data = []
        # get data from file items
        for fileObject in files:
            # append as a list
            data.append([fileObject.name])

        # write data to file
        write_report_data_as_csv(
            os.path.join(
                settings.OUTPUT_FOLDER,
                settings.FILE_NAME_SECOND_PROCESS_FAMILIES_REPORT,
            ),  # report full file name
            [],  # empty header by default
            data,
        )
    else:
        output("No families located in output folder!")
else:
    output("Failed to read data required to analyse missing families!")

# clean up
delete_file_in_input_dir()
