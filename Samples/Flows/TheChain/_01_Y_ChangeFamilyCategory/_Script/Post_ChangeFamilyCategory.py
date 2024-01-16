'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a post - processing module combining temp files, cleaning up temp files, moving 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Combining temp files:
    - marker files helping to copy family files back to their origin
    - changed family marker files to be used in reload action

- Moving family files back to their origin location.

'''

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

import utilModifyBVN as utilR # sets up all commonly used variables and path locations!
# import log utils
import BatchProcessorLogUtils as logutils
import Utility as util

# -------------
# my code here:
# -------------

# temp files to combine
FILE_DATA_TO_COMBINE = [
    ['_marker_', 'CopyFilesTaskList' + utilR.REPORT_FILE_EXTENSION],
    ['_changed_', 'ChangedFilesTaskList' + utilR.REPORT_FILE_EXTENSION]
]

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    print (message)

def DeleteTempFiles(keepFiles):
    '''
    Deletes all temp file.

    :param keepFiles: List of files not to delete (fully qualified file path)
    :type keepFiles: [str]

    :return: True if all files got deleted successfully, otherwise False.
    :rtype: bool
    '''

    flagDeleteAll = True
    for toDelete in FILE_DATA_TO_COMBINE:
        filesMatching = util.GetFilesWithFilter(utilR.WORKING_DIRECTORY, '.temp', '*' + toDelete[0])
        for f in filesMatching:
            if(f not in keepFiles):
                flagDelete = util.FileDelete(f)
                Output('Deleting ' + util.GetFileNameWithoutExt(f) + ' status: ' + str(flagDelete))
                flagDeleteAll = flagDeleteAll & flagDelete
    return flagDeleteAll


def DeleteTaskListFiles(directoryPath):
    '''
    Deletes any task list files which may be present

    :param directoryPath: Fully qualified directory path where task list files are located.
    :type directoryPath: str

    :return: True if all files where deleted or none existed in the first place, otherwise False
    :rtype: bool
    '''

    flagOverAll = True
    taskListFiles = util.GetFilesWithFilter(
        directoryPath,
        utilR.REPORT_FILE_EXTENSION
        )
    Output ('Looking for task files in: ' + directoryPath)
    if(len(taskListFiles) > 0):
        for f in taskListFiles:
            flag = util.FileDelete(f)
            Output ('Deleted task file: ' + f + ' status: [' + str(flag) +']')
            flagOverAll = flagOverAll and flag
    else:
        Output ('No task files found to be deleted.')
    return flagOverAll

def CombineDataFiles():
    '''
    Combines varies report files into single text file.

    Files are filter based on FILE_DATA_TO_COMBINE list.
    '''

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
    '''
    Move family files back to original location.
    This is a work around to the fact that I'm unable to save family files after processing!
    '''
    
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

def CreateFollowUpReportDataFile():
    '''
    writes out changed file  list in format for follow up reporting

    :return: true if successfully written list to file, otherwise False
    :rtype: bool
    '''
    rows = util.ReadCSVfile(utilR.WORKING_DIRECTORY + '\\' + FILE_DATA_TO_COMBINE[1][1])
    dataFile=[]
    for i in range (1,len(rows)):
        data = rows[i][1]
        dataFile.append([data])
    
    # write out file list without header
    header = []
    
    try:
        # write data
        util.writeReportData(
            utilR.WORKING_DIRECTORY + '\\' + utilR.FOLLOW_UP_REPORT_FILE_NAME, 
            header, 
            dataFile, 
            writeType = 'w')
        return True
    except Exception:
        return False

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

# delete move task file
flagDeleteMoveTask = util.FileDelete(utilR.WORKING_DIRECTORY + '\\' + FILE_DATA_TO_COMBINE[0][1])
Output('Deleted move families task file: [' + str(flagDeleteMoveTask) + ']')

# delete any task list files
flagDeleteMoveTask = DeleteTaskListFiles(utilR.FAMILY_CHANGE_DIRECTIVE_DIRECTORY)
Output('Deleted families task file: [' + str(flagDeleteMoveTask) + ']')

# create follow up list file
flagFollowUp = CreateFollowUpReportDataFile()
if(flagFollowUp):
    Output('Created follow up list file: [{}]'.format(utilR.WORKING_DIRECTORY + '\\' + utilR.FOLLOW_UP_REPORT_FILE_NAME))
else:
    Output('Failed to created follow up list file: [{}]'.format(utilR.WORKING_DIRECTORY + '\\' + utilR.FOLLOW_UP_REPORT_FILE_NAME))

processingResults_ = logutils.ProcessLogFiles(utilR.LOG_MARKER_DIRECTORY)
Output('LogResults.... status: ' + str(processingResults_.status))
Output('LogResults.... message: ' + str(processingResults_.message))