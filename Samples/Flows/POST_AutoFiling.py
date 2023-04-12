'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automated filing.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to file incoming models into as given folder structure and keep a record of date and revision of files received.

The given folder structure includes a NavisWorks federated model folder where all .nwc files are stored. In order to replace existing files in that location, incoming files are stripped of their revision information contained within the file name.


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

# this sample shows how to do some automated filing of (incoming) Revit and NWC files after a process has run
# steps included are:
# copy and rename, i.e. remove revision data, NWC files into given locations to assist in updating federated NavisWorks models
# move Revit, NWC, IFC files into an automatically created dated folder in a given INCOMING location [INCOMING location can be nominated per file to allow for separate locations per consultant for instance]
# updated an incoming files register with date and revision of files received. (Date is current date, revision will need to be included in the file name). The register is a CSV text file which in turn can be linked into MS Excel

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import libraries
from duHast.Utilities import FilesGet as fileGet
from duHast.Utilities import FilesIO as fileIO
from duHast.Utilities import DirectoryIO as dirIO
from duHast.Utilities import DateStamps as dateStamp
from duHast.Utilities import FilesCSV as fileCSV

import os.path
from os import path
import shutil
from System.IO import Path

# to read csv files
import csv
clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import script_util

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not debug_:
        script_util.Output(str(message))
    else:
        print (message)

def _getNWCFileName(currentFileName):
    '''
    Drop revision and other things of current NWC file name so the previous version in a federated model can be replaced.

    :param currentFileName: _description_
    :type currentFileName: str
    :return: _description_
    :rtype: _type_
    '''

    returnValue = currentFileName
    foundMatch = False
    try:
        for nwcNameStartsWidth, newNWCFileName in nwcFileNaming_:
            if (currentFileName.startswith(nwcNameStartsWidth)):
                foundMatch = True
                returnValue = newNWCFileName
                break
    except Exception as e:
        Output('Failed to find match: ' + str(e))
        returnValue = currentFileName
    if(foundMatch):
        Output('Found match for:  ' + currentFileName + ' to: ' + returnValue)
    else:
        Output('Found no match for:  ' + currentFileName )
    return returnValue

def _copyNWCFiles():
    '''
    Copy nwc files to Navisworks. federated model, location

    :return: True if all files where copied successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    fileFilter = '*.nwc'
    # check whether any files match the filter
    for nwcFileNameStart, nwcTargetFolder in defaultNWCLocations_:
        files =  fileGet.GetFilesWithFilter (sourcePath_, fileFilter, nwcFileNameStart + '*')
        if(files != None and len(files) > 0):
            Output('Copying nwc Files...' + str(len(files)))
            for file in files:
                try:
                    # extract file name only
                    fileName = Path.GetFileName(file)
                    src = sourcePath_ + '\\' + fileName
                    destinationFileName = _getNWCFileName(fileName)
                    dst = nwcTargetFolder + '\\' + destinationFileName
                    copy_status = fileIO.CopyFile(src,dst)
                    status = status & copy_status
                    Output('Copied file from ' + src + ' to ' + dst)
                except Exception:
                    Output('Failed to copy file from ' + src + ' to ' + dst)
                    status = False
        else:
            Output('No nwc files matching filter ' + fileFilter + ' in source location: ' + sourcePath_)
    return status

def CreateTargetFolder(targetLocation, folderName):
    '''
    Set up dated model incoming folder.

    :param targetLocation: Directory in which to create a new folder
    :type targetLocation: str
    :param folderName: New folder name.
    :type folderName: str
    :return: True if folder was created successfully, otherwise False
    :rtype: bool
    '''

    returnFolderName = folderName
    # check if folder exists
    flag = False
    if(dirIO.DirectoryExists(targetLocation + '\\' + folderName) == False):
        gotFolder = False
        n = 1
        # create new folder (stop at 10 attempts)
        while (gotFolder == False and n < 10):
            if (dirIO.DirectoryExists(targetLocation + '\\' + folderName + '(' + str(n) + ')') == False):
                flag = dirIO.CreateFolder(targetLocation, folderName + '(' + str(n) + ')')
                returnFolderName = folderName + '(' + str(n) + ')'
                # ignore the flag coming back in to avoid infinite loops
                gotFolder = True
            n += 1
    return flag, returnFolderName

def MoveFiles(fileData):
    '''
    Move files into incoming folder(s)

    :param fileData: _description_
    :type fileData: _type_
    :return: True if all files where moved successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    # get the date stamp
    folderName = dateStamp.GetFolderDateStamp() + str('_Models')
    for fileFilter, targetLocation in fileData:
        # check if target root path still exists
        if(path.exists(targetLocation)):
            # check whether any files match the filter
            files = fileGet.GetFilesWithFilter(sourcePath_, '.*', fileFilter + '*')
            # copy any *.nwc files into the right folders first
            _copyNWCFiles()
            # move files into file in location
            if(files != None and len(files) > 0):
                flagGotFolder = dirIO.CreateTargetFolder(targetLocation, folderName)
                if (flagGotFolder):
                    Output('Moving Files...' + str(len(files)))
                    # move files
                    for file in files:
                        try:
                            # extract file name only
                            fileName = Path.GetFileName(file)
                            src = sourcePath_ + '\\' + fileName
                            dst = targetLocation + '\\' + folderName + '\\' + fileName
                            shutil.move(src,dst)
                            status = status & True
                            Output('Moved file from ' + src + ' to ' + dst)
                        except Exception:
                            Output('Failed to move file from ' + src + ' to ' + dst)
                            status = False
                else:
                    Output('Failed to create target folder ' + targetLocation )
            else:
                Output('No files matching filter ' + fileFilter + ' in source location: ' + sourcePath_)
        else:
            Output(targetLocation + ' no longer exists!')
            status = False
    return status

# --------------------- saving files received list ---------------------------------

def SaveFilesReceivedList():
    '''
    Saves out a file where each row contains the dates a file was received last.

    Note:
    This reads the previously written received file and only overwrites the date of files a match was found for/

    :return: True if everything went well, otherwise False.
    :rtype: bool
    '''

    status = True
    # get the current received file and read rows into 2D array
    currentIssueList = _readCurrentFile()
    # get current data mapping array
    allFilesMappingTable = _buildMappingTable()
    # data to be written back
    newIssueList = []
    for rowCounter in range(0, len(allFilesMappingTable)):
        newIssueRow = []
        columnCounter = 0
        for files in allFilesMappingTable[rowCounter]:
            for fileExtension,nameFilter in files:
                # get files and check for match
                dateValue, revision = _getMatch(fileExtension, nameFilter)
                if (dateValue == '-'):
                    # use the value from currentIssueList (if there is one...)
                    if(currentIssueList is not None and len(currentIssueList)>0):
                        try:
                            newIssueRow.append(currentIssueList[rowCounter + outPutRowHeadersCount_][columnCounter + outPutColumnHeadersCount_])
                            columnCounter += 1
                            newIssueRow.append(currentIssueList[rowCounter + outPutRowHeadersCount_][columnCounter + outPutColumnHeadersCount_])
                        except Exception:
                            # current file issue list has less columns the new one...add default
                            newIssueRow.append('-')# date
                            columnCounter += 1
                            newIssueRow.append('-')# revision
                    else:
                        # no file issue list was found...add default value
                        newIssueRow.append('-')# date
                        columnCounter += 1
                        newIssueRow.append('-')# revision
                else:
                    newIssueRow.append(dateValue)
                    columnCounter += 1
                    newIssueRow.append(revision)
                # increase column counter
                columnCounter += 1
        newIssueList.append(newIssueRow)
    # write array back to file
    paddedData = _addHeadersToData(newIssueList)
    status = _writeNewData(paddedData)
    return status

def _addHeadersToData(newIssueList):
    '''
    Adds row and column headers to files received data

    :param newIssueList: _description_
    :type newIssueList: _type_
    :return: _description_
    :rtype: _type_
    '''
    updatedData = []
    # check if row headers are required
    if (outPutRowHeadersCount_ > 0):
        # row counter
        rowIndex = 0
        for dataRow in newIssueList:
            columnIndex = 0
            for rowHeader in outPutRowHeaders_:
                dataRow.insert(columnIndex, rowHeader[rowIndex])
                columnIndex  += 1
            updatedData.append(dataRow)
            rowIndex += 1
    else:
        for dataRow in newIssueList:
            updatedData.append(dataRow)
    # check if column headers are required
    if (outPutColumnHeadersCount_ > 0):
        rowIndex = 0
        for columnHeader in outPutColumnHeaders_:
            # Insert blank columns for row headers
            if (outPutRowHeadersCount_ > 0):
                for x in range(0,outPutRowHeadersCount_):
                    columnHeader.insert(0,'-')
            # need to allow for row headers!!
            updatedData.insert(rowIndex, columnHeader)
            rowIndex += 1
    return updatedData

def _getMatch(fileExtension, nameFilter):
    '''
    Find file match with filters provided
    File extension in format '.rvt'

    :param fileExtension: _description_
    :type fileExtension: _type_
    :param nameFilter: _description_
    :type nameFilter: _type_
    :return: _description_
    :rtype: str (default='-'), str(default='-')
    '''

    returnValue = '-'
    revision = '-'
    # check whether valid name filter otherwise return '-'
    if(nameFilter is not ''):
        files = fileGet.GetFilesWithFilter(sourcePath_, fileExtension, nameFilter + '*')
        if (files is not None and len(files) > 0):
            # got a match
            returnValue = dateStamp.GetFolderDateStamp()
            # get the revision
            revision = _getRevision(files[0])
    return returnValue, revision

def _getRevision(filename):
    '''
    Get the revision information from the file name.

    :param filename: the file name
    :type filename: str
    :return: the file revision, if exists, otherwise '-'
    :rtype: str (default='-')
    '''

    # default value in case no revision information is included in file name
    returnValue = '-'
    for revStart in revisionSeparatorsStart_:
        # check if file contains any of these
        startIndex = filename.find(revStart)
        if ( startIndex > 0):
            endIndex = startIndex + 1
            # look for end of revision
            for revEnd in revisionSeparatorsEnd_:
                endIndex = filename.find(revEnd)
                if (endIndex > 0):
                    break
            returnValue = filename[startIndex + 1:endIndex]
            break
    return returnValue

def _buildMappingTable():
    '''
    Builds a mapping array from global nwc and rvt all files received lists
    This defines the rows and column of the incoming file tracker
    in this sample its: NWC, Revision of NWC, Revit, Revision of Revit

    :return: _description_
    :rtype: _type_
    '''

    mappingArray = []
    # loop over lists and build mapping table as required
    rvtList = _rebuildList(allFilesReceivedRVT_)
    nwcList = _rebuildList(allFilesReceivedNWC_)
    # loop over array and build mapping 2d array:
    # row discipline, column building in format ([filter (rvt), filename], [filter(nwc), filename])
    for x in range(0, len(nwcList)):
        mappingRow = []
        for y in range(0,len(nwcList[x])):
            mappingRow.append([nwcList[x][y], rvtList[x][y]])
        mappingArray.append(mappingRow)
    return mappingArray

def _rebuildList(receivedFiles):
    '''
    Loops over list of received files and builds a list of pairs of [file filter, file name]

    :param receivedFiles: _description_
    :type receivedFiles: _type_
    :return: _description_
    :rtype: _type_
    '''

    outputList = []
    for x in receivedFiles:
        dummy = []
        for fileTypeFilter,fileNameFilters in x:
            for fileNameFilter in fileNameFilters:
                dummy.append([fileTypeFilter, fileNameFilter])
            outputList.append(dummy)
    return outputList

def _readCurrentFile():
    '''
    Read the current issue date file located in SourcePath location with name
    'issueList.csv'

    :return: _description_
    :rtype: _type_
    '''

    referenceList = []
    try:
        referenceList = fileCSV.ReadCSVfile(currentIssueDatafileName_)
    except Exception as e:
        Output('Failed to open current model issue list with exception: ' + str(e))
    return referenceList

def _writeNewData(data):
    '''
    Write new revision data out to file.

    :param data: _description_
    :type data: _type_
    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    try:
        fileCSV.writeReportDataAsCSV(currentIssueDatafileName_,[],data)
    except Exception as e:
        status = False
        Output('Failed to write data file!' + currentIssueDatafileName_+ ' with exception: ' + str(e))
    return status

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'
# directory containing incoming files
sourcePath_ = r'C:\temp'

# list of locations where incoming files are to be saved,
# format is:
# [Name starts with, fully qualified directory path]
# this script will create a dated folder in the location provided and move files into it
defaultModelInLocations_ = [
    ['Structure File Name', r'C:\temp\Structure\In'],
    ['Fire Dry File Name', r'C:\temp\Fire\In'],
    ['Fire Wet File Name', r'C:\temp\Fire\In'],
    ['Electrical File Name', r'C:\temp\Electrical\In'],
    ['Security File Name', r'C:\temp\Security\In'],
    ['Mechanical File Name', r'C:\temp\Mechanical\In'],
    ['Steel Fabricator Zone File Name', r'C:\temp\Structure\In'],
    ['Hydraulic File Name', r'C:\temp\Hydraulic\In']
]


# list of locations where incoming NavisWorks files are to be saved
defaultNWCLocations_ = [
    ['Structure File Name', r'C:\temp\NavisWorks'],
    ['Fire Dry File Name', r'C:\temp\NavisWorks'],
    ['Fire Wet File Name', r'C:\temp\NavisWorks'],
    ['Common File Name', r'C:\temp\NavisWorks']# all other consultants
]

# list containing the default file names:
# [[Navis file name before move, Navis file name after move]]
nwcFileNaming_ = [
    ['StructureFileBeforeName', 'StructureFileAfterName'],
    ['FireDryBeforeName', 'FireDryAfterName'],
    ['FireWetBeforeName', 'FireWetAfterName'],
    ['ElectricalFileBeforeName', 'ElectricalFileAfterName'],
    ['SecurityFileBeforeName', 'SecurityFileAfterName'],
    ['MechanicalFileBeforeName', 'MechanicalFileAfterName'],
    ['SteelFileBeforeName', 'SteelFileAfterName'],
    ['HydraulicFileBeforeName', 'HydraulicFileAfterName']
]

# nwc files list to build files received array 
nwcSTNorth_ = [['.nwc',['StructureFileBeforeName']]]
nwcSTSteelOne_ = [['.nwc',['SteelFileBeforeName']]]
nwcHY_ = [['.nwc',['HydraulicFileBeforeName']]]
nwcFPW_ = [['.nwc',['FireWetBeforeName']]]
nwcFPD_ = [['.nwc',['FireDryBeforeName']]]
nwcME_ = [['.nwc',['MechanicalFileBeforeName']]]
nwcEL_ = [['.nwc',['ElectricalFileBeforeName']]]
nwcSE_ = [['.nwc',['SecurityFileBeforeName']]]

# rvt files list to build files received array 
rvtSTNorth_ = [['.rvt',['StructureFileBeforeName']]]
rvtSTSteelOne_ = [['.rvt',['SteelFileBeforeName']]]
rvtHY_ = [['.rvt',['HydraulicFileBeforeName']]]
rvtFPW_ = [['.rvt',['FireWetBeforeName']]]
rvtFPD_ = [['.rvt',['FireDryBeforeName']]]
rvtME_ = [['.rvt',['MechanicalFileBeforeName']]]
rvtEL_ = [['.rvt',['ElectricalFileBeforeName']]]
rvtSE_ = [['.rvt',['SecurityFileBeforeName']]]

# build full files received baseline 2D array

Output('Building files received mapping table.... start')
allFilesReceivedNWC_ = [nwcSTNorth_, nwcSTSteelOne_,  nwcHY_,  nwcFPW_, nwcFPD_, nwcME_,  nwcEL_,  nwcSE_]
allFilesReceivedRVT_ = [rvtSTNorth_, rvtSTSteelOne_,  rvtHY_, rvtFPW_, rvtFPD_, rvtME_, rvtEL_, rvtSE_]

currentIssueDatafileName_ = sourcePath_ + r'\issueList.csv'
revisionSeparatorsStart_ = ['[', '(']
revisionSeparatorsEnd_ = [']', ')']

# output headers
outPutColumnHeaders_ = [
    ['NWC','REVISION','REVIT','REVISION']
]
outPutRowHeaders_ = [
    ['structure', 'structure - steel zone one','hydraulic','fire - wet','fire - dry','mechanical','electrical','security']
]

# these are used to correctly calculate the columns and rows containing data when reading existing data file
outPutColumnHeadersCount_ = len(outPutColumnHeaders_)
outPutRowHeadersCount_ = len(outPutRowHeaders_)

# save files received list
resultSaveFileStats_ = SaveFilesReceivedList()
Output('Writing files received mapping table.... status ' + str(resultSaveFileStats_))

# move files
Output('Moving files .... start')
result_ = MoveFiles(defaultModelInLocations_)
Output('Moving files .... status: ' + str(result_))