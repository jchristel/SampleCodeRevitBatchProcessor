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
