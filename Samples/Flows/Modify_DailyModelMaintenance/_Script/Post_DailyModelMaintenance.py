"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing post processing script which runs outside the revit batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- runs at the very end of the flow
- processes log files ( did any exception occur?)
- deletes marker files

    - log marker files
    - revit work sharing monitor marker files

- combines report files per type and revit file into single files per type
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
import sys  # required to return an exit code
import os

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output_with_time_stamp as output
from duHast.Utilities.files_io import (
    file_exist,
    get_file_name_without_ext,
)
from duHast.Utilities.files_combine import (
    combine_files,
    combine_files_csv_header_independent,
    append_to_file,
    combine_files_json,
)

from duHast.Utilities.files_get import get_files_with_filter, get_files_single_directory
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.date_stamps import FILE_DATE_STAMP_YYYY_MM_DD
from duHast.Revit.ModelHealth.Reporting import report_file_names as rFns
from utils.view_templates import (
    combine_vt_reports,
    convert_vt_reports_to_parquet,
    delete_hash_table_vt_json_reports,
)


# -------------
# my code here:
# -------------


def get_file_name_from_temp(file_name, filter):
    """
    Returns the original file name extracted from report temp file name.

    sample:

    21_08_29NHR-BVN-MOD-ARC-EBL-00M-NL00001 - EASTBLOCK_FileSize

    :param file_name: file name without path and extension
    :type file_name: str
    :param filter: file name ends on: filter ?
    :type filter: str

    :return: file name without date stemp and filter value
    :rtype: str
    """

    overall_length = len(file_name)
    date_length = len(FILE_DATE_STAMP_YYYY_MM_DD)
    filter_length = len(filter)
    return file_name[date_length : overall_length - filter_length]


def merge_files():
    """
    Appends temp report files to log files. Returns a list of files where that log file did not exist or which failed to append to data log file

    :return: List of files
    :rtype: [str]
    """

    # create overall log file
    log_file_name = (
        settings.LOG_FILE_NAME_PREFIX
        + rFns.PARAM_ACTIONS_FILENAME_MOTHER
        + settings.LOG_FILE_NAME_EXTENSION
    )
    data_file_name = os.path.join(settings.OUTPUT_FOLDER, log_file_name)
    if file_exist(data_file_name) == False:
        output("Need to create data file: {}".format(data_file_name))
        try:
            write_report_data_as_csv(data_file_name, rFns.LOG_FILE_HEADER, [])
        except Exception as e:
            output(
                "Failed to create data log file {} with exception: {}".format(
                    file_name_filter, e
                )
            )
            # make sure these temp files do not get deleted....
            raise ValueError("Failed to create log file {}".format(data_file_name))

    failed_files = []
    for file_name_filter in rFns.PARAM_ACTIONS_FILENAMES:
        files_matching = get_files_with_filter(
            settings.OUTPUT_FOLDER,
            settings.TEMP_FILE_NAME_EXTENSION,
            "*" + file_name_filter,
        )
        for file_match in files_matching:
            file_without_ext = get_file_name_without_ext(file_match)

            # append single temp file to data log file
            flag_append = append_to_file(data_file_name, file_match, True)
            if flag_append:
                output("Appended: {}  to: {}".format(file_without_ext, log_file_name))
            else:
                output(
                    "Failed to append: {} to: {}".format(
                        file_without_ext, log_file_name
                    )
                )
                failed_files.append(file_match)
    return failed_files


def append_files(
    folder_path, file_prefix, file_suffix, file_extension, out_put_file_name
):
    """
    DuHast append file wrapper...

    Used to append warnings to warnings report
    """
    file_list = get_files_single_directory(
        folder_path, file_prefix, file_suffix, file_extension
    )

    # build fully qualified out put file name
    full_out_file_name = os.path.join(settings.OUTPUT_FOLDER, out_put_file_name)

    for file in file_list:
        append_flag = append_to_file(
            source_file=full_out_file_name, append_file=file, ignore_first_row=True
        )
        output(
            "...appended {}  to {} with status [{}]".format(
                file, full_out_file_name, append_flag
            )
        )


def combine_data_files():
    """
    Combines varies report files which are created per Revit project file into a single text file
    """
    for file_to_combine in FILE_DATA_TO_COMBINE:
        output("Combining {} report files.".format(file_to_combine[0]))
        file_to_combine[2](
            folder_path=settings.OUTPUT_FOLDER,
            file_prefix="",
            file_suffix=file_to_combine[0],
            file_extension=settings.REPORT_FILE_NAME_EXTENSION,
            out_put_file_name=file_to_combine[1],
        )


# list of separate report file extensions and the combined file name
FILE_DATA_TO_COMBINE = [
    [
        settings.REPORT_EXTENSION_SHEETS_SHORT,
        settings.COMBINED_REPORT_NAME_SHEETS_SHORT,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_SHEETS,
        settings.COMBINED_REPORT_NAME_SHEETS,
        combine_files_csv_header_independent,
    ],
    [
        settings.REPORT_EXTENSION_SHARED_PARAMETERS,
        settings.COMBINED_REPORT_NAME_SHARED_PARAMETERS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_GRIDS,
        settings.COMBINED_REPORT_NAME_GRIDS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_LEVELS,
        settings.COMBINED_REPORT_NAME_LEVELS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_WORKSETS,
        settings.COMBINED_REPORT_NAME_WORKSETS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_GEO_DATA,
        settings.COMBINED_REPORT_NAME_GEO_DATA,
        combine_files_json,
    ],
    [
        settings.REPORT_EXTENSION_FAMILIES,
        settings.COMBINED_REPORT_NAME_FAMILIES,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_MARKED_VIEWS,
        settings.COMBINED_REPORT_NAME_MARKED_VIEWS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_WALL_TYPES,
        settings.COMBINED_REPORT_NAME_WALL_TYPES,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_VIEWS,
        settings.COMBINED_REPORT_NAME_VIEWS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_CAD_LINKS,
        settings.COMBINED_REPORT_NAME_CAD_LINKS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_REVIT_LINKS,
        settings.COMBINED_REPORT_NAME_REVIT_LINKS,
        combine_files,
    ],
    [
        settings.REPORT_EXTENSION_WARNING_TYPES,
        settings.COMBINED_REPORT_NAME_WARNING_TYPES,
        append_files,
    ],
]

# exit code for this script
# 0 all is ok
# 1 something went wrong

exit_code = 0
try:
    failed_files_ = merge_files()
except Exception as e:
    output("Failed to merge files: [{}]".format(e))
    exit_code = 1

try:
    output("Combining report files:")
    combine_data_files()
except Exception as e:
    output("Failed to combine report files: [{}]".format(e))
    exit_code = 1

try:
    output("Creating view template hash table:")
    combine_vt_data_result = combine_vt_reports(settings.OUTPUT_FOLDER)
    output(
        "Combined view template data files:{} [{}]".format(
            combine_vt_data_result.message, combine_vt_data_result.status
        )
    )
except Exception as e:
    output("Failed to create VT hash files: [{}]".format(e))
    exit_code = 1


try:
    output("Converting view template hash table files to parquet file format:")
    convert_to_parquet_result = convert_vt_reports_to_parquet(settings.OUTPUT_FOLDER)
    output(
        "Converted view template data files:{} [{}]".format(
            convert_to_parquet_result.message, convert_to_parquet_result.status
        )
    )
    if convert_to_parquet_result.status:
        output(
            "Deleting no longer required view template hash table files in json format:"
        )
        delete_json_hash_files_status = delete_hash_table_vt_json_reports(
            settings.OUTPUT_FOLDER
        )
        output(
            "Deleted no longer required view template hash table files in json format:{} [{}]".format(
                delete_json_hash_files_status.message,
                delete_json_hash_files_status.status,
            )
        )
except Exception as e:
    output("Failed to convert VT hash files to parquet format: [{}]".format(e))
    exit_code = 1

# return the exit code
sys.exit(exit_code)
