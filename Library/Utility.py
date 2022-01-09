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
import codecs
import csv

# default file stamp date format
FILE_DATE_STAMP_YY_MM_DD = '%y_%m_%d'
FILE_DATE_STAMP_YYMMDD_SPACE = '%y %m %d'
FILE_DATE_STAMP_YYYYMMDD_SPACE = '%Y %m %d'
FILE_DATE_STAMP_YYYY_MM_DD = '%Y_%m_%d'
FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC = '%Y_%m_%d_%H_%M_%S'

# time stamp using colons
TIME_STAMP_HHMMSEC_COLON = '%H:%M:%S'

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

def GetLocalAppDataPath():
    """return directory path to local app data folder"""
    return os.environ['LOCALAPPDATA']

# ---------------------------------------------------------------------------------------------------------------------------------

# folderPath        folder path from which to get files
# filePrefix        file starts with this value
# fileSuffix        file name end on suffix
# fileExtension     file extension in format '.ext'
def GetFilesSingleFolder(folderPath, filePrefix, fileSuffix, fileExtension):
    '''Get files from a folder filtered by file prefix, file suffix, file extension '''
    fileList = glob.glob(folderPath + '\\' + filePrefix + '*' + fileSuffix + fileExtension)
    return fileList

# folderPath      root directory to start fiel search in
# filePrefix        file starts with this value
# fileSuffix        file name end on suffix
# fileExtension     file extension in format '.ext'
def GetFilesFromDirectoryWalkerWithFilters(folderPath, filePrefix, fileSuffix, fileExtension):
    """returns all files in directory and nested subdirectories where file name matches filters value"""
    filesFound = []
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            fileName = GetFileNameWithoutExt(name)
            if (name.endswith(fileExtension) and fileName.startswith(filePrefix) and fileName.endswith(fileSuffix)):
                filesFound.append(root + '\\' + name)
    return filesFound

# folderPath              root directory to start fiel search in
# fileExtension     file must have this extension
def GetFilesFromDirectoryWalkerWithFiltersSimple(folderPath, fileExtension):
    """returns all files in directory and nested subdirectories where file name matches filters value"""
    filesFound = []
    filesFound = GetFilesFromDirectoryWalkerWithFilters(folderPath, '', '', fileExtension)
    return filesFound

# folderPath        root directory to start fiel search in
# filePrefix        file starts with this value
# fileSuffix        file name end on suffix
# fileExtension     file extension in format '.ext'
# includeSubDirs    whether to include subdirectories in search
def FilesAsDictionary(folderPath, filePrefix, fileSuffix, fileExtension, includeSubDirs = False):
    """returns all files in directory and nested subdirectories where file name contains filter value as dictionary: 
    - key file name without extension
    - values: list of directories where this file occures (based on file name only!)
    use case: check for duplicaes by file name only"""
    filesFound = []
    # set up a dictionary
    fileDic = {}
    try:
        if(includeSubDirs):
            filesFound = GetFilesFromDirectoryWalkerWithFilters(folderPath, '', '', '.rfa')
        else:
            filesFound = GetFilesSingleFolder(folderPath, '', '', '.rfa')
    except Exception:
        return fileDic
    
    # populate dictionary
    for filePath in filesFound:
        fileName = GetFileNameWithoutExt(filePath)
        if(fileName in fileDic):
            fileDic[fileName].append(filePath)
        else:
            fileDic[fileName] = [filePath]
    return fileDic

# files are combined based on this search pattern: folderPath + '\\' + filePreffix + '*' + fileSuffix + fileExtension
# prefix is usually the time stamp in format  '%y_%m_%d'
def CombineFiles(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt', fileGetter = GetFilesSingleFolder):
    """used to combine report files into one file (assumes all files have the same number of columns)"""
    file_list = fileGetter (folderPath, filePrefix, fileSuffix, fileExtension)
    with open(folderPath + '\\' + outPutFileName, 'w' ) as result:
        fileCounter = 0
        for file_ in file_list:
            lineCounter = 0
            fp = open( file_, 'r' )
            lines = fp.readlines()
            fp.close()
            for line in lines:
                # ensure header from first file is copied over
                if(fileCounter == 0 and lineCounter == 0 or lineCounter != 0):
                    result.write( line )
                lineCounter += 1
            
            fileCounter += 1

# files are combined based on this search pattern: folderPath + '\\' + filePreffix + '*' + fileSuffix + fileExtension
# prefix is usually the time stamp in format  '%y_%m_%d'
def AppendToSingleFiles(sourceFile, appendFile):
    """used to append one file to another, assumes same number of headers)"""
    flag = True
    try:
        # read file to append into memory...hopefully will never get in GB range in terms of file size
        fp = codecs.open(appendFile,'r',encoding='utf-8')
        lines=fp.readlines()
        fp.close()
        with codecs.open(sourceFile, 'a', encoding='utf-8') as f:
            for line in lines:
                f.write( line )
    except Exception:
        flag = False
    return flag

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
# header:           list of column headers, provide empty list if not required!
# data:             list of list of strings representing row data
# writeType         w: new file, a: append to existing file...
def writeReportData(fileName, header, data, writeType = 'w'):
    with codecs.open(fileName, writeType, encoding='utf-8') as f:
        # check if header is required
        if(len(header) > 0):
            print('\t'.join(header + ['\n']))
            f.write('\t'.join(header + ['\n']))
        # check if data is required
        if(len(data) > 0):
            for d in data:
                f.write('\t'.join(d + ['\n']))
        f.close()

# ---------------------------------------------------------------------------------------------------------------------------------

# file extension in format '.txt'
def GetFiles(folderPath, fileExtension='.rvt'):
    """returns a list of files from a given folder with a given file extension"""
    file_list = glob.glob(folderPath + '\\*' + fileExtension)
    return file_list

# file extension in format '.txt'
# file filter is in 'something*'
def GetFilesWithFilter(folderPath, fileExtension='.rvt', filter = '*'):
    """returns a list of files from a given folder with a given file extension and a file name filter"""
    file_list = glob.glob(folderPath + '\\' + filter + fileExtension)
    return file_list

# path      root directory to start fiel search in
# filter    file name must contain filter value
def GetFilesFromDirectoryWalker(path, filter):
    """returns all files in directory and nested subdirectories where file name contains filter value"""
    filesFound = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if (name.Contains(filter)) :
                filesFound.append(root + '\\' + name)
    return filesFound

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
    except Exception as e:
        print('An exception occured when attempting to delete a directory: ' + str(e))
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
    except Exception as e:
        # just in case the folder does exist (created by another instance at almost the same time)
        if('[Errno 17]' not in str(e)):
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

# filePathCSV      fully qualified file path to tab separated file
def ReadCSVfile(filepathCSV):
    """read a csv files into a list of rows"""
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

# filePath      fully qualified file path to tab separated file
def ReadTabSeparatedFile(filePath):
    """read a tab delimited files into a list of rows"""
    rowList = []
    try:
        with codecs.open (filePath,'r',encoding='utf-8') as f:
            reader = csv.reader(f, dialect='excel-tab')
            for row in reader: # each row is a list
                rowList.append(row)
            f.close()
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

# returns True if valueTwo starts with valueOne
def ConTwoStartWithOne (valueOne, valueTwo):
    if (valueTwo.startswith(valueOne)):
        return True
    else:
        return False

# returns True if valueTwo does not starts with valueOne
def ConTwoDoesNotStartWithOne (valueOne, valueTwo):
    if (valueTwo.startswith(valueOne)):
        return False
    else:
        return True

# ---------------------------------------------------------------------------------------------------------------------------------

# text      string to be converted all lower case and then to be converted to a boolean ( 'true' = True, 'false' = False)
def ParsStringToBool(text):
    '''converts a string lower case and then to bool. Will throw an exception if it fails to do so'''
    if(text.lower() == 'true'):
        return True
    elif (text.lower() == 'false'):
        return False
    else:
         raise Exception('String cant be converted to bool')

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

# helper method for index of item in list
def IndexOf(list, item):
    try:
        return list.index(item)
    except:
        return -1

# sourcelist    list to remove items from
# removeList    list containing items to be removed from source
def RemoveItemsFromList(sourceList, removeIdsList):
    """helper removes ids from a source list"""
    try:
        for item in removeIdsList:
            sourceList.remove(item)
    except:
        pass
    return sourceList