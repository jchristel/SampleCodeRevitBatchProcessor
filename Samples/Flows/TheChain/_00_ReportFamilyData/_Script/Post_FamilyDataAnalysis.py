"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains post reporting analysis utility functions:
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

# --------------------------
# Imports
# --------------------------
import os

import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.console_out import output
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.files_get import (
    get_files_with_filter,
    get_files_from_directory_walker_with_filters,
)
from duHast.Utilities.files_io import (
    copy_file,
    get_file_name_without_ext,
    file_exist,
)
from duHast.Utilities.files_tab import read_tab_separated_file
from duHast.Utilities.directory_io import create_directory, directory_exists
from duHast.Utilities.date_stamps import get_folder_date_stamp
from duHast.Utilities.files_combine import combine_files

from duHast.Revit.Family.Data.family_report_utils_deprecated import combine_reports


from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_family_base_processor,
)
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_family_base_report_name,
)

from duHast.Revit.Categories.Data.Objects.category_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_category_processor,
)
from duHast.Revit.Categories.Data.Objects.category_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_category_report_name,
)

from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_line_pattern_processor,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_line_pattern_report_name,
)

from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_shared_parameter_processor,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_shared_parameter_report_name,
)

from duHast.Revit.Warnings.Data.Objects.warnings_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_warnings_processor,
)
from duHast.Revit.Warnings.Data.Objects.warnings_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_warnings_report_name,
)

# -------------
# my code here:
# -------------

# list containing file name prefixes and the associated combined report file names
FILE_DATA_TO_COMBINE = [
    [
        data_type_category_processor,
        data_type_category_report_name + settings.REPORT_FILE_EXTENSION,
    ],
    [
        data_type_shared_parameter_processor,
        data_type_shared_parameter_report_name + settings.REPORT_FILE_EXTENSION,
    ],
    [
        data_type_line_pattern_processor,
        data_type_line_pattern_report_name + settings.REPORT_FILE_EXTENSION,
    ],
    [
        data_type_family_base_processor,
        data_type_family_base_report_name + settings.REPORT_FILE_EXTENSION,
    ],
    [
        data_type_warnings_processor,
        data_type_warnings_report_name + settings.REPORT_FILE_EXTENSION,
    ],
]


def setup_dated_directory_in_analysis():
    """
    Sets up a dated folder in the Analysis directory

    :return: True if folder was created successfully, otherwise False
    :rtype: bool
    """

    flag = create_directory(
        root=settings.ANALYSIS_FOLDER, folder_name=get_folder_date_stamp()
    )
    folder_name = os.path.join(settings.ANALYSIS_FOLDER, get_folder_date_stamp())
    return flag, folder_name


def copy_results_into_analysis(target_directory):
    """
    Copies all text files in Output folder to target folder

    :param target_directory: Fully qualified  directory path
    :type target_directory: str
    :return: true if all files copied successfully, otherwise False
    :rtype: bool
    """

    flag_copy = True
    # copy all text files from output
    files = get_files_with_filter(
        folder_path=settings.OUTPUT_FOLDER,
        file_extension=settings.REPORT_FILE_EXTENSION,
    )
    output("Found result files: {}".format(len(files)))
    for f in files:
        # get the file name of the path
        file_name = os.path.basename(f)
        # build the destination file path
        new_file_path = os.path.join(target_directory, file_name)
        # copy the log file
        flag_copy_file = copy_file(f, new_file_path)
        output(
            "Copied file: {} to: {} [{}]".format(
                get_file_name_without_ext(f), new_file_path, flag_copy_file
            )
        )
        flag_copy = flag_copy and flag_copy_file
    return flag_copy


# ------------------------------------------- clean up -------------------------------------------
def check_temp_reports_exist():
    """
    Check whether temp report folder exists (in case of an empty report run)

    :return: True if any temp report files exists, otherwise False.
    :rtype: bool
    """

    flag = False
    for to_combine in FILE_DATA_TO_COMBINE:
        files = get_files_from_directory_walker_with_filters(
            folder_path=settings.OUTPUT_FOLDER,
            file_prefix="",
            file_suffix=to_combine[0],
            file_extension=settings.REPORT_FILE_EXTENSION,
        )
        if len(files) > 0:
            flag = True
            break
    return flag


def combine_temp_reports():
    """
    Combines temporary report files into into single report files.
    """

    # combine all by file reports into one per processor
    for to_Combine in FILE_DATA_TO_COMBINE:
        output("Combining {} report files.".format(to_Combine[0]))
        # combine files
        combine_files(
            settings.OUTPUT_FOLDER,
            "",
            to_Combine[0],
            settings.REPORT_FILE_EXTENSION,
            to_Combine[1],
            get_files_from_directory_walker_with_filters,
        )


def write_empty_report_file(file_name, header=[]):
    """
    Writes an empty report file.

    :param fileName: The report file name excluding path.
    :type fileName: str
    :param header: header, defaults to []
    :type header: list, optional
    """

    output("{}: Writing empty report file.".format(file_name))
    data_to_file = []
    write_report_data_as_csv(
        os.path.join(settings.OUTPUT_FOLDER, file_name),  # report full file name
        header,  # empty header by default
        data_to_file,
    )


# -------------------------------------------combining report files -------------------------------------------


def combine_report_files_check():
    """
    Check whether a marker file exists, which specifies: where existing report file are located to be used to be merged with current report.

    :return: True if marker file exists, otherwise False.  The root directory path to where previous report files are located
    :rtype: bool, string, string
    """

    combine_reports_flag = False
    previous_reports_directory = ""

    # build marker file path
    marker_file_path = os.path.join(
        settings.INPUT_DIRECTORY, settings.FILE_NAME_MARKER_MERGE_FAMILY_DATA
    )
    # check if file exists in input location
    if file_exist(marker_file_path):
        # read file
        rows = read_tab_separated_file(marker_file_path)
        # should be at least one row...
        if len(rows) >= 1:
            for row in rows:
                if len(row) >= 1:
                    # assign family out file path
                    if directory_exists(row[0]):
                        previous_reports_directory = row[0]
                        combine_reports_flag = True
                # get out after parsing first row
                break
    return combine_reports_flag, previous_reports_directory


def combine_current_with_previous_report_files(previous_report_root_directory):
    """
    Loops over reports listed in global variable and attempts to find a match for the report in the current output directory\
        and the past in directory.
    It will combine both reports as follows:

        - duplicate family data: data from the current data set will be used
        - any unique data from either report will be added to the combined report

    :param previous_report_root_directory: Directory path containing previous (older) reports.
    :type previous_report_root_directory: str
    """

    # loop over report names and find matches in both location
    for to_combine in FILE_DATA_TO_COMBINE:
        # set default values
        current_report_file = ""
        previous_report_file = ""
        if file_exist(os.path.join(settings.OUTPUT_FOLDER, to_combine[1])):
            current_report_file = os.path.join(settings.OUTPUT_FOLDER, to_combine[1])
            output(
                "Found match for current report file: {}".format(current_report_file)
            )
        else:
            output(
                "No match found for: {} current output folder.".format(to_combine[1])
            )

        if file_exist(os.path.join(previous_report_root_directory, to_combine[1])):
            previous_report_file = os.path.join(
                previous_report_root_directory, to_combine[1]
            )
            output(
                "Found match for previous report file: {}".format(previous_report_file)
            )
        else:
            output(
                "No match found for: {} previous report folder.".format(to_combine[1])
            )

        if current_report_file != "" and previous_report_file != "":
            # put try catch around this in case report files are empty...
            try:
                # update report
                updated_report_rows_status = combine_reports(
                    previous_report_file, current_report_file
                )
                output(updated_report_rows_status.message)
                updated_report_rows = updated_report_rows_status.result
                # write out new report on top of old one
                write_report_data_as_csv(current_report_file, "", updated_report_rows)
                output("Wrote updated report to: {}".format(current_report_file))
            except Exception as e:
                output(
                    "Failed to combine reports: [{}]\t[{}] with exception: {}".format(
                        current_report_file, previous_report_file, e
                    )
                )
        else:
            output(
                "Failed to find two report files for report: {} Nothing was combined.".format(
                    to_combine[1]
                )
            )
