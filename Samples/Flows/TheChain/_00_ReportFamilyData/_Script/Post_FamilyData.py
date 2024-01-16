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


# ------------------------------------------- user feed back and report to disk -------------------------------------------

def _writeEmptyReportFile(fileName, header = []):
    '''
    Writes an empty report file.

    :param fileName: The report file name excluding path.
    :type fileName: str
    :param header: header, defaults to []
    :type header: list, optional
    '''

    pOut.Output(fileName + ': Writing empty report file.')
    dataToFile = []
    util.writeReportDataAsCSV(
        utilData.OUTPUT_FOLDER + '\\' + fileName, # report full file name
        header, # empty header by default
        dataToFile, 
        writeType = 'w')

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
            pOut.Output('::'.join(m))
        # write data out to file
        util.writeReportDataAsCSV(
            utilData.OUTPUT_FOLDER + '\\' + fileName, # report full file name
            header, # empty header 
            processingResults.result, 
            writeType = 'w'
        )
    else:
        pOut.Output(fileName + ': Result did not contain any data to be written to file.')
        _writeEmptyReportFile(fileName, header)

# ------------------------------------------- clean up -------------------------------------------
def CheckTempReportsExist():
    '''
    Check whether temp report folder exists (in case of an empty report run)

    :return: True if any temp report files exists, otherwise False.
    :rtype: bool
    '''

    flag = False
    for toCombine in FILE_DATA_TO_COMBINE:
        files = util.GetFilesFromDirectoryWalkerWithFilters(
            utilData.OUTPUT_FOLDER, 
            '', 
            toCombine[0], 
            utilData.REPORT_FILE_EXTENSION
        )
        if (len(files) > 0):
            flag = True
            break
    return flag

def CombineTempReports():
    '''
    Combines temporary report files into into single report files.
    '''

    # combine all by file repoorts into one per porocessor
    for toCombine in FILE_DATA_TO_COMBINE:
        pOut.Output('Combining '+ toCombine[0] + ' report files.')
        # combine files
        util.CombineFiles(
            utilData.OUTPUT_FOLDER, 
            '' , 
            toCombine[0], 
            utilData.REPORT_FILE_EXTENSION,
            toCombine[1], 
            util.GetFilesFromDirectoryWalkerWithFilters
        )

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
        _writeEmptyReportFile(fileName, header)

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

# ------------------------------------------- Report analysis -------------------------------------------

def CheckCircularReferences():
    '''
    Checks for any circular nesting references in family files processed by analyzing the \
        FamilyBaseDataCombinedReport.csv report file.
    '''
    try:
        # check for circular references in families
        checkCircularRefResult = famDataCircularCheck.CheckFamiliesHaveCircularReferences(
            utilData.OUTPUT_FOLDER + '\\' + 'FamilyBaseDataCombinedReport' + utilData.REPORT_FILE_EXTENSION
            )

        pOut.Output('Circular referencing check.... status: ' + str(checkCircularRefResult.status))
        if(checkCircularRefResult.result != None):
            # re-format output data
            dataToFile = []
            for data in checkCircularRefResult.result:
                row = [
                    data.filePath, 
                    '[' + ','.join(data.parent) + ']', 
                    '[' + ','.join(data.child) + ']'
                    ]
                dataToFile.append(row)
            checkCircularRefResult.result = dataToFile
        _UserOutAndLogFile(checkCircularRefResult, utilData.FILE_NAME_CIRCULAR_REFERENCE_REPORT)
    except Exception as e:
        pOut.Output('Failed circular reference check with exception: ' + str(e))
        _writeEmptyReportFile(utilData.FILE_NAME_CIRCULAR_REFERENCE_REPORT)

def CheckMissingFamilies():
    '''
    Checks for nested families which are not processed as root families and therefore are not in the library or missing.
    Uses the FamilyBaseDataCombinedReport.csv report file
    '''

    dataFilePath = utilData.OUTPUT_FOLDER + '\\' + 'FamilyBaseDataCombinedReport' + utilData.REPORT_FILE_EXTENSION
    
    try:
        checkMissingFams = famDataMissingFams.CheckFamiliesMissingFromLibrary(dataFilePath)

        pOut.Output('Missing families from library check.... status: ' + str(checkMissingFams.status))
        #initialise missing families list
        missingFams = []
        if(len(checkMissingFams.result) > 0):
            # duplicate data for later (to find the host families)
            missingFams = list(checkMissingFams.result)
        
            # re-format output data for missing family text file
            dataToFile = []
            for data in checkMissingFams.result:
                try:
                    # missing fams data
                    row = [
                        data.name,
                        data.category
                    ]
                    dataToFile.append(row)
                except  Exception as e:
                    pOut.Output('an exception occured when processing missing family data prior to be written to file: ' + str(e))
            checkMissingFams.result = dataToFile
            _UserOutAndLogFile(checkMissingFams, utilData.FILE_NAME_MISSING_FAMILIES_REPORT)
        else:
            # write empty report files
            dataToFile = []
            _writeReprocess(dataToFile, utilData.FILE_NAME_MISSING_FAMILIES_REPORT)
    
        # get host families of those missing families
        missingFamiliesHostFamilies = famDataMissingFams.FindMissingFamiliesDirectHostFamilies (
            dataFilePath, 
            missingFams
        )
        if(len(missingFamiliesHostFamilies.result) > 0):
            # re-format output data
            dataToFile = []
            for data in missingFamiliesHostFamilies.result:
                try:
                    row = [
                        data.filePath,
                        data.name,
                        data.category
                    ]
                    dataToFile.append(row)
                except  Exception as e:
                    pOut.Output('an exception occured when processing missing family data prior to be written to file: ' + str(e))
            _writeReprocess(dataToFile, utilData.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT )
        else:
            # write empty report files
            dataToFile = []
            _writeReprocess(dataToFile, utilData.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT )
    except Exception as e:
        pOut.Output('Failed missing family check with exception: ' + str(e))
        _writeEmptyReportFile(utilData.FILE_NAME_MISSING_FAMILIES_REPORT)
        _writeEmptyReportFile(utilData.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT)


# ------------------------------------------- Analysis folder and copy files -------------------------------------------

def SetUpdatedFolderInAnalysis():
    '''
    Sets up a dated folder in the Analysis directory

    :return: True if folder was created succesfully, otherwise False
    :rtype: bool
    '''

    flag =  util.CreateFolder(
        utilData.ANALYSIS_FOLDER, 
        util.GetFolderDateStamp()
        )
    folderName = utilData.ANALYSIS_FOLDER + '\\' + util.GetFolderDateStamp()
    return flag, folderName

def CopyResultsIntoAnalysis(targetFolder):
    '''
    Copies all text files in Output folder to target folder

    :param targetFolder: Fully qualified  directory path
    :type targetFolder: str
    :return: true if all files copied succesfully, otherwise False
    :rtype: bool
    '''
    
    flagCopy = True
    # copy all text files from output
    files = util.GetFilesWithFilter(utilData.OUTPUT_FOLDER , utilData.REPORT_FILE_EXTENSION)
    pOut.Output( 'Found result files: ' + str(len(files)))
    for f in files:
        # get the file name of the path
        fileName = os.path.basename(f)
        # build the destination file path
        newfilePath = os.path.join(targetFolder, fileName)
        # copy the log file
        flagCopyFile = util.CopyFile(f, newfilePath)
        pOut.Output('Copied file: ' + util.GetFileNameWithoutExt(f) + ' to: ' + newfilePath + ' [' + str(flagCopyFile) + ']')
        flagCopy = flagCopy and flagCopyFile
    return flagCopy

# -------------------------------------------combining report files -------------------------------------------

def _CombineReportFilesCheck():
    '''
    Check whether a marker file exists, which specifies: where existing report file are located to be used to be merged wwith current report.

    :return: True if marker file exists, otherwise False.  The root directory path to where previous report files are located
    :rtype: bool, string, string
    '''

    combineReports = False
    previousReportsDirectory = ''

    # build marker file path
    markerFilePath = utilData.INPUT_DIRECTORY + '\\' + utilData.FILE_NAME_MARKER_MERGE_FAMILY_DATA
    # check if file exists in input location
    if(util.FileExist(markerFilePath)):
        # read file
        rows = util.ReadTabSeparatedFile(markerFilePath)
        # should be at least one row...
        if (len(rows) >= 1):
            for row in rows:
                if (len(row)>=1):
                    # assign family out file path
                    if(util.DirectoryExists(row[0])):
                        previousReportsDirectory = row[0]
                        combineReports = True
                # get out after parsing first row
                break
    return combineReports , previousReportsDirectory

def CombineCurrentWithPreviousReportFiles(previousReportRootDirectory):
    '''
    Loops over reports listed in global variable and attempts to find a match for the report in the current output directory\
        and the passt in directory.
    It will combine both reports as follows:

        - duplicate family data: data from the current data set will be used
        - any unique data from either report will be added to the combined report

    :param previousReportRootDirectory: Directory path containing previous (older) reports.
    :type previousReportRootDirectory: str
    '''

    # loop over report names and find matches in both location
    for toCombine in FILE_DATA_TO_COMBINE:
        # set default values
        currentReportFile = ''
        previousReportFile  = ''
        if(util.FileExist(utilData.OUTPUT_FOLDER + '\\' + toCombine[1])):
            currentReportFile = utilData.OUTPUT_FOLDER + '\\' + toCombine[1]
            pOut.Output('Found match for current report file: ' + currentReportFile)
        else:
            pOut.Output('No match found for: ' + toCombine[1] + ' current output folder.')

        if(util.FileExist(previousReportRootDirectory + '\\' + toCombine[1])):
            previousReportFile = previousReportRootDirectory + '\\' + toCombine[1]
            pOut.Output('Found match for previous report file: ' + previousReportFile)
        else:
            pOut.Output('No match found for: ' + toCombine[1] + ' previous report folder.')

        if(currentReportFile != '' and previousReportFile != ''):
            # put try catch around this in case report files are empty...
            try:
                # update report
                updatedReportRowsStatus = rFamRepUtils.CombineReports(previousReportFile, currentReportFile)
                pOut.Output(updatedReportRowsStatus.message)
                updatedReportRows = updatedReportRowsStatus.result
                # write out new report on top of old one
                util.writeReportDataAsCSV(
                    currentReportFile, 
                    '', 
                    updatedReportRows)
                pOut.Output ('Wrote updated report to: ' + currentReportFile)
            except Exception as e:
                pOut.Output("Failed to combine reports: [" + currentReportFile + "]\t[" + previousReportFile + '] with exception: ' + str(e))
        else:
            pOut.Output('Failed to find two report files for report: ' + toCombine[1] + ' Nothing was combined.')

# -------------
# main:
# -------------
# check whether any families where processed (possible that in follow up mode nothing was needed to be processed!)
if(CheckTempReportsExist()):
    # set up a folder with the current date in the analysis folder to store some data
    datedAnalysisFolderCreated_, datedAnalysisDatedDirectoryPath_ = SetUpdatedFolderInAnalysis()
    # combine temporary, by family, reports
    CombineTempReports()
    # delete the working by session id directories
    pCleanUp.DeleteWorkingDirectories()

    # check whether report files need to be combined / merged with previous  (older) report files before progressing
    combineReportFiles, previousReportRootDirectory = _CombineReportFilesCheck()
    if(combineReportFiles):
        CombineCurrentWithPreviousReportFiles(previousReportRootDirectory)

    # check processed files for any circular references
    CheckCircularReferences()
    # check processed files for any missing families
    CheckMissingFamilies()

    # copy log files first if data folder was created 
    # log file markers will be removed once the log files are processed
    # therefore those log files need to be copied first
    if(datedAnalysisFolderCreated_):
        flagCopyLogOne_ = CopyLogFiles(datedAnalysisDatedDirectoryPath_)
        pOut.Output('Copied all log files to Analysis dated folder with status: ' + str(flagCopyLogOne_))
        flagCopyLogTwo_ = CopyLogFiles(utilData.ANALYSIS_CURRENT_FOLDER)
        pOut.Output('Copied all log files to Analysis current folder with status: ' + str(flagCopyLogTwo_))
    
    # check log files for any exceptions or warnings ( do this last since log marker files are required to copy logs for \
    # analysis in powerBi)
    # this will also remove any log file marker files
    ProcessLogFiles()

    # copy report files
    if(datedAnalysisFolderCreated_):
        flagCopyResultOne_ = CopyResultsIntoAnalysis(datedAnalysisDatedDirectoryPath_)
        pOut.Output('Copied all report files to Analysis dated folder with status: ' + str(flagCopyResultOne_))
        flagCopyResultTwo_ = CopyResultsIntoAnalysis(utilData.ANALYSIS_CURRENT_FOLDER)
        pOut.Output('Copied all report files to Analysis current folder with status: ' + str(flagCopyResultTwo_))
else:
    pOut.Output('No temp report files where found, indicating no families where processed.')
# delete any files in Input directory
pCleanUp.DeleteFileInInputDir()