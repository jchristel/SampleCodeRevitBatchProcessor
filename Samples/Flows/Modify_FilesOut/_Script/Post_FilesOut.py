"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a post process script outside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is run after all batch processor sessions for step one and two have completed.

It:
    - reads the marker files for each file exported and compiles a meta data file from it
    - deletes any temp revit files, log files, marker files
    - processes batch processor log files to checks for any exceptions which may have occurred during processing
    - removes worksharing monitor marker files

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

# import clr
# import System
import os


import settings as settings  # sets up all commonly used variables and path locations!
from utils.revision_marker_files import read_marker_files_from_revit_processed
from utils.meta_data import write_meta_data
from utils.post_cleanup import clean_up_export_folder
from utils.docFile_io import write_new_file_data, read_current_file
from duHast.Utilities.console_out import output_with_time_stamp as output
from duHast.Utilities.batch_processor_log_utils import process_log_files
from duHast.Utilities.worksharing_monitor_process import clean_up_wsm_data_files


# -------------
# my code here:
# -------------


# -------------
# main:
# -------------

# store output here:
root_path_ = settings.ROOT_PATH

# file data
doc_files_ = []
# read current file data
doc_files_ = read_current_file(settings.REVISION_DATA_FILEPATH)

# build out directory location
root_path_ = os.path.join(root_path_, settings.MODEL_OUT_FOLDER_NAME)

# read file data from revit files processed
marker_file_data_ = []
marker_file_data_result = read_marker_files_from_revit_processed(
    root_path_, settings.MARKER_FILE_EXTENSION
)
if marker_file_data_result.status:
    marker_file_data_ = marker_file_data_result.result
    # writes out new file data file in script location
    flag_write_file_data_ = write_new_file_data(
        doc_files=doc_files_, marker_file_data=marker_file_data_
    )
    output("Saved new document data file:...[{}]".format(flag_write_file_data_.status))
    if flag_write_file_data_.status == False:
        output(flag_write_file_data_.message)

    # write out metadata file
    flag_meta_data_ = write_meta_data(
        meta_data_header=settings.ACONEX_METADATA_HEADER,
        doc_files=flag_write_file_data_.result[0],
        root_path=root_path_,
    )
    output("Saved new Aconex meta data file:...[{}]".format(flag_meta_data_.status))
    if flag_meta_data_.status == False:
        output(flag_meta_data_.message)
else:
    output("Failed to read marker data:...[{}]".format(marker_file_data_result.message))

# run export folder clean up
flag_export_clean_up_ = clean_up_export_folder(root_path_)
output("Clean up:...[{}]".format(flag_export_clean_up_.status))
if flag_export_clean_up_.status == False:
    output(flag_export_clean_up_.message)

# process logs
processing_results_ = process_log_files(settings.LOG_MARKER_DIRECTORY)
output(
    "Log result: {} :: [{}]".format(
        processing_results_.message, processing_results_.status
    )
)

# WSMP marker files clean up
clean_up_wsm_files_ = clean_up_wsm_data_files(settings.WSM_MARKER_DIRECTORY)
output(
    "WSM result: {} :: [{}]".format(
        clean_up_wsm_files_.message, clean_up_wsm_files_.status
    )
)
