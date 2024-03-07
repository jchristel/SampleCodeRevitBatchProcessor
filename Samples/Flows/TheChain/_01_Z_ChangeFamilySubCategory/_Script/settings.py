"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a settings module 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It contains 

- Global variables used throughout the modules in this workflow.
- Amends PATH variable to include sample code library locations

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
DU_HAST_DEBUG = r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\src"

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

# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

# revit files library location
REVIT_LIBRARY_PATH = r"C:\Users\jchristel\dev\test_lib"
REVIT_LIBRARY_INCLUDE_SUB_DIRS_IN_SEARCH = True
FILE_EXTENSION_OF_FILES_TO_PROCESS = ".rfa"

# this is where families will be saved temporarily after successful reload
WORKING_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_Output")

# log marker file location
LOG_MARKER_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_LogMarker")

#: WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# directory containing any task lists identifying specific families only to be processed
# if that folder is empty, all families in library will be processed
# directory may also contain any other input data required for tasks to be executed in files processed. i.e.
#   - rename loaded families
#   - rename custom categories
PREDEFINED_TASK_FILE_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_TaskList")
# any predefined task file needs to start with this string
PREDEFINED_TASK_FILE_NAME_PREFIX = "ChangeList"
# file name filter
PREDEFINED_TASK_FILE_NAME_FILTER = PREDEFINED_TASK_FILE_NAME_PREFIX
PREDEFINED_TASK_FILE_EXTENSION = ".task"

# all reports are of this file type
REPORT_FILE_EXTENSION = ".csv"

# location of any input files ( refer docs for details )
INPUT_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_Input")

# flag indicating whether to add default parameters to families
ADD_DEFAULT_PARAMETERS = False

# file name of follow up report
FOLLOW_UP_REPORT_FILE_NAME = "FollowUpReportList" + REPORT_FILE_EXTENSION

# where are task files located
TASK_FILE_DIRECTORY = os.path.join(ROOT_SCRIPT_DIRECTORY_USER, "_TaskList")
# number of task files in use
TASK_FILE_NO = 4

# flag indicating whether this is a cloud based project
IS_CLOUD_PROJECT = False
