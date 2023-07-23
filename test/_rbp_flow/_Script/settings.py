"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing settings used in all flow scripts.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- adds the following directories to the environment

    - duHast library
    - test library

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
# Copyright © 2023, Jan Christel
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

# set path to common library
import sys, os

# get the script location
SCRIPT_DIRECTORY = os.path.dirname(__file__)
# build flow directory name
FLOW_DIRECTORY = os.path.dirname(SCRIPT_DIRECTORY)
# build duHast and duHast test directories
DU_HAST_TEST_DIRECTORY = os.path.dirname(os.path.dirname(FLOW_DIRECTORY))
DU_HAST_DIRECTORY = os.path.join(DU_HAST_TEST_DIRECTORY, r"duHast\src")

# add the directories to path
sys.path += [
    DU_HAST_DIRECTORY,
    DU_HAST_TEST_DIRECTORY,
    SCRIPT_DIRECTORY,
]

# any data output to go here
OUTPUT_FOLDER = FLOW_DIRECTORY + r"\_Output"

# log marker file location
LOG_MARKER_DIRECTORY = FLOW_DIRECTORY + r"\_LogMarker"

# task list directory
TASK_LIST_DIRECTORY = FLOW_DIRECTORY + r"\_TaskList"

# sample files directory
SAMPLE_FILES_DIRECTORY = FLOW_DIRECTORY + r"\_sampleFiles"

# WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

# splash sceen sheet name
SPLASH_SCREEN_SHEET_NAME = "SPLASH SCREEN"

#: revit version used in determining which revit files to add to task list
#: Revit files will have revit version number applicable to them in their file name
DEFAULT_REVIT_VERSION = "Revit_2022"
