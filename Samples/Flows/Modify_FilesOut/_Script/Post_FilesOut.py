"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a post process script outside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is run after all batch processor sessions for step one and two have completed.

It:


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
import os.path
from System.IO import Path


import settings as settings  # sets up all commonly used variables and path locations!
from utils import utils as utilLocal
from utils.meta_data import meta_data
from utils.post_cleanup import clean_up_export_folder
from utils.docFile_utils import write_new_file_data

# import log utils
from duHast.Utilities import BatchProcessorLogUtils as logutils
from duHast.Utilities import WorksharingMonitorProcess as wsmp

# -------------
# my code here:
# -------------


# output messages
def Output(message=""):
    print(message)


# -------------
# main:
# -------------

# store output here:
root_path_ = settings.ROOT_PATH

# file data
doc_files_ = []
# read current file data
doc_files_ = utilLocal.read_current_file(settings.REVISION_DATA_FILEPATH)

# build out directory location
root_path_ = root_path_ + "\\" + settings.MODEL_OUT_FOLDER_NAME

# read file data from revit files processed
marker_file_data_ = []
marker_file_data_result = utilLocal.read_marker_files_from_revit_processed(
    root_path_, settings.MARKER_FILE_EXTENSION
)
if marker_file_data_result.status:
    marker_file_data_ = marker_file_data_result.result
    # writes out new file data file in script location
    flag_write_file_data_, doc_files_ = write_new_file_data(
        doc_files=doc_files_, marker_file_data=marker_file_data_
    )
    Output("Saved new document data file:...[{}]".format(flag_write_file_data_))

    # write out metadata file
    flag_meta_data_ = meta_data(
        meta_data_header=settings.ACONEX_METADATA_HEADER,
        doc_files=doc_files_,
        root_path=root_path_,
    )
    Output("Saved new Aconex meta data file:...[{}]".format(flag_meta_data_))
else:
    Output("Failed to read marker data:...[{}]".format(marker_file_data_result.message))

# run export folder clean up
flag_export_clean_up = clean_up_export_folder(root_path_)
Output("Clean up:...[{}]".format(flag_export_clean_up))

# process logs
processing_results_ = logutils.ProcessLogFiles(settings.LOG_MARKER_DIRECTORY)
Output(
    "Log result: {} :: [{}]".format(
        processing_results_.message, processing_results_.status
    )
)

# WSMP marker files clean up
clean_up_wsm_files_ = wsmp.CleanUpWSMDataFiles(settings.WSM_MARKER_DIRECTORY)
Output(
    "WSM result: {} :: [{}]".format(
        clean_up_wsm_files_.message, clean_up_wsm_files_.status
    )
)
