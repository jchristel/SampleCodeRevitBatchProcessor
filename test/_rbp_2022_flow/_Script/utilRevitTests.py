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

# set path to common library
import sys, os

# get the script location
SCRIPT_DIRECTORY = os.path.dirname(__file__)
# build flow directory name
FLOW_DIRECTORY =  os.path.dirname(SCRIPT_DIRECTORY)
# build duHast and duHast test directories
DU_HAST_TEST_DIRECTORY = os.path.dirname(os.path.dirname(FLOW_DIRECTORY))
DU_HAST_DIRECTORY = os.path.join(DU_HAST_TEST_DIRECTORY, r'duHast\src')

# add the directories to path
sys.path += [DU_HAST_DIRECTORY, DU_HAST_TEST_DIRECTORY,SCRIPT_DIRECTORY,]

# any data output to go here
OUTPUT_FOLDER = FLOW_DIRECTORY + r"\_Output"

# log marker file location
LOG_MARKER_DIRECTORY = FLOW_DIRECTORY + r"\_LogMarker"

# task list directory
TASK_LIST_DIRECTORY = FLOW_DIRECTORY + r"\_TaskList"

# task file name
TASK_FILE_NAME = "Tasklist_0.txt"

# fully qualified task file path
FULL_TASK_FILE_PATH = os.path.join(TASK_LIST_DIRECTORY, TASK_FILE_NAME)

# sample files directory
SAMPLE_FILES_DIRECTORY = FLOW_DIRECTORY + r"\_sampleFiles"

# WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

# splash sceen sheet name
SPLASH_SCREEN_SHEET_NAME = "SPLASH SCREEN"
