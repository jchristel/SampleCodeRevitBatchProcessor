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

# import common library
from duHast.Utilities import Utility as util

# import log utils
from duHast.Utilities import BatchProcessorLogUtils as logutils
from duHast.Utilities import WorksharingMonitorProcess as wsmp

# -------------
# my code here:
# -------------


# output messages
def Output(message=""):
    print(message)


# writes out the document data file back in the script folder
# with updated revision information retrieved from marker files
def write_new_file_data(doc_files):
    flag = False
    # compare lists
    doc_files_sorted = []
    for cfd in doc_files:
        match = False
        for nfd in marker_file_data_:
            if (
                nfd.existingFileName == cfd.existingFileName
                and nfd.fileExtension == cfd.fileExtension
            ):
                match = True
                doc_files_sorted.append(nfd)
                break
        if match == False:
            doc_files_sorted.append(cfd)
    data = convert_class_to_string(doc_files_sorted)
    flag = write_new_data(settings.REVISION_DATA_FILEPATH, data)
    return flag, doc_files_sorted


# write new revision data out to file
def write_new_data(path, data):
    status = True
    try:
        util.writeReportDataAsCSV(path, [], data)
    except Exception as e:
        status = False
        Output("Failed to write data file: {} with exception: {}".format(path, e))
    return status


def convert_class_to_string(doc_files):
    data = []
    for doc_file in doc_files:
        data.append(doc_file.getData())
    return data


# deletes back up folders and revit project files
def clean_up_export_folder():
    status = True
    # delete sub directories
    try:
        sub_dirs = util.GetChildDirectories(settings.ROOT_PATH_EXPORT)
        if len(sub_dirs) > 0:
            for d in sub_dirs:
                status = status & util.DirectoryDelete(d)
    except Exception as e:
        Output("Failed to delete sub directory with exception {}".format(e))
        status = status & False
    try:
        # delete rvt files
        revit_files = util.GetFilesWithFilter(settings.ROOT_PATH_EXPORT)
        if len(revit_files) > 0:
            for f in revit_files:
                status = status & util.FileDelete(f)
    except Exception as e:
        Output("Failed to delete file with exception {}".format(e))
        status = status & False

    try:
        # delete txt marker files
        text_files = util.GetFilesWithFilter(
            root_path_, settings.MARKER_FILE_EXTENSION, "*"
        )
        if len(text_files) > 0:
            for f in text_files:
                status = status & util.FileDelete(f)
    except Exception as e:
        Output("Failed to delete file with exception {}".format(e))
        status = status & False

    try:
        # delete log files
        text_files = util.GetFilesWithFilter(root_path_, ".log", "*")
        if len(text_files) > 0:
            for f in text_files:
                status = status & util.FileDelete(f)
    except Exception as e:
        Output("Failed to delete log file with exception: {}".format(e))
        status = status & False

    return status


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
    flag_write_file_data_, doc_files_ = write_new_file_data(doc_files_)
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
flag_export_clean_up = clean_up_export_folder()
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
