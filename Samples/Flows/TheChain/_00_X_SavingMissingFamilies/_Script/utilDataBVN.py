'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of global variables.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Apart from defining a number of variable values this module also updates path variable with directories containing modules required to 
run this script.

'''

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
#
#

# path to Common library modules
COMMON_LIBRARY_DEBUG_PATH = r'\\bvn\Data\studio\infotech\standards\Scripts\Revit Python\RBP\SampleCodeRevitBatchProcessor\Library'
COMMON_LIBRARY_UI_DEBUG_PATH = r'\\bvn\Data\studio\infotech\standards\Scripts\Revit Python\RBP\SampleCodeRevitBatchProcessor\UI'
#SCRIPT_LOCATION = r'P:\19\1903020.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\_00_ReportFamilyData\_Script'


# set path to common library
import sys
sys.path += [COMMON_LIBRARY_DEBUG_PATH, COMMON_LIBRARY_UI_DEBUG_PATH]

import Utility as util

# get the script location
SCRIPT_DIRECTORY = util.GetFolderPathFromFile(__file__)
# add the script directory to path
sys.path += [SCRIPT_DIRECTORY]
# build flow directory name
FLOW_DIRECTORY = util.GetParentDirectory(SCRIPT_DIRECTORY)
# build user directory name
ROOT_SCRIPT_DIRECTORY_USER = FLOW_DIRECTORY + r'\_Users'+ '\\' + util.GetCurrentUserName()

# how many task files are written to file
NUMBER_OF_TASK_FILES = 4
# where are task files located
TASK_FILE_DIRECTORY = ROOT_SCRIPT_DIRECTORY_USER + r'\_TaskList'
# file extension of files to be processed
FILE_EXTENSION_OF_FILES_TO_PROCESS = '.rfa'

# Root directory path of files to be processed
REVIT_FILES_DIRECTORY = r'\\bvn\data\studio\SharedAssets\Revit\RevitContent\CentralHealthLibrary\_Kinship'

# log marker file location
LOG_MARKER_DIRECTORY = ROOT_SCRIPT_DIRECTORY_USER + r'\_LogMarker'

# WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# input directory path
# may contain marker files (see below) 
INPUT_DIRECTORY = ROOT_SCRIPT_DIRECTORY_USER + r'\_Input'

# any data output to go here
OUTPUT_FOLDER = ROOT_SCRIPT_DIRECTORY_USER + r'\_Output'
# combined families folder
OUTPUT_FOLDER_COMBINED_FAMILIES = ROOT_SCRIPT_DIRECTORY_USER + r'\_Output\combined'
ANALYSIS_FOLDER = ROOT_SCRIPT_DIRECTORY_USER + r'\_Analysis'
ANALYSIS_CURRENT_FOLDER = ROOT_SCRIPT_DIRECTORY_USER + r'\_Analysis\_Current'

# all reports are of this file type
REPORT_FILE_EXTENSION = '.csv'

# log file containing any files where an exception occured during processing or one of the processors failed
FILE_NAME_EXCEPTIONS_REPORT = 'ProcessExceptions' + REPORT_FILE_EXTENSION

# log file containing any files where circular referencing occured
FILE_NAME_CIRCULAR_REFERENCE_REPORT = 'CircularReferences' + REPORT_FILE_EXTENSION

# log file containing any files containing missing families
FILE_NAME_MISSING_FAMILIES_REPORT = 'MissingFamilies' + REPORT_FILE_EXTENSION

# log file containing any files containing missing families (to be used in follow up processing run where only these families
# will be processed rather then the entire data sat)
FILE_NAME_SECOND_PROCESS_FAMILIES_REPORT = 'SecondProcessFamilies' + REPORT_FILE_EXTENSION

# log file containing any files containing missing families
FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT = 'HostsMissingFamilies' + REPORT_FILE_EXTENSION

# marker file indicating missing families are to be saved out.
# contains two rows:
# - first row: fully qualified file path of family base data report file to be used as reference
# - second row: fully qualified root directory path to where save missing families to
FILE_NAME_MARKER_SAVEOUT_MISSING_FAMILIES = 'SaveOutMissingFams' + REPORT_FILE_EXTENSION

# marker file indicating that in a post process the combined report files are to be merged with (older) report files 
# in a given folder
# contains single rows:
# - first row: fully qualified root directory path to where other family data files are located.
FILE_NAME_MARKER_MERGE_FAMILY_DATA = 'MergeFamilyData' + REPORT_FILE_EXTENSION


def SaveOutMissingFamiliesCheck():
    '''
    Check whether a marker file exists, which specifies: where family base report is located and the directory to save missing families to.

    :return: True if marker file exists, otherwise False. The file path of the family base data raport. The root directory path to where families are to be saved to.
    :rtype: bool, string, string
    '''

    saveOut = False
    familyBaseDataFilePath = ''
    familyOutDirectory = ''

    # build marker file path
    markerFilePath = INPUT_DIRECTORY + '\\' + FILE_NAME_MARKER_SAVEOUT_MISSING_FAMILIES
    # check if file exists in input location
    if(util.FileExist(markerFilePath)):
        # read file
        rows = util.ReadCSVfile(markerFilePath)
        # should be at least two rows...
        if (len(rows) >= 2):
            gotBaseData = False
            gotDirOut = False
            # assign family base data file path
            if(util.FileExist(rows[0][0])):
                familyBaseDataFilePath = rows[0][0]
                gotBaseData = True
            # assign family out file path
            if(util.DirectoryExists(rows[1][0])):
                familyOutDirectory = rows[1][0]
                gotDirOut = True
            saveOut = gotBaseData and gotDirOut
    return saveOut , familyBaseDataFilePath , familyOutDirectory