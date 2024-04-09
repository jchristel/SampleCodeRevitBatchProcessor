"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of global variables.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Apart from defining a number of variable values this module also updates path variable with directories containing modules required to 
run this script.

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
#
#

# path to Common library modules
DU_HAST_PATH = r"C:\Program Files\Python311\Lib\site-packages"
DU_HAST_DEBUG =r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\src"

# set path to common library
import sys
sys.path = [DU_HAST_DEBUG] + sys.path
sys.path += [DU_HAST_PATH]

import os

from duHast.Utilities.directory_io import get_parent_directory
from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.utility import get_current_user_name

# get the script location
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
# add the script directory to path
sys.path += [SCRIPT_DIRECTORY]
# build flow directory name
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)
# build user directory name
ROOT_SCRIPT_DIRECTORY_USER = os.path.join(
    FLOW_DIRECTORY, "_Users" + "\\" + get_current_user_name()
)

# how many task files are written to file
NUMBER_OF_TASK_FILES = 4
# where are task files located
TASK_FILE_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_TaskList")
# file extension of files to be processed
FILE_EXTENSION_OF_FILES_TO_PROCESS = ".rfa"

# Root directory path of files to be processed
# (note: this is the root directory of the files to be processed and not the root directory of the entire project)
# ideally this can be moved into a config file by user... TODO:
REVIT_LIBRARY_PATH = r'C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData'

# log marker file location
LOG_MARKER_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_LogMarker")

# WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# input directory path
# may contain marker files (see below)
INPUT_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER , "_Input")

# any data output to go here
OUTPUT_FOLDER = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_Output")
ANALYSIS_FOLDER = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_Analysis")
ANALYSIS_CURRENT_FOLDER = os.path.join(ROOT_SCRIPT_DIRECTORY_USER , r"_Analysis\_Current")

# all reports are of this file type
REPORT_FILE_EXTENSION = ".csv"

# log file containing any files where an exception occured during processing or one of the processors failed
FILE_NAME_EXCEPTIONS_REPORT = "ProcessExceptions" + REPORT_FILE_EXTENSION

# log file containing any files where circular referencing occured
FILE_NAME_CIRCULAR_REFERENCE_REPORT = "CircularReferences" + REPORT_FILE_EXTENSION

# log file containing any files containing missing families
FILE_NAME_MISSING_FAMILIES_REPORT = "MissingFamilies" + REPORT_FILE_EXTENSION

# log file containing any files containing missing families (to be used in follow up processing run where only these families
# will be processed rather then the entire data sat)
FILE_NAME_SECOND_PROCESS_FAMILIES_REPORT = (
    "SecondProcessFamilies" + REPORT_FILE_EXTENSION
)

# log file containing any files containing missing families
FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT = "HostsMissingFamilies" + REPORT_FILE_EXTENSION

# marker file indicating missing families are to be saved out.
# contains two rows:
# - first row: fully qualified file path of family base data report file to be used as reference
# - second row: fully qualified root directory path to where save missing families to
FILE_NAME_MARKER_SAVEOUT_MISSING_FAMILIES = "SaveOutMissingFams" + REPORT_FILE_EXTENSION

# marker file indicating that in a post process the combined report files are to be merged with previous (older) report files
# in a given folder
# contains single rows:
# - first row: fully qualified root directory path to where previous family data files are located.
FILE_NAME_MARKER_MERGE_FAMILY_DATA = "MergeFamilyData" + REPORT_FILE_EXTENSION

# flag indicating whether this is a cloud based project
IS_CLOUD_PROJECT = False
