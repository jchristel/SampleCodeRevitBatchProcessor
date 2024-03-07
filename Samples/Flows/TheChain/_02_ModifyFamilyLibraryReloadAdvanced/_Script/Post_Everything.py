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


# flag whether this runs in debug or not
debug_ = False

# --------------------------
# default file path locations
# --------------------------

import os

# clr.AddReference('System.Core')
# clr.ImportExtensions(System.Linq)

import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.console_out import output
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_csv import read_csv_file, write_report_data_as_csv
from duHast.Utilities.files_io import file_delete

# -------------
# my code here:
# -------------

FILE_DATA_TO_COMBINE = [
    ["ChangedFamilies", "ChangedFilesTaskList" + settings.REPORT_FILE_EXTENSION]
]

# -------------
# main:
# -------------

# get part changed families report files
_files_to_combine = get_files_single_directory(
    settings.WORKING_DIRECTORY,
    settings.CHANGED_FAMILY_PART_REPORT_PREFIX,
    "",
    settings.REPORT_FILE_EXTENSION,
)
# check whether anything came back
if len(_files_to_combine) > 0:
    output("Found part changed family report files: {}".format(len(_files_to_combine)))
    rows_overall = []
    # combine files
    for _file in _files_to_combine:
        rows = read_csv_file(_file)
        output("read rows from file: [{}]  {}".format(len(rows) - 1, _file))
        # ignore header row
        for i in range(1, len(rows)):
            # read second column into list and append to overall list to be written to file
            # second column contains the file path in library location
            # first column is file path in temp (\Output) location
            rows_overall.append([rows[i][1]])
    # write data to file
    try:
        _combined_changed_family_report_path = os.path.join(
            settings.WORKING_DIRECTORY,
            settings.CHANGED_FAMILY_REPORT_FILE_NAME + settings.REPORT_FILE_EXTENSION,
        )
        write_report_data_as_csv(_combined_changed_family_report_path, "", rows_overall)
        output(
            "Successfully wrote combined changed family report to: {}".format(
                _combined_changed_family_report_path
            )
        )
        # delete single files
        for _file in _files_to_combine:
            _flag_delete = file_delete(_file)
            output("Deleted part file: [{}] {}".format(_flag_delete, _file))
    except Exception as e:
        output(
            "Failed to write combined family change list to file with exception: {}".format(
                e
            )
        )
else:
    output("No changed families part files found!")
