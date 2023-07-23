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
