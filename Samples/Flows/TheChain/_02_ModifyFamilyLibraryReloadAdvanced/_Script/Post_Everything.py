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

# this sample processes log files and displays results indicating whether any revit files failed to process with a
# time out warning
# exception which caused the process to be aborted


# flag whether this runs in debug or not
debug_ = False

# --------------------------
# default file path locations
# --------------------------

import clr
import System

#clr.AddReference('System.Core')
#clr.ImportExtensions(System.Linq)

import utilReloadBVN as utilR # sets up all commonly used variables and path locations!
import Utility as util

# -------------
# my code here:
# -------------

FILE_DATA_TO_COMBINE = [
    ['ChangedFamilies', 'ChangedFilesTaskList' + utilR.REPORT_FILE_EXTENSION]
]

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    print (message)


# -------------
# main:
# -------------

# get part changed families report files
filesToCombine = util.GetFilesSingleFolder(
    utilR.WORKING_DIRECTORY, 
    utilR.CHANGED_FAMILY_PART_REPORT_PREFIX, 
    '', 
    '.csv'
)
# check whether anything came back
if (len(filesToCombine) > 0):
    Output ('Found part changed family report files: ' + str(len(filesToCombine)))
    rowsOverall = []
    # combine files
    for f in filesToCombine:
        rows = util.ReadCSVfile(f)
        Output('read rows from file: [' + str(len(rows) - 1) + '] ' + f)
        # ignore header row
        for i in range(1,len(rows)):
            # read second column into list and append to overall list to be written to file
            # second column contains the file path in library location
            # first column is file path in temp (\Output) location
            rowsOverall.append([rows[i][1]])
    # write data to file
    try:
        combinedChangedFamilyReportPath = utilR.WORKING_DIRECTORY + '\\' + utilR.CHANGED_FAMILY_REPORT_FILE_NAME + utilR.REPORT_FILE_EXTENSION
        util.writeReportDataAsCSV (
            combinedChangedFamilyReportPath, 
            '', 
            rowsOverall)
        Output ('Successfully wrote combined changed family report to: ' + combinedChangedFamilyReportPath)
        # delete single files
        for f in filesToCombine:
            flagDelete = util.FileDelete(f)
            Output('Deleted part file: [' + str(flagDelete) + '] ' + f)
    except Exception as e:
        Output('Failed to write combined family change list to file with exception: ' + str(e))
else:
    Output ('No changed families part files found!')

