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

import clr
import System
from System.IO import Path
import glob
import datetime
import os
import shutil
import os.path
from os import path
import csv

# default file stamp date format
FILE_DATE_STAMP_YY_MM_DD = '%y_%m_%d'
FILE_DATE_STAMP_YYYY_MM_DD = '%Y_%m_%d'
FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC = '%Y_%m_%d_%H_%M_%S'

# get the date stamp prefix of report files
def GetFileDateStamp(format = FILE_DATE_STAMP_YY_MM_DD):
    d = datetime.datetime.now()
    return d.strftime(format)

# available fodler date formats
FOLDER_DATE_STAMP_YYMMDD = '%y%m%d'
FOLDER_DATE_STAMP_YYYYMMDD = '%Y%m%d'

# get the date stamp prefix of report files
def GetFolderDateStamp(format = FOLDER_DATE_STAMP_YYYYMMDD):
    d = datetime.datetime.now()
    return d.strftime(format)

# get the date stamp in provided format
def GetDateStamp(format):
    d = datetime.datetime.now()
    return d.strftime(format)

# ---------------------------------------------------------------------------------------------------------------------------------

# used to combine report files into one file (assumes all files have the same number of columns)
# files are combined based on this search pattern: folderPath + '\\' + filePreffix + '*' + fileSuffix + fileExtension
# prefix is usually the time stamp in format  '%y_%m_%d'
def CombineFiles(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt'):
    file_list = glob.glob(folderPath + '\\' + filePrefix + '*' + fileSuffix + fileExtension)
    print(str(len(file_list)))
    with open(folderPath + '\\' + outPutFileName, 'w' ) as result:
        fileCounter = 0
        for file_ in file_list:
            lineCounter = 0
            for line in open( file_, 'r' ):
                # ensure header from first file is copied over
                if(fileCounter == 0 and lineCounter == 0 or lineCounter != 0):
                    result.write( line )
                lineCounter += 1
            fileCounter += 1

# used to combine report files into one file, files may have different number / named columns
# files are combined based on this search pattern: folderPath + '\\' + filePreffix + '*' + fileSuffix + fileExtension
# prefix is usually the time stamp in format  '%y_%m_%d'
def CombineFilesHeaderIndependent(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt'):
    file_list = glob.glob(folderPath + '\\' + filePrefix + '*' + fileSuffix + fileExtension)
    # build list of unique headers
    headers = GetUniqueHeaders(file_list)
    # open output file
    with open(folderPath + '\\' + outPutFileName, 'w' ) as result:
        fileCounter = 0
        for file_ in file_list:
            lineCounter = 0
            columnMapper = []
            for line in open( file_, 'r' ):
                line = line.rstrip('\n')
                # read the headers in file
                if (lineCounter == 0):
                    headersInFile = line.split('\t')
                    # match up unique headers with headers from this file
                    for uh in headers:
                        if (uh in headersInFile):
                            columnMapper.append(headersInFile.index(uh))
                        else:
                            columnMapper.append(-1)
                # ensure unique header is written
                if(fileCounter == 0 and lineCounter == 0):
                    headers.append('\n')
                    result.write('\t'.join(headers))
                elif(lineCounter != 0):
                    # write out padded rows
                    rowdata = line.split('\t')
                    #print(rowdata)
                    paddedRow = []
                    for cm in columnMapper:
                        if(cm == -1):
                            # this column does not exist in this file
                            paddedRow.append('N/A')
                        elif (cm > len(rowdata)):
                            # less columns in file than mapper index (shouldnt happen??)
                            paddedRow.append('index out of bounds')
                        else:
                            paddedRow.append(rowdata[cm])
                    paddedRow.append('\n')
                    result.write('\t'.join(paddedRow))
                lineCounter += 1
            fileCounter += 1

# returns a unique list of headers retrieved from text files
# assumes: 
#   - first row is header row
#   - headers are separated by <tab> character
# returns alphabeticaly sorted list of strings
def GetUniqueHeaders(files):
    headersInAllFiles = []
    for f in files:
        data = GetFirstRowInFile(f)
        if (data is not None):
            rowSplit = data.split('\t')
            headersInAllFiles.append(rowSplit)
    headersUnique = []
    for headerByfile in headersInAllFiles:
        for header in headerByfile:
            if(header not in headersUnique):
                headersUnique.append(header)
    return sorted(headersUnique)

# reads the first line of a text file and returns it as a single string
def GetFirstRowInFile(filePath):
    row = ''
    try:
        with open(filePath) as f:
            row = f.readline().strip()
    except Exception:
        row = None
    return row

# method writing out report information
# fileName:         fully qualified file path
# header:           list of column headers
# data:             list of lists representing row data
def writeReportData(fileName, header, data):
    f = open(fileName, 'w')
    f.write('\t'.join(header + ['\n']))
    for d in data:
        f.write('\t'.join(d + ['\n']))
    f.close()

# ---------------------------------------------------------------------------------------------------------------------------------

# returns a list of files from a given folder with a given file extension
# file extension in format '.txt'
def GetFiles(folderPath, fileExtension='.rvt'):
    file_list = glob.glob(folderPath + '\\*' + fileExtension)
    return file_list

# returns a list of files from a given folder with a given file extension and a file name filter
# file extension in format '.txt'
# file filter is in 'something*'
def GetFilesWithFilter(folderPath, fileExtension='.rvt', filter = '*'):
    file_list = glob.glob(folderPath + '\\' + filter + fileExtension)
    return file_list

# number of file size options
FILE_SIZE_IN_KB = 1024
FILE_SIZE_IN_MB = 1024*1024
FILE_SIZE_IN_GB = 1024*1024*1024

# get the file size in given units (default is MB)
# filePath  fully qualified file path
# unit      unit of file size to be returned, default is MB
def GetFileSize(filePath, unit = FILE_SIZE_IN_MB):
    # default value if anything goes wrong
    size = -1
    try:
        size = os.path.getsize(filePath)
        # convert units
        size = size / unit
    except:
        pass
    return size

# ---------------------------------------------------------------------------------------------------------------------------------

# checks whether a file exists
def FileExist(fullFilePath):
    try:
        value = os.path.exists(fullFilePath)
    except Exception:
        value = False
    return value

# deletes file
def FileDelete(fullFilePath):
    try:
        os.remove(fullFilePath)
        value = True
    except Exception:
        value = False
    return value

# deletes an empty directory
def DirectoryEmptyDelete(fullDirectoryPath):
    try:
        os.rmdir(fullDirectoryPath)
        value = True
    except Exception:
        value = False
    return value

# deletes a directory (even if it contains files)
def DirectoryDelete(fullDirectoryPath):
    try:
        shutil.rmtree(fullDirectoryPath)
        value = True
    except Exception:
        value = False
    return value

# returns the immediate subdirectories of directory
def GetChildDirectories(fullDirectoryPath):
    subfoldersWithPaths = []
    for root, dirs, files in os.walk(fullDirectoryPath):
        for dir in dirs:
            subfoldersWithPaths.append( os.path.join(root, dir) )
        break
    return subfoldersWithPaths

# get directory from file
def GetFolderPathFromFile(filePath):
    try:
        value = os.path.dirname(filePath)
    except Exception:
        value = ''
    return value

# rename a file
def RenameFile(oldName, newName):
    try:
        os.rename(oldName, newName)
        value = True
    except Exception:
        value = False
    return value

# copies a file
def CopyFile(oldName, newName):
    value = True
    try:
        shutil.copy(oldName, newName)
    except Exception:
        value = False
    return value

# set up folder
def CreateFolder(root, folderName):
    dirName = path.join(root,folderName)
    flag = True
    try:
        os.mkdir(dirName)
    except Exception:
        flag = False
    return flag

# checks whether folder exists and if not attempts to create it
def CreateTargetFolder(rootPath, folderName):
    #check if folder exists
    flag = True
    if(path.exists(rootPath + '\\' + folderName) == False):
        #create new folder
        flag = CreateFolder(rootPath, folderName)
    return flag

# returns an time stamped output file name based on the revit file name
# file extension needs to include '.', default is '.txt'
# file suffix will be appended after the name but before the file extension. Default is blank.
def GetOutPutFileName(revitFilePath, fileExtension = '.txt', fileSuffix = ''):
    # get date prefix for file name
    filePrefix = GetFileDateStamp()
    name = Path.GetFileNameWithoutExtension(revitFilePath)
    return filePrefix + '_' + name + fileSuffix + fileExtension

# returns the revit file name without the file extension
def GetFileNameWithoutExt(filePath):
    name = Path.GetFileNameWithoutExtension(filePath)
    return name

# removes '..\..' or '..\' from relative file path supplied by Revit and replaces it with full path derived from Revit document
def ConvertRelativePathToFullPath(relativeFilePath, fullFilePath):
    if( r'..\..' in relativeFilePath):
        two_up = path.abspath(path.join(fullFilePath ,r'..\..'))
        return two_up + relativeFilePath[5:]
    elif('..' in relativeFilePath):
        one_up = path.abspath(path.join(fullFilePath ,'..'))
        return one_up + relativeFilePath[2:]
    else:
        return relativeFilePath

# read a csv files into a list of rows
def ReadCSVfile(filepathCSV):
    rowList = []
    try:
        with open(filepathCSV) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader: # each row is a list
                rowList.append(row)
    except Exception as e:
        print (str(e))
        rowList = []
    return rowList

# ---------------------------------------------------------------------------------------------------------------------------------

# currently known comparisons
# returns True if valueOne does not match valueTwo
def ConDoesNotEqual (valueOne, valueTwo):
    if (valueOne != valueTwo):
        return True
    else:
        return False

# returns True if valueOne does match valueTwo
def ConDoesEqual (valueOne, valueTwo):
    if (valueOne == valueTwo):
        return True
    else:
        return False

# returns True if valueOne starts with valueTwo
def ConOneStartWithTwo (valueOne, valueTwo):
    if (valueOne.startswith(valueTwo)):
        return True
    else:
        return False

# returns True if valueTwo starts with valueTwo
def ConTwoStartWithOne (valueOne, valueTwo):
    if (valueTwo.startswith(valueOne)):
        return True
    else:
        return False

# ---------------------------------------------------------------------------------------------------------------------------------

# default 2 digit padding
PAD_SINGLE_DIGIT_TO_TWO = '%02d'
# three digit padding
PAD_SINGLE_DIGIT_TO_THREE = '%03d'

# pads a single digit integer (past in as a string) with a leading zero (default)
# returns a string
def PadSingleDigitNumericString(numericstring, format = PAD_SINGLE_DIGIT_TO_TWO):
    # attempt to convert string to int first
    try:
        value = int(numericstring)
        return str(format%value)
    except Exception:
        #string was not an integer...
        return numericstring

#encode string as ascii and replaces all non ascii characters
def EncodeAscii (string):
    return string.encode('ascii','replace')

# returns the first value in a list matching condition
# if no value found returns the specificed default value
def GetFirst(iterable, default, condition = lambda x: True):
    return next((x for x in iterable if condition(x)),default)

# converts feet and inches to mm
def ConvertImperialToMetricMM(value):
    return value * 304.8
