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
import clr
import System
import os
import sys


import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.console_out import output  # output to console function
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.batch_processor_log_utils import process_log_files

import Post_FamilyDataCleanUp as pCleanUp  # clean up functions
from Post_FamilyDataLogFiles import (
    write_out_re_process_data,
    copy_log_files_to_marker_dir,
)
from Post_FamilyDataAnalysis import (
    setup_dated_directory_in_analysis,
    check_temp_reports_exist,
    combine_temp_reports,
    copy_results_into_analysis,
    write_empty_report_file,
    combine_report_files_check,
    combine_current_with_previous_report_files,
)

# import common library
from duHast.Revit.Family.Data.family_base_data_circular_referencing import (
    check_families_have_circular_references,
)
from duHast.Revit.Family.Data.family_base_data_missing_families import (
    check_families_missing_from_library,
    find_missing_families_direct_host_families,
)

# -------------
# my code here:
# -------------


# looking for message indicating one of the data processors failed
CUSTOM_EXCEPTION_MESSAGES_TO_BE_FLAGGED = ["status: False"]


# ------------------------------------------- user feed back and report to disk -------------------------------------------


def user_out_and_log_file(processing_results, file_name, header=[]):
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
            file_name=os.path.join(
                settings.OUTPUT_FOLDER, file_name
            ),  # report full file name
            header=header,  # empty header
            data=processing_results.result,
        )
    else:
        output(
            "{}: Result did not contain any data to be written to file.".format(
                file_name
            )
        )
        write_empty_report_file(file_name, header)

# -------------------------------------------- log files --------------------------------------------

def process_all_log_files():
    """
    Checks log files for any warnings or exceptions and writes out a report file containing any issues in format\
        filepath exception description
    """

    # process logs
    processing_results = process_log_files(
        folder_path=settings.LOG_MARKER_DIRECTORY,
        debug=CUSTOM_EXCEPTION_MESSAGES_TO_BE_FLAGGED,
    )

    output("LogResults.... status: {}".format(processing_results.status))

    # write any files with exceptions out to file:
    if processing_results.result != None:
        # re-format output data
        data_to_file = []
        data_to_process_file = []
        for data in processing_results.result:
            row = [data[0], data[2]]
            data_to_file.append(row)
            # re - process files
            rowProcessData = [data[0]]
            data_to_process_file.append(rowProcessData)
        processing_results.result = data_to_file
        output("LogResults.... message(s): \n[{}]".format(processing_results.result))
        user_out_and_log_file(processing_results, settings.FILE_NAME_EXCEPTIONS_REPORT)

        # write out second family list as CSV (files which failed to process for a reason and need to be processed again)
        write_out_re_process_data(
            data=data_to_process_file,
            file_name=settings.FILE_NAME_SECOND_PROCESS_FAMILIES_REPORT,
        )

# ------------------------------------------- Report analysis -------------------------------------------


def check_circular_references():
    """
    Checks for any circular nesting references in family files processed by analyzing the \
        FamilyBaseDataCombinedReport.csv report file.
    """
    try:
        # check for circular references in families
        check_circular_ref_result = check_families_have_circular_references(
            os.path.join(
                settings.OUTPUT_FOLDER,
                "FamilyBaseDataCombinedReport" + settings.REPORT_FILE_EXTENSION,
            )
        )

        output(
            "Circular referencing check.... status: {}".format(
                check_circular_ref_result.status
            )
        )
        if check_circular_ref_result.result != None:
            # re-format output data
            data_to_file = []
            for data in check_circular_ref_result.result:
                row = [
                    data.filePath,
                    "[" + ",".join(data.parent) + "]",
                    "[" + ",".join(data.child) + "]",
                ]
                data_to_file.append(row)
            check_circular_ref_result.result = data_to_file
        user_out_and_log_file(
            check_circular_ref_result, settings.FILE_NAME_CIRCULAR_REFERENCE_REPORT
        )
    except Exception as e:
        output("Failed circular reference check with exception: {}".format(e))
        write_empty_report_file(settings.FILE_NAME_CIRCULAR_REFERENCE_REPORT)


def check_missing_families():
    """
    Checks for nested families which are not processed as root families and therefore are not in the library or missing.
    Uses the FamilyBaseDataCombinedReport.csv report file
    """

    data_file_path = os.path.join(
        settings.OUTPUT_FOLDER,
        "FamilyBaseDataCombinedReport" + settings.REPORT_FILE_EXTENSION,
    )

    try:
        check_missing_families = check_families_missing_from_library(data_file_path)

        output(
            "Missing families from library check.... status: {}".format(
                check_missing_families.status
            )
        )
        # provide more feedback as to what went wrong
        if(check_missing_families.status == False):
            output("Missing families from library check.... message: {}".format(
                check_missing_families.message
            ))
        # initialise missing families list
        missing_families = []
        if len(check_missing_families.result) > 0:
            # duplicate data for later (to find the host families)
            missing_families = list(check_missing_families.result)

            # re-format output data for missing family text file
            data_to_file = []
            for data in check_missing_families.result:
                try:
                    # missing fams data
                    row = [data.name, data.category]
                    data_to_file.append(row)
                except Exception as e:
                    output(
                        "an exception occurred when processing missing family data prior to be written to file: {}".format(
                            e
                        )
                    )
            check_missing_families.result = data_to_file
            user_out_and_log_file(
                check_missing_families, settings.FILE_NAME_MISSING_FAMILIES_REPORT
            )
        else:
            # write empty report files
            data_to_file = []
            write_out_re_process_data(
                data_to_file, settings.FILE_NAME_MISSING_FAMILIES_REPORT
            )

        # get host families of those missing families
        missing_families_host_families = find_missing_families_direct_host_families(
            data_file_path, missing_families
        )

        output(
            "Missing families hosts .... status: {}".format(
                missing_families_host_families.status
            )
        )
        # provide more feedback as to what went wrong
        if(missing_families_host_families.status == False):
            output("Missing families hosts.... message: {}".format(
                missing_families_host_families.message
            ))


        if len(missing_families_host_families.result) > 0:
            # re-format output data
            data_to_file = []
            for data in missing_families_host_families.result:
                try:
                    row = [data.filePath, data.name, data.category]
                    data_to_file.append(row)
                except Exception as e:
                    output(
                        "an exception occurred when processing missing family data prior to be written to file: {}".format(
                            e
                        )
                    )
            write_out_re_process_data(
                data_to_file, settings.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT
            )
        else:
            # write empty report files
            data_to_file = []
            write_out_re_process_data(
                data_to_file, settings.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT
            )
    except Exception as e:
        output("Failed missing family check with exception: {}".format(e))
        write_empty_report_file(settings.FILE_NAME_MISSING_FAMILIES_REPORT)
        write_empty_report_file(settings.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT)


# -------------
# main:
# -------------
try:
    # check whether any families where processed (possible that in follow up mode nothing was needed to be processed!)
    if check_temp_reports_exist():
        # set up a folder with the current date in the analysis folder to store some data
        (
            dated_analysis_folder_created_,
            dated_analysis_dated_directory_path_,
        ) = setup_dated_directory_in_analysis()
        # combine temporary, by family, reports
        combine_temp_reports()
        # delete the working by session id directories
        pCleanUp.delete_working_directories()

        # check whether report files need to be combined / merged with previous  (older) report files before progressing
        combine_report_files, previous_report_root_directory = combine_report_files_check()
        if combine_report_files:
            combine_current_with_previous_report_files(previous_report_root_directory)

        # check processed files for any circular references
        check_circular_references()
        # check processed files for any missing families
        check_missing_families()

        # copy log files first if data folder was created
        # log file markers will be removed once the log files are processed
        # therefore those log files need to be copied first
        if dated_analysis_folder_created_:
            flag_copy_log_one_ = copy_log_files_to_marker_dir(dated_analysis_dated_directory_path_)
            output(
                "Copied all log files to Analysis dated folder with status: {}".format(
                    flag_copy_log_one_
                )
            )
            flag_copy_log_two_ = copy_log_files_to_marker_dir(settings.ANALYSIS_CURRENT_FOLDER)
            output(
                "Copied all log files to Analysis current folder with status: {}".format(
                    flag_copy_log_two_
                )
            )

        # check log files for any exceptions or warnings ( do this last since log marker files are required to copy logs for \
        # analysis in powerBi)
        # this will also remove any log file marker files
        process_all_log_files()

        # copy report files
        if dated_analysis_folder_created_:
            flag_copy_result_one_ = copy_results_into_analysis(
                dated_analysis_dated_directory_path_
            )
            output(
                "Copied all report files to Analysis dated folder with status: {}".format(
                    flag_copy_result_one_
                )
            )
            flag_copy_result_two_ = copy_results_into_analysis(
                settings.ANALYSIS_CURRENT_FOLDER
            )
            output(
                "Copied all report files to Analysis current folder with status: {}".format(
                    flag_copy_result_two_
                )
            )
    else:
        output("No temp report files where found, indicating no families where processed.")
    # delete any files in Input directory
    pCleanUp.delete_file_in_input_directory()
except Exception as e:
    output("Failed post processing with exception: {}".format(e))
    sys.exit(1)
