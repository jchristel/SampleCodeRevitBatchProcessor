#!/usr/bin/python
# -*- coding: utf-8 -*-
#License:
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


# path to Common library modules
COMMON_LIBRARY_DEBUG_PATH = r'\\bvn\Data\studio\infotech\standards\Scripts\Revit Python\RBP\SampleCodeRevitBatchProcessor\Library'
COMMON_LIBRARY_UI_DEBUG_PATH = r'\\bvn\Data\studio\infotech\standards\Scripts\Revit Python\RBP\SampleCodeRevitBatchProcessor\UI'
SCRIPT_LOCATION = r'P:\19\1906009.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\ModifyRevitBVNFiles\_Script'
DU_HAST_DIRECTORY = r'\\bvn\Data\studio\infotech\standards\Scripts\Revit Python\RBP\Lib\site-packages'

# set path to common library
import sys
sys.path += [COMMON_LIBRARY_DEBUG_PATH, COMMON_LIBRARY_UI_DEBUG_PATH,  DU_HAST_DIRECTORY]

# import common library
from duHast.Utilities import Utility as util

# get the script location
SCRIPT_DIRECTORY = util.GetFolderPathFromFile(__file__)
sys.path += [SCRIPT_DIRECTORY]

# build flow directory name
FLOW_DIRECTORY = util.GetParentDirectory(SCRIPT_DIRECTORY)

# store output here:
ROOT_PATH = r'P:\19\1906009.000\Exchange\Out\__BIM Models\2023'
ROOT_PATH_NWC = r'P:\19\1906009.000\Design\BIM\Navisworks\Current Model'
ROOT_PATH_IFC = r'P:\19\1906009.000\Design\BIM\IFC'
# store rev data here:
REVISION_DATA_FILEPATH = FLOW_DIRECTORY + r'\_Script\FileNames.csv'
# store export step 2 files here
ROOT_PATH_EXPORT = FLOW_DIRECTORY + r'\_Output'
# log marker file location
LOG_MARKER_DIRECTORY = FLOW_DIRECTORY + r'\_LogMarker'
# WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY


# bim 360 folder for Revit and NWC files
BIM360_FOLDER_NAME = 'BIM360Out'

# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Files.rvt'
# file extension of files to be processed
FILE_EXTENSION_OF_FILES_TO_PROCESS = '.rvt'
# splash sceen sheet name
SPLASH_SCREEN_SHEET_NAME = 'SPLASH SCREEN'
# header row for aconex meta data file
ACONEX_METADATA_HEADER = [
    'Document No',
    'Revision',
    'Title',
    'Type',
    'Status',
    'Discipline',
    'Project Phase',
    'File',
    'Print Size',
    'Alternative Reference',
    'Revision Date',
    'Created By Organization',
    'Comments',
    'Author',
    'Required for Handover?',
    'Supersede'
]

ACONEX_METADATA_FILE_NAME = 'AconexMetaData.csv'
ACONEX_METADATA_COMPANY = 'BVN'
ACONEX_METADATA_DISCIPLINE = 'Architectural'
ACONEX_METADATA_DOC_TYPE = 'Model'
ACONEX_METADATA_DOC_STATUS = 'Information Only'
ACONEX_METADATA_DATE_FORMAT = '%d/%m/%Y'
ACONEX_METADATA_NOT_APPLICABLE = 'NA'

ACONEX_METADATA_PROJECT_PHASE = '2. Detailed Business Case/Schematic Design'


# model out folder name
MODEL_OUT_FOLDER_NAME = util.GetFolderDateStamp(util.FOLDER_DATE_STAMP_YYMMDD) + '_MODEL_WEEKLY ISSUE'
# marker file extension
MARKER_FILE_EXTENSION = '.txt'
# export file formats extensions
IFC_FILE_EXTENSION = '.ifc'
NWC_FILE_EXTENSION = '.nwc'
RVT_FILE_EXTENSION = '.rvt'
# Views to be exported Prefix
EXPORT_NWC_VIEW_PREFIX = 'ETN-'
EXPORT_IFC_VIEW_PREFIX = 'ETI-'
# flag indicating whether IFC and navis exports should have the same revision as the revit file theya re created from
# or use their own sequence
EXPORT_FILES_USE_REVIT_REVISION = True

# contains prefixes of views to be exported and therefore will not 
# be deleted in step two
VIEWS_TO_KEEP_FOR_EXPORT = [
    EXPORT_NWC_VIEW_PREFIX,
    EXPORT_IFC_VIEW_PREFIX
]
# Revision format for exports
REVISION_PREFIX = '['
REVISION_SUFFIX = ']'
# number of task files in use
TASK_FILE_NO = 3
# revit file name prefix for detached  copy used to export from
REVIT_FILE_NAME_PREFIX_EXPORT = '_EXPORT_'

# list containing default worksets for levels grids, scope boxes per project file
DEFAULT_WORKSETS = [
    ['ARC-1906009-MOD-NBH-00M-NL-0', '99_LEVELS AND GRIDS']
]

# list containing sheet rules per project files
# sheet with properties listed here  will not be deleted
# script will stop processing rules after the first file match...
# put more specific rules to front of list!!
SHEET_KEEP_RULES = [
    ['ARC-1906009-MOD-NBH-00M-NL-0',[
        ['Design Stage', util.ConDoesNotEqual, 'DOCUMENTATION'],
        ['Design Stage', util.ConDoesNotEqual, 'MODEL MANAGEMENT']
        ]
    ]
]

# list containing view rules per project file
# views with properties listed here will not be deleted
# script will stop processing rules after the first file match...
# put more specific rules to front of list!!
VIEW_KEEP_RULES = [
     ['ARC-1906009-MOD-NBH-00M-NL-0',[
        ['Element Series', util.ConDoesNotEqual, 'STARTING VIEWS'],
        ['Design Stage', util.ConDoesNotEqual, 'LINKED VIEW'],
        ['Design Stage', util.ConDoesNotEqual, 'DOCUMENTATION'],
        ['Design Stage', util.ConDoesNotEqual, 'MODEL EXPORT']
    ]]
]