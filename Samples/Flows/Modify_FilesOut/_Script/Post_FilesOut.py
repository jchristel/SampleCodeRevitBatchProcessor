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
