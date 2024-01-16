'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains post saving out missing families functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Write all path of families saved out into a file used in a follow up report flow.
- Copy report files and log files into analysis folders.
- Check log files for:

    - any exceptions which may have occured during processing


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


import utilDataBVN as utilData # sets up all commonly used variables and path locations!
# import common library
import Utility as util
import BatchProcessorLogUtils as logutils
import FileList as fl

# -------------
# my code here:
# -------------

# output messages
def Output(message = ''):
    '''
    Print message to console.

    :param message: The message, defaults to ''
    :type message: str, optional
    '''

    # 08/09/2022 19:09:19 :
    timestamp = util.GetDateStamp('%d/%m/%Y %H_%M_%S : ')
    print (timestamp + message)


# looking for message indicating one of the data processors failed
CUSTOM_EXCEPTION_MESSAGES_TO_BE_FLAGGED = [
    'status: False'
    ]

# ------------------------------------------- user feed back and report to disk -------------------------------------------

def _UserOutAndLogFile(processingResults, fileName, header = []):
    '''
    Show user feed back and write to report file

    :param processingResults: Result class instance.

        - result.status. bool. (not used)
        - result.message string (not used)
        - result.result A list of lists of string containing the data to be written to file.

    :type processingResults: class:`.Result`
    '''

    if(processingResults.result != None):
        # show user any issues
        for m in processingResults.result:
            Output('::'.join(m))
        # write data out to file
        util.writeReportDataAsCSV(
            utilData.OUTPUT_FOLDER + '\\' + fileName, # report full file name
            header, # empty header 
            processingResults.result, 
            writeType = 'w'
        )
    else:
        Output('Result did not contain any data to be written to file.')

# ------------------------------------------- clean up -------------------------------------------

def DeleteFileInInputDir():
    '''
    Deletes any files in the input directory.
    '''
    files = util.GetFilesSingleFolder(utilData.INPUT_DIRECTORY, '', '', utilData.REPORT_FILE_EXTENSION)
    if(len(files) > 0):
        for f in files:
            flagDelete = util.FileDelete(f)
            Output('Deleted marker file: ' + f + ' [' + str(flagDelete) +']')
    else:
        Output('Input directory did not contain any files.')


# ------------------------------------------- log file processing -------------------------------------------

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

    Output('LogResults.... status: ' + str(processingResults_.status))

    # write any files with exceptions out to file:
    if(processingResults_.result != None):
        # re-format output data
        dataToFile = []
        for data in processingResults_.result:
            row = [data[0], data[2]]
            dataToFile.append(row)
        processingResults_.result = dataToFile
        _UserOutAndLogFile(processingResults_, utilData.FILE_NAME_EXCEPTIONS_REPORT)

# -------------
# main:
# -------------

# check log files for any exceptions or warnings
ProcessLogFiles()

# get the folder in which families have been saved to:
saveOutMissingFamilies, baseDataReportFilePath, familyOutRootDirectory = utilData.SaveOutMissingFamiliesCheck()

# collect data and write to processing file
if(saveOutMissingFamilies):
    # get all families located in combined out folder
    files = fl.GetRevitFilesForProcessingSimpleInclSubDirs(utilData.OUTPUT_FOLDER_COMBINED_FAMILIES, '.rfa')
    
    if(len(files) > 0):
        # needs to be a list of lists
        data = []
        # get data from file items
        for fileObject in files:
            # append as a list
            data.append([fileObject.name])

        # write data to file
        util.writeReportDataAsCSV(
            utilData.OUTPUT_FOLDER + '\\' + utilData.FILE_NAME_SECOND_PROCESS_FAMILIES_REPORT, # report full file name
            [], # empty header by default
            data, 
            writeType = 'w'
        )
    else:
        Output('No families located in output folder!')
else:
    Output('Failed to read data required to analyse missing families!')

# clean up
DeleteFileInInputDir()