"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the flows global settings.
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
# Copyright 2024, Jan Christel
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


DU_HAST_DIRECTORY_DEV_LOCAL = (
    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\src"
)
DU_HAST_DIRECTORY_DEV_NETWORK = (
    r"\\"
)
# set path to common library
import sys
import os

# flag toggling between development or product version of duHast
_use_dev_du_hast = True

if _use_dev_du_hast:
    # inserting at 0 index makes sure the dev version of duHast is used rather then the installed product version
    sys.path.insert(0, DU_HAST_DIRECTORY_DEV_LOCAL)
else:
    # add reference to production version of duHast
    sys.path += [DU_HAST_DIRECTORY_DEV_NETWORK]


from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.directory_io import get_parent_directory

#: get the script location
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)

# add the script directory to path
sys.path += [SCRIPT_DIRECTORY]

#: build flow directory name
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)

#: log marker file location
LOG_MARKER_DIRECTORY = os.path.join(FLOW_DIRECTORY, r"_LogMarker")

#: log file destination folder name
LOGFILE_COPY_TO_DIRECTORY = os.path.join(FLOW_DIRECTORY, r"_LogFilesFromRTV")

#: WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# number of task files to be used / created
NO_OF_TASK_LIST_FILES = 1

# file extension of files to be processed
FILE_EXTENSION_OF_FILES_TO_PROCESS = ".rvt"

# nwc file extension
NWC_FILE_EXTENSION = ".nwc"

# ifc file extension
IFC_FILE_EXTENSION = ".ifc"

# flag indicating whether this is a cloud based project
IS_CLOUD_PROJECT = False

# source path of files to be processed
PATH_TO_FILES_TO_PROCESS = r"\path\to\source\files"

# default output path if no file data present
ROOT_PATH_REVIT_DEFAULT = r"default\save\as\path"

# directory containing revit batch processor task files
TASK_LIST_DIRECTORY = os.path.join(FLOW_DIRECTORY, r"_TaskList")

# path to downloaded zip files
# file will be unpacked and moved into PATH_TO_FILES_TO_PROCESS
SOURCE_PATH_ZIP_FILES = os.path.join(PATH_TO_FILES_TO_PROCESS, "Zips")

# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

# default revision value to be used if there is no revision attached to file
DEFAULT_REVISION = "-"

# model in folder name
MODEL_IN_FILING_FOLDER_NAME = "_Models"

# name of the csv file containing all incoming file information
DATA_FILE_NAME = "file_data.csv"
# fully qualified file path of incoming file information
DATA_FILE_PATH = os.path.join(SCRIPT_DIRECTORY, DATA_FILE_NAME)

# revision tracker file name
REVISION_TRACKER_FILE_NAME = "issueList.csv"

# characters used to delineate revision information in a file name
REVISION_SEPARATORS_START = ["[", "("]
REVISION_SEPARATORS_END = ["]", ")"]

# flag indicating whether to delete any links (Revit and CAD) in the file
DELETE_LINKS = True