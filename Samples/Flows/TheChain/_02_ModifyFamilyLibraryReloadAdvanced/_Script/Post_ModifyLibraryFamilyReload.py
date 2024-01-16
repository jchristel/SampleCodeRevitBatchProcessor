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
# import log utils
import BatchProcessorLogUtils as logUtils
import Utility as util

# -------------
# my code here:
# -------------

FILE_DATA_TO_COMBINE = [
    ['_marker_', 'CopyFilesTaskList' + utilR.REPORT_FILE_EXTENSION]
]

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    print (message)

# keepFiles     list of files not to delete (fully qualified file path)
def DeleteTempFiles(keepFiles):
    """
    deletes all temp files
    """
    flagDeleteAll = True
    filesMatching = util.GetFilesWithFilter(utilR.WORKING_DIRECTORY, '.temp', '*' + '_marker_')
    for f in filesMatching:
        if(f not in keepFiles):
            flagDelete = util.FileDelete(f)
            Output('Deleting ' + util.GetFileNameWithoutExt(f) + ' status: ' + str(flagDelete))
            flagDeleteAll = flagDeleteAll & flagDelete
    return flagDeleteAll

def CombineDataFiles():
    """
    combines varies report files into single text file
    """
    for toCombine in FILE_DATA_TO_COMBINE:
        Output('Combining '+ toCombine[0] + ' report files.')
        # combine files
        util.CombineFiles(
            utilR.WORKING_DIRECTORY, 
            '' , 
            toCombine[0], 
            '.temp',
            toCombine[1]
    )

def MoveFiles():
    """
    move family files back to original location
    this is a work around to the fact that I'm unable to save family files after processing!
    """
    fileCopyTaskList = util.ReadCSVfile(utilR.WORKING_DIRECTORY + '\\' + FILE_DATA_TO_COMBINE[0][1])
    rowCounter = 0
    for copyRow in fileCopyTaskList:
        if(rowCounter != 0):
            flagCopy = util.CopyFile(copyRow[0], copyRow[1])
            Output('Copied file: ' + copyRow[0] + ' status: '+ str(flagCopy))
            if(flagCopy):
                flagDelete = util.FileDelete(copyRow[0])
                Output('Deleted file: ' + copyRow[0] + ' status: '+ str(flagDelete))
        rowCounter = rowCounter + 1 

# -------------
# main:
# -------------

# combine marker files (copy instructions)
Output('Combining report files:')
CombineDataFiles()

# delete marker files
flagDeleteAll = DeleteTempFiles([])
Output('Deleted all temp files: [' + str(flagDeleteAll) + ']')

# move family files back to source location
MoveFiles()

# copied list of files changed
flagCopyChangedFiles = util.CopyFile(
    utilR.WORKING_DIRECTORY + '\\' + FILE_DATA_TO_COMBINE[0][1], 
    utilR.WORKING_DIRECTORY + '\\' + utilR.CHANGED_FAMILY_PART_REPORT_PREFIX + util.GetFileDateStamp(util.FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC) + utilR.REPORT_FILE_EXTENSION
)
Output('Created changed families task file: [' + str(flagCopyChangedFiles) + ']')

# delete task file
flagDeleteTask = util.FileDelete(utilR.WORKING_DIRECTORY + '\\' + FILE_DATA_TO_COMBINE[0][1])
Output('Deleted move families task file: [' + str(flagDeleteTask) + ']')

processingResults_ = logUtils.ProcessLogFiles(utilR.LOG_MARKER_DIRECTORY)
Output('LogResults.... status: ' + str(processingResults_.status))
Output('LogResults.... message: ' + str(processingResults_.message))