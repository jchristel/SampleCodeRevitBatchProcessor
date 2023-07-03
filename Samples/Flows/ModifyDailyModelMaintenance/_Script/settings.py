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
# Copyright (c) 2023  Jan Christel
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


DU_HAST_DIRECTORY = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
# set path to common library
import sys

sys.path += [DU_HAST_DIRECTORY]

from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.directory_io import get_parent_directory
from duHast.Utilities.compare import does_not_equal

#: get the script location
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
# add the script directory to path
sys.path += [SCRIPT_DIRECTORY]
#: build flow directory name
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)

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

# number of task files to be used / created
NO_OF_TASK_LIST_FILES = 3
# file extension of files to be processed
FILE_EXTENSION_OF_FILES_TO_PROCESS = ".rvt"


#: the project directory
PROJECT_DIRECTORY = r"P:\19\1903020.000\Design\BIM\_Revit"

# files to process directory
PATH_TO_FILES_TO_PROCESS = PROJECT_DIRECTORY + r"\1.0 Project Files"

# path to workset default visibility settings
WORKSET_DEFAULT_VISIBILITY_SETTINGS = FLOW_DIRECTORY + r"\ProjectsWorksets.txt"

# path to library folders
PATH_TO_CLINICAL_LIBRARY = PROJECT_DIRECTORY + r"\2.0 Project Library\__ClinicalLibrary"
PATH_TO_BESPOKE_JOINERY_LIBRARY = (
    PROJECT_DIRECTORY + r"\2.0 Project Library\__BespokeJoinery"
)
PATH_TO_UNIONS_LIBRARY = PROJECT_DIRECTORY + r"\2.0 Project Library\__Unions"

# reports by file extensions used
REPORT_EXTENSION_LEVELS = "_Levels"
REPORT_EXTENSION_SHEETS = "_Sheets"
REPORT_EXTENSION_SHEETS_SHORT = "_Sheets_Short"
REPORT_EXTENSION_GRIDS = "_Grids"
REPORT_EXTENSION_WORKSETS = "_Worksets"
REPORT_EXTENSION_SHARED_PARAMETERS = "_SharedParameters"
REPORT_EXTENSION_GEO_DATA = "_GeoData"
REPORT_EXTENSION_FAMILIES = "_Families"
REPORT_EXTENSION_MARKED_VIEWS = "_MarkedViews"
REPORT_EXTENSION_VIEWS = "_Views"
REPORT_EXTENSION_WALL_TYPES = "_Wall_Types"
REPORT_EXTENSION_FFE_TAG_INSTANCES = "_FFE_Tags"

# combined report file names
COMBINED_REPORT_NAME_LEVELS = "ProjectsLevels.csv"
COMBINED_REPORT_NAME_SHEETS = "ProjectsSheets.csv"
COMBINED_REPORT_NAME_SHEETS_SHORT = "SheetData_Short.csv"
COMBINED_REPORT_NAME_GRIDS = "ProjectsGrids.csv"
COMBINED_REPORT_NAME_WORKSETS = "ProjectsWorksets.csv"
COMBINED_REPORT_NAME_SHARED_PARAMETERS = "ProjectsSharedParametersCombinedReport.csv"
COMBINED_REPORT_NAME_GEO_DATA = "ProjectsGeoData.txt"
COMBINED_REPORT_NAME_FAMILIES = "ProjectsFamilies.csv"
COMBINED_REPORT_NAME_MARKED_VIEWS = "MarkedViews.csv"
COMBINED_REPORT_NAME_VIEWS = "Views.csv"
COMBINED_REPORT_NAME_WALL_TYPES = "Wall_Types.csv"

# list containing default worksets for levels grids, scope boxes per project file
DEFAULT_WORKSETS = [["NHR-", ["99_LEVELS AND GRIDS"]]]

# file containing unwanted shared parameters which will get auto deleted
# in format name <tab> GUID
UNWANTED_SHARED_PARAMETER_FILE = "UnwantedSharedParameters.csv"

# temp file name extension
TEMP_FILE_NAME_EXTENSION = ".temp"

# report file extension
REPORT_FILE_NAME_EXTENSION = ".csv"

# log file extension
LOG_FILE_NAME_EXTENSION = ".log"

# log file name prefix:
LOG_FILE_NAME_PREFIX = "LogFile"

# list containing view rules per project file
# views with properties listed here will not be marked as deleted
# script will stop processing rules after the first file match...
# put more specific rules to front of list!!
VIEW_KEEP_RULES = [
    [
        "NHR-BVN-MOD-ARC",
        [
            ["Design Stage", does_not_equal, "WORKING"],
        ],
    ]
]

# list containing names of files in which no family reload is to be undertaken
EXCLUDE_FILES_FROM_FAMILY_RELOAD = ["NHR-BVN-MOD-ARC-EBL-00M-NL00001"]

# These are the properties to be reported on in filtered views reports
VIEW_DATA_FILTERS = [
    "View Name",
    "Title on Sheet",
    "View Template",
    "Design Stage",
]

# FFE tag type name to be reported on prior family reload so
# tags can be moved back if reload shifted them
MULTI_CATEGORY_TAG_TYPE_NAME = "Label Only"
