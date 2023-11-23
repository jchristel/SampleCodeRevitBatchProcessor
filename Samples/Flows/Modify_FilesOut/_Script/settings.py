"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing settings used in all flow scripts.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- adds the following directories to the environment

    - duHast library

- populates a number of variables used in all flow scripts
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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


DU_HAST_DIRECTORY = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
# set path to common library
import sys

sys.path += [DU_HAST_DIRECTORY]

from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.directory_io import get_parent_directory
from duHast.Utilities.compare import does_not_equal
from duHast.Utilities.date_stamps import get_folder_date_stamp

# import common library
#from duHast.Utilities import Utility as util

#: get the script location
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
# add the script directory to path
sys.path += [SCRIPT_DIRECTORY]
#: build flow directory name
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)

# store output here:
ROOT_PATH = r"export\revit\models\to\here"
ROOT_PATH_NWC = r"copy\nwc\models\here\after\export"
ROOT_PATH_IFC = r"copy\IFC\models\here\after\export"


# store rev data here:
REVISION_DATA_FILEPATH = FLOW_DIRECTORY + r"\_Script\FileNames.csv"

#: any data output to go here
OUTPUT_FOLDER = FLOW_DIRECTORY + r"\_Output"

#: log marker file location
LOG_MARKER_DIRECTORY = FLOW_DIRECTORY + r"\_LogMarker"

#: log file destination folder name
LOGFILE_COPY_TO_DIRECTORY = FLOW_DIRECTORY + r"_LogFilesFromRTV"

#: WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# directory containing revit batch processor task files
TASK_LIST_DIRECTORY = FLOW_DIRECTORY + r"\__TaskList"

# flag indicating whether this is a cloud based project
IS_CLOUD_PROJECT = False

# number of task files to be used / created
NO_OF_TASK_LIST_FILES = 3
# file extension of files to be processed
FILE_EXTENSION_OF_FILES_TO_PROCESS = ".rvt"

# bim 360 folder for Revit and NWC files
# exported models will be copied into this folder with revision removed from file name
BIM360_FOLDER_NAME = "BIM360Out"

# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

# splash sceen sheet name
SPLASH_SCREEN_SHEET_NAME = "SPLASH SCREEN"

# header row for aconex meta data file (may vary from project to project)
ACONEX_METADATA_HEADER = [
    "Document No",
    "Revision",
    "Title",
    "Type",
    "Status",
    "Discipline",
    "Project Phase",
    "File",
    "Print Size",
    "Alternative Reference",
    "Revision Date",
    "Created By Organization",
    "Comments",
    "Author",
    "Required for Handover?",
    "Supersede",
]

ACONEX_METADATA_FILE_NAME = "AconexMetaData.csv"
ACONEX_METADATA_COMPANY = "your company name here"
ACONEX_METADATA_DISCIPLINE = "Architectural"
ACONEX_METADATA_DOC_TYPE = "Model"
ACONEX_METADATA_DOC_STATUS = "Information Only"
ACONEX_METADATA_DATE_FORMAT = "%d/%m/%Y"
ACONEX_METADATA_NOT_APPLICABLE = "NA"

# custom aconex property
ACONEX_METADATA_PROJECT_PHASE = "your project phase"


# model out folder name
MODEL_OUT_FOLDER_NAME = (
    get_folder_date_stamp() + "_MODEL_WEEKLY ISSUE"
)
# marker file extension
MARKER_FILE_EXTENSION = ".txt"
# export file formats extensions
IFC_FILE_EXTENSION = ".ifc"
NWC_FILE_EXTENSION = ".nwc"
RVT_FILE_EXTENSION = ".rvt"
# Views to be exported Prefix
EXPORT_NWC_VIEW_PREFIX = "ETN-"
EXPORT_IFC_VIEW_PREFIX = "ETI-"
# flag indicating whether IFC and navis exports should have the same revision as the revit file theya re created from
# or use their own sequence
EXPORT_FILES_USE_REVIT_REVISION = True

# contains prefixes of views to be exported and therefore will not
# be deleted in step two
VIEWS_TO_KEEP_FOR_EXPORT = [EXPORT_NWC_VIEW_PREFIX, EXPORT_IFC_VIEW_PREFIX]
# Revision format for exports
REVISION_PREFIX = "["
REVISION_SUFFIX = "]"

# revit file name prefix for detached  copy used to export from
REVIT_FILE_NAME_PREFIX_EXPORT = "_EXPORT_"

# list containing default worksets for levels grids, scope boxes per project file
DEFAULT_WORKSETS = [["Revit project file name start", "Shared Levels and Grids"]]

# list containing sheet rules per project files
# sheet with properties listed here  will not be deleted
# script will stop processing rules after the first file match...
# put more specific rules to front of list!!
SHEET_KEEP_RULES = [
    [
        "Revit project file name start",
        [
            ["Sheet property name", does_not_equal, "sample value"],
            ["Sheet property name", does_not_equal, "sample value"],
        ],
    ]
]

# list containing view rules per project file
# views with properties listed here will not be deleted
# script will stop processing rules after the first file match...
# put more specific rules to front of list!!
VIEW_KEEP_RULES = [
    [
        "Revit project file name start",
        [
            ["view property name", does_not_equal, "sample value"],
            ["view property name", does_not_equal, "sample value"],
            ["view property name", does_not_equal, "sample value"],
            ["view property name", does_not_equal, "sample value"],
        ],
    ]
]

# list containing file names of files in which not delete revit links from
DO_NOT_DELETE_LINKS = [
    "sample Revit file name",
]
