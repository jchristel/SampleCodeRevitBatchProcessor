'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains post reporting functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- check if anything was reported: do any temp files exists?
- if so:
    - Combine temp report files per family into single report file per report type.
    - Delete temp folders
    - Copy report files and log files into analysis folders.
    - Check Family base data report file for:

        - missing families 
        - host families which contain missing families
        - circular references in family nesting

    - Check log files for:

        - any exceptions which may have occured during processing
- if not:
    - dont do anything...


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

# --------------------------
# Imports
# --------------------------
import clr
import System
import os
import sys


import settings as utilData # sets up all commonly used variables and path locations!
import Post_Output as pOut # output to console function
import Post_FamilyDataCleanUp as pCleanUp # clean up functions

# import common library
import Utility as util
import BatchProcessorLogUtils as logutils
import RevitFamilyBaseDataAnalysisCircularReferencing as famDataCircularCheck
import RevitFamilyBaseDataAnalysisMissingFamilies as famDataMissingFams
import RevitFamilyBaseDataUtils as rFamBaseDataUtils
import RevitFamilyReportUtils as rFamRepUtils

# -------------
# my code here:
# -------------

# list containing file name prefixes and the associoated combined report file names
FILE_DATA_TO_COMBINE = [
    ['Category', 'FamilyCategoriesCombinedReport' + utilData.REPORT_FILE_EXTENSION],
    ['SharedParameter', 'FamilySharedParametersCombinedReport' + utilData.REPORT_FILE_EXTENSION],
    ['LinePattern', 'FamilyLinePatternsCombinedReport' + utilData.REPORT_FILE_EXTENSION],
    ['FamilyBase', 'FamilyBaseDataCombinedReport' + utilData.REPORT_FILE_EXTENSION],
    ['Warnings', 'FamilyWarningsCombinedReport' + utilData.REPORT_FILE_EXTENSION]
]

# looking for message indicating one of the data processors failed
CUSTOM_EXCEPTION_MESSAGES_TO_BE_FLAGGED = [
    'status: False'
    ]



# ------------------------------------------- log file processing -------------------------------------------

def _writeReprocess(data, fileName, header = []):
    '''
    Writes out a CSV file which can be used to re-process families which did not process correctly the first time around.

    :param data: _description_
    :type data: [[str]]
    :param header: _description_
    :type header: [str]
    '''

    if (len(data) > 0):
        # show user any issues
        for d in data:
            pOut.Output('::'.join(d))
        # write data out to file
        util.writeReportDataAsCSV(
            utilData.OUTPUT_FOLDER + '\\' + fileName, # report full file name
            header, # empty header by default
            data, 
            writeType = 'w'
        )
    else:
        pOut.Output(fileName + ': Result did not contain any data to be written to file.')
        # write out empty re-process file
        util.writeReportDataAsCSV( 
            utilData.OUTPUT_FOLDER + '\\' + fileName, 
            header,
            []
        )
        pOut.Output(fileName + ': Empty file written.')

def ProcessLogFiles():
    '''
    Checks log files for any warnings or exceptions and writes out a report file containing any issues in format\
        filepath exception description
    '''

    # process logs
    processingResults_ = logutils.ProcessLogFiles(
        utilData.LOG_MARKER_DIRECTORY,
        CUSTOM_EXCEPTION_MESSAGES_TO_BE_FLAGGED
        )

    pOut.Output('LogResults.... status: ' + str(processingResults_.status))

    # write any files with exceptions out to file:
    if(processingResults_.result != None):
        # re-format output data
        dataToFile = []
        dataToProcessFile = []
        for data in processingResults_.result:
            row = [data[0], data[2]]
            dataToFile.append(row)
            # re - process files
            rowProcessData = [data[0]]
            dataToProcessFile.append(rowProcessData)
        processingResults_.result = dataToFile
        _UserOutAndLogFile(processingResults_, utilData.FILE_NAME_EXCEPTIONS_REPORT)

        # write out second family list as CSV (files which failed to process for a reason and need to be processed again)
        _writeReprocess(dataToProcessFile, utilData.FILE_NAME_SECOND_PROCESS_FAMILIES_REPORT)

# ------------------------------------------- copy log files -------------------------------------------

def _copyLog(logfiles, targetFolder, extension):
    '''
    Copies log files and renames them

    :param logfiles: A list of fully qualified log file path.
    :type logfiles: [str]
    :param targetFolder: The destionation directory to where files will be copied to.
    :type targetFolder: str
    :param extension: File extension in format: '.extension'
    :type extension: str
    '''

    flag = True
    # copy logfiles over
    logCounter = 1
    for logfilePath in logfiles:
        # get the file name of the path
        logFileName = 'BatchRvt_' + util.PadSingleDigitNumericString(str(logCounter)) + extension
        # build the destination file path
        newLogFilePath = targetFolder + '\\' + logFileName
        # copy the log file
        flagCopy = util.CopyFile(logfilePath, newLogFilePath)
        flag = flag and flagCopy
        logCounter = logCounter  + 1
    return flag

def CopyLogFiles(targetFolder):
    '''
    Copies log files (.log and .txt) from local app data folder to provided folder and renames them:\
        'BatchRvt_' + counter
    '''

    flagCopyLogs = True
    if(util.DirectoryExists(utilData.LOG_MARKER_DIRECTORY)):
        if(util.DirectoryExists(targetFolder)):
            # get log marker files
            markerfileIds = logutils.GetCurrentSessionIds(
                utilData.LOG_MARKER_DIRECTORY,
                False #keep markers for processing later on
                )
            # check if any ids where retrieved
            if (len(markerfileIds) > 0):
                # copy .log files
                logfiles = logutils.GetLogFiles(markerfileIds)
                copyLog =  _copyLog(logfiles, targetFolder, '.log')
                # copy .txt files
                logfiles = logutils.GetLogTxtFiles(markerfileIds)
                copyTextLog = _copyLog(logfiles, targetFolder, '.txt')
                # combine copy results
                flagCopyLogs = copyLog and copyTextLog
            else:
                pOut.Output('\nNo log marker files found in ' + utilData.LOG_MARKER_DIRECTORY)
                flagCopyLogs = False
        else:
            pOut.Output ('\nLog file destination directory does not exist: ' + targetFolder)
            flagCopyLogs = False
    else:
        pOut.Output ('\nLog marker directory does not exist: ' + utilData.LOG_MARKER_DIRECTORY)
        flagCopyLogs = False
    return flagCopyLogs