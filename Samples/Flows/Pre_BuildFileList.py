"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write files to task lists.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to write files in a given directory to an arbitrary number of task lists for Revit Batch Processor.

Note:

This code below will:

- filter files in a given directory by their file extension
- add them to task lists depending on their file size in an attempt to create an equal workload for all Revit Batch Processor sessions to be spun up. 

This script can be used when: 

- multiple sessions of Revit Batch Processor are to be run in parallel using a batch script set up and 
- the number and / or names of files to processed are likely to change.

- this can either be:

    - started from a batch file before Revit Batch Processor is started
    - started as a pre - process script in the first session of Revit Batch Processor 


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

# sample description
# this sample shows how to build a task list file (used as a pre-process) using FileList module

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r"C:\temp"
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r"C:\temp"

import clr
import System

# set path to library and this script
import sys

sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import libraries
from duHast.UI import file_list as fl

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import script_util

# -------------
# my code here:
# -------------


# output messages either to batch processor (debug = False) or console (debug = True)
def output(message=""):
    """
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    """
    if not DEBUG:
        script_util.Output(str(message))
    else:
        print(message)


# -------------
# main:
# -------------

# directory containing files
ROOT_PATH = r""
# store task files lists here
ROOT_PATH_EXPORT = r""
# number of task list files to be written out
TASK_FILES_NUMBER = 1

# get file data
output("Writing file Data.... start")
try:
    RESULT = fl.write_file_list(
        ROOT_PATH, ".rvt", ROOT_PATH_EXPORT, TASK_FILES_NUMBER, fl.get_revit_files
    )
    output(RESULT.message)
    output("Writing file Data.... status: [{}]".format(RESULT.status))
except Exception as e:
    output("Failed to write file list with exception: {}".format(e))
