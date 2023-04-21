'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Combines reports.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to combine multiple report files written per Revit project file into a single file per report type.


This script can be used when: 

- multiple sessions of Revit Batch Processor are to be run in parallel using a batch script set up
- single session of Revit Batch Processor is used


- this can either be:

    - started from a batch file after Revit Batch Processor is finished
    - started as a post - process script in the Revit Batch Processor UI

'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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

# sample description
# this sample shows how to merge a number of text report files created on the same day with the same suffix (from the same report)
# into a single report file for ease of reviewing

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import common library
from duHast.Utilities import date_stamps as dateStamp
from duHast.Utilities import files_combine as fileCombine

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import script_util

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''
    
    if not DEBUG:
        script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

# combine data
output('Writing summary Data.... start')

# get the current date stamp to be used as a file prefix for the combined report
DATE_STAMP = dateStamp.get_file_date_stamp()

# combine report files based on:
fileCombine.combine_files(
    ROOT_PATH,  # - part report location
    DATE_STAMP, # - part report prefix ( same date stamp as current)
    '_CAD',     # - part report file name suffix
    '.txt',     # - part report file extension
    DATE_STAMP + '_CAD_Links_summary.txt'   # - combined report file name in same location as part reports
)
# notify users
output('Writing summary Data.... finished: {}_CAD_Links_summary.txt'.format(DATE_STAMP))

# combine report files based on:
fileCombine.combine_files(
    ROOT_PATH,      # - part report location
    DATE_STAMP,     # - part report prefix ( same date stamp as current)
    '_RVT',         # - part report file name suffix
    '.txt',         # - part report file extension
    DATE_STAMP + '_RVT_Links_summary.txt'   # - combined report file name in same location as part reports
)
# notify user
output('Writing summary Data.... finished: {}_RVT_Links_summary.txt'.format(DATE_STAMP))
