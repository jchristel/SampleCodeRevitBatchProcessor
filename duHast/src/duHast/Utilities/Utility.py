'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- file system tasks (copy, create, delete...)
- date stamps (with varies formatting options)
- write data ( text files )

'''
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

#import clr
#import System
#from numpy import empty
from System.IO import Path
import glob
import datetime
import os
import shutil
import os.path
from os import path
import codecs
import csv
import collections

import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

#: default file stamp date format using underscores as delimiter: 21_03_01
FILE_DATE_STAMP_YY_MM_DD = '%y_%m_%d'
#: file stamp date format using spaces as delimiter: 21 03 01
FILE_DATE_STAMP_YYMMDD_SPACE = '%y %m %d'
#: file stamp date format using spaces as delimiter: 2021 03 01
FILE_DATE_STAMP_YYYYMMDD_SPACE = '%Y %m %d'
#: file stamp date format using underscores as delimiter: 2021_03_01
FILE_DATE_STAMP_YYYY_MM_DD = '%Y_%m_%d'
#: file stamp date time format using underscores as delimiter: 2021_03_01_18_59_59
FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC = '%Y_%m_%d_%H_%M_%S'

#: time stamp using colons: 18:59:59
TIME_STAMP_HHMMSEC_COLON = '%H:%M:%S'

def GetFileDateStamp(format = FILE_DATE_STAMP_YY_MM_DD):
    '''
    Returns a date stamp formatted suitable for a file name.

    :param format: The date stamp format, defaults to FILE_DATE_STAMP_YY_MM_DD
    :type format: str, optional
    
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    '''

    d = datetime.datetime.now()
    return d.strftime(format)

#: folder date format: no delimiter 210301
FOLDER_DATE_STAMP_YYMMDD = '%y%m%d'
#: folder date format: no delimiter 20210301
FOLDER_DATE_STAMP_YYYYMMDD = '%Y%m%d'
#: folder date format: no delimiter 2021
FOLDER_DATE_STAMP_YYYY = '%Y'

def GetFolderDateStamp(format = FOLDER_DATE_STAMP_YYYYMMDD):
    '''
    Returns a date stamp formatted suitable for a folder name.

    :param format: The date stamp format, defaults to FOLDER_DATE_STAMP_YYYYMMDD
    :type format: str, optional
    
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    '''

    d = datetime.datetime.now()
    return d.strftime(format)

# get the date stamp in provided format
def GetDateStamp(format):
    '''
    Returns a date stamp formatted using past in format string.

    :param format: The date stamp format
    :type format: str

    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    '''

    d = datetime.datetime.now()
    return d.strftime(format)

def GetLocalAppDataPath():
    '''
    return directory path to local app data folder

    :return: Path to local app data
    :rtype: str
    '''

    return os.environ['LOCALAPPDATA']

def GetCurrentUserName():
    '''
    Returns the current user name

    :return: the user name
    :rtype: str
    '''
    
    return os.environ['USERNAME']

#: ---------------------------------------------------------------------------------------------------------------------------------

def GetFilesSingleFolder(folderPath, filePrefix, fileSuffix, fileExtension):
    '''
    Get files from a folder filtered by file prefix, file suffix, file extension

    :param folderPath: Folder path from which to get files.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value.
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'

    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    '''

    fileList = glob.glob(folderPath + '\\' + filePrefix + '*' + fileSuffix + fileExtension)
    return fileList

def GetFilesFromDirectoryWalkerWithFilters(folderPath, filePrefix, fileSuffix, fileExtension):
    '''
    Returns a list of all files in directory and nested sub directories where file name matches filters value.

    :param folderPath: Root folder path from which to get files.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    
    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    '''

    filesFound = []
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            fileName = GetFileNameWithoutExt(name)
            if (name.endswith(fileExtension) and fileName.startswith(filePrefix) and fileName.endswith(fileSuffix)):
                filesFound.append(root + '\\' + name)
    return filesFound

def GetFilesFromDirectoryWalkerWithFiltersSimple(folderPath, fileExtension):
    '''
    Returns a list of all files in directory and nested subdirectories where file name matches file extension filter value
    
    :param folderPath: Root folder path from which to get files.
    :type folderPath: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'

    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    '''

    filesFound = []
    filesFound = GetFilesFromDirectoryWalkerWithFilters(folderPath, '', '', fileExtension)
    return filesFound

def FilesAsDictionary(folderPath, filePrefix, fileSuffix, fileExtension, includeSubDirs = False):
    '''
    Returns a dictionary of all files in directory and nested subdirectories where file name contains filter value. 
    
    - key file name without extension
    - values: list of directories where this file occurs (based on file name only!)

    Use case: check for duplicates by file name only

    :param folderPath: Root folder path from which to get files.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :param includeSubDirs: If True subdirectories will be included in search for files, defaults to False
    :type includeSubDirs: bool, optional
    
    :return: A dictionary where the key is the file name without the file extension. Value is a list of fully qualified file path to instances of that file.
    :rtype: dictionary
        key: str
        value: lit of str
    '''

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

def CombineFiles(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt', fileGetter = GetFilesSingleFolder):
    '''
    Combines multiple text files into a single new file. Assumes same number of headers (columns) in each files.

    The new file will be saved into the same folder as the original files.

    :param folderPath: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :param outPutFileName: The file name of the combined file, defaults to 'result.txt'
    :type outPutFileName: str, optional
    :param fileGetter: Function returning list of files to be combined, defaults to GetFilesSingleFolder
    :type fileGetter: func(folderPath, filePrefix, fileSuffix, fileExtension), optional
    '''

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

def AppendToSingleFiles(sourceFile, appendFile):
    '''
    Appends one text file to another. Assumes same number of headers (columns) in both files.

    :param sourceFile: The fully qualified file path of the file to which the other file will be appended.
    :type sourceFile: str
    :param appendFile: The fully qualified file path of the file to be appended.
    :type appendFile: str

    :return: If True file was appended without an exception, otherwise False.
    :rtype: bool
    '''

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

def CombineFilesHeaderIndependent(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt'):
    '''
    Used to combine report files into one file, files may have different number / named columns.

    Columns which are unique to some files will have as a value 'N/A' in files where those columns do not exist.

    :param folderPath: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :param outPutFileName: The file name of the combined file, defaults to 'result.txt'
    :type outPutFileName: str, optional
    '''

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
                    # replace any empty strings in header
                    fileName = GetFileNameWithoutExt(file_)
                    emptyHeaderCounter = 0
                    for i in range(len(headersInFile)):
                        # reformat any empty headers to be unique
                        if(headersInFile[i] == ''):
                            headersInFile[i] = fileName +  '.Empty.' + str(emptyHeaderCounter)
                            emptyHeaderCounter = emptyHeaderCounter + 1
                    # match up unique headers with headers from this file
                    # build header mapping
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
                    rowData = line.split('\t')
                    #print(rowData)
                    paddedRow = []
                    for cm in columnMapper:
                        if(cm == -1):
                            # this column does not exist in this file
                            paddedRow.append('N/A')
                        elif (cm > len(rowData)):
                            # less columns in file than mapper index (should'nt happen??)
                            paddedRow.append('index out of bounds')
                        else:
                            paddedRow.append(rowData[cm])
                    paddedRow.append('\n')
                    result.write('\t'.join(paddedRow))
                lineCounter += 1
            fileCounter += 1

def GetUniqueHeaders(files):
    '''
    Gets a list of alphabetically sorted headers retrieved from text files.
    
    Assumes:

    - first row in each file is the header row
    - headers are separated by <tab> character

    :param files: List of file path from which the headers are to be returned.
    :type files: list of str
    
    :return: List of headers.
    :rtype: list of str
    '''

    headersInAllFiles = {}
    for f in files:
        data = GetFirstRowInFile(f)
        if (data is not None):
            rowSplit = data.split('\t')
            headersInAllFiles[GetFileNameWithoutExt(f)] = rowSplit
    headersUnique = []
    for headerByFile in headersInAllFiles:
        emptyHeaderCounter = 0
        for header in headersInAllFiles[headerByFile]:
            # reformat any empty headers to be unique
            if(header == ''):
                header = headerByFile +  '.Empty.' + str(emptyHeaderCounter)
                emptyHeaderCounter = emptyHeaderCounter + 1
            if(header not in headersUnique):
                headersUnique.append(header)
    return sorted(headersUnique)

def writeReportData(fileName, header, data, writeType = 'w'):
    '''
    Function writing out report information.

    :param fileName: The reports fully qualified file path.
    :type fileName: str
    :param header: list of column headers
    :type header: list of str
    :param data: list of list of strings representing row data
    :type data: [[str,str,..]]
    :param writeType: Flag indicating whether existing report file is to be overwritten 'w' or appended to 'a', defaults to 'w'
    :type writeType: str, optional
    '''

    with codecs.open(fileName, writeType, encoding='utf-8') as f:
        # check if header is required
        if(len(header) > 0):
            f.write('\t'.join(header + ['\n']))
        # check if data is required
        if(len(data) > 0):
            for d in data:
                if (len(d) > 1):
                    f.write('\t'.join(d + ['\n']))
                elif(len(d) == 1):
                    f.write(d[0] + '\n')
        f.close()

def writeReportDataAsCSV (fileName, header, data, writeType = 'w'):
    '''
    Function writing out report information as CSV file.

    :param fileName: The reports fully qualified file path.
    :type fileName: str
    :param header: list of column headers
    :type header: list of str
    :param data: list of list of strings representing row data
    :type data: [[str,str,..]]
    :param writeType: Flag indicating whether existing report file is to be overwritten 'w' or appended to 'a', defaults to 'w'
    :type writeType: str, optional
    '''

    # open the file in the write mode
    with codecs.open(fileName, writeType, encoding='utf-8') as f:
        # create the csv writer
        writer = csv.writer(f)
        # check header
        if(len(header) > 0):
            writer.writerow(header)
        if(len(data) > 0):
            for d in data:
                # write a row to the csv file
                writer.writerow(d)
        f.close()

# ---------------------------------------------------------------------------------------------------------------------------------

def GetFiles(folderPath, fileExtension='.rvt'):
    '''
    Gets a list of files from a given folder with a given file extension

    :param folderPath: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folderPath: str
    :param fileExtension: Filter: File needs to have this file extension, defaults to '.rvt'
    :type fileExtension: str, optional
    
    :return: List of file path
    :rtype: list of str
    '''
    
    file_list = glob.glob(folderPath + '\\*' + fileExtension)
    return file_list

def GetFilesWithFilter(folderPath, fileExtension='.rvt', filter = '*'):
    '''
    Gets a list of files from a given folder with a given file extension and a matching a file name filter.

    :param folderPath: Folder path from which to get files.
    :type folderPath: str
    :param fileExtension: Filter: File needs to have this file extension, defaults to '.rvt'
    :type fileExtension: str, optional
    :param filter: File name filter ('something*'), defaults to '*'
    :type filter: str, optional
    
    :return: List of file path
    :rtype: list of str
    '''

    file_list = glob.glob(folderPath + '\\' + filter + fileExtension)
    return file_list

def GetFilesFromDirectoryWalker(path, filter):
    '''
    Gets all files in directory and nested subdirectories where file name contains filter value.

    :param path: Folder path from which to get files.
    :type path: str
    :param filter: File name filter ('something*')
    :type filter: str

    :return: List of file path
    :rtype: list of str
    '''

    filesFound = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if (name.Contains(filter)) :
                filesFound.append(root + '\\' + name)
    return filesFound

#: file size in KB conversion
FILE_SIZE_IN_KB = 1024
#: file size in MB conversion
FILE_SIZE_IN_MB = 1024*1024
#: file size in GB conversion
FILE_SIZE_IN_GB = 1024*1024*1024

def GetFileSize(filePath, unit = FILE_SIZE_IN_MB):
    '''
    Get the file size in given units (default is MB)

    :param filePath: Fully qualified file path
    :type filePath: str
    :param unit: the file size unit, defaults to FILE_SIZE_IN_MB
    :type unit: int

    :return: The file size.
    :rtype: float
    '''

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

def FileExist(fullFilePath):
    '''
    Checks whether a file exists

    :param fullFilePath: Fully qualified file path
    :type fullFilePath: str
    
    :return: True file exists, otherwise False
    :rtype: bool
    '''

    try:
        value = os.path.exists(fullFilePath)
    except Exception:
        value = False
    return value

def FileDelete(fullFilePath):
    try:
        os.remove(fullFilePath)
        value = True
    except Exception:
        value = False
    return value

def DirectoryEmptyDelete(fullDirectoryPath):
    '''
    Deletes an empty directory

    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    
    :return: True directory deleted, otherwise False
    :rtype: bool
    '''

    try:
        os.rmdir(fullDirectoryPath)
        value = True
    except Exception:
        value = False
    return value

def DirectoryDelete(fullDirectoryPath):
    '''
    Deletes a directory (even if it contains files)

    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    
    :return: True directory deleted, otherwise False
    :rtype: bool
    '''

    try:
        shutil.rmtree(fullDirectoryPath)
        value = True
    except Exception as e:
        print('An exception occurred when attempting to delete a directory: ' + str(e))
        value = False
    return value

def GetChildDirectories(fullDirectoryPath):
    '''
    Returns the immediate subdirectories of directory

    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    
    :return: any sub directories, empty list if none exist
    :rtype: list of str
    '''

    subFoldersWithPaths = []
    for root, dirs, files in os.walk(fullDirectoryPath):
        for dir in dirs:
            subFoldersWithPaths.append( os.path.join(root, dir) )
        break
    return subFoldersWithPaths

def GetParentDirectory(fullDirectoryPath):
    '''
    Returns the parent directory of directory, or empty string if invalid directory

    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    
    :return: parent directory, or empty string
    :rtype: str
    '''

    parentDir = ''
    try:
        parentDir = os.path.dirname(fullDirectoryPath)
    except Exception:
        pass
    return parentDir


# get directory from file
def GetFolderPathFromFile(filePath):
    '''
    Extracts directory from file path.

    :param filePath: A fully qualified file path.
    :type filePath: str
    :return: If no exception occurs : A fully qualified directory path,else an empty string.
    :rtype: str
    '''
    try:
        value = os.path.dirname(filePath)
    except Exception:
        value = ''
    return value

def RenameFile(oldName, newName):
    '''
    Renames a file.

    :param oldName: Fully qualified file path to file to be renamed.
    :type oldName: str
    :param newName: Fully qualified new file name.
    :type newName: str
    
    :return: True file renamed, otherwise False
    :rtype: bool
    '''

    try:
        os.rename(oldName, newName)
        value = True
    except Exception:
        value = False
    return value

def CopyFile(oldName, newName):
    '''
    Copies a file

    :param oldName: Fully qualified file path to file to be copied.
    :type oldName: str
    :param newName: Fully qualified path to new file location and name.
    :type newName: str
    
    :return: True file copied, otherwise False
    :rtype: bool
    '''

    value = True
    try:
        shutil.copy(oldName, newName)
    except Exception:
        value = False
    return value

# set up folder
def CreateFolder(root, folderName):
    '''
    Create a folder.

    :param root: Directory path in which the new folder is to be created
    :type root: str
    :param folderName: New folder name.
    :type folderName: str
    
    :return: True if folder is created, otherwise False
    :rtype: bool
    '''

    dirName = path.join(root,folderName)
    flag = True
    try:
        os.mkdir(dirName)
    except Exception as e:
        # just in case the folder does exist (created by another instance at almost the same time)
        if('[Errno 17]' not in str(e)):
            flag = False
    return flag

def CreateTargetFolder(rootPath, folderName):
    '''
    Create a folder.

    Checks whether folder exists and if not attempts to create it.

    :param root: Directory path in which the new folder is to be created
    :type root: str
    :param folderName: New folder name.
    :type folderName: str

    :return: True if folder is created, otherwise False
    :rtype: bool
    '''

    #check if folder exists
    flag = True
    if(path.exists(rootPath + '\\' + folderName) == False):
        #create new folder
        flag = CreateFolder(rootPath, folderName)
    return flag

def DirectoryExists(directoryPath):
    '''
    Check if a given directory exists

    :param directoryPath: Fully qualified directory path
    :type directoryPath: str
    :return: True if directory exists, otherwise False
    :rtype: bool
    '''
    if(path.exists(directoryPath)):
        return True
    else:
        return False

def GetOutPutFileName(revitFilePath, fileExtension = '.txt', fileSuffix = ''):
    '''
    Returns a time stamped output file name based on the past in file name and file extension.

    :param revitFilePath: Fully qualified file path to file
    :type revitFilePath: str
    :param fileExtension: File extension needs to include '.', defaults to '.txt'
    :type fileExtension: str, optional
    :param fileSuffix: File suffix will be appended after the name but before the file extension, defaults to ''
    :type fileSuffix: str, optional
    
    :return: File name.
    :rtype: str
    '''

    # get date prefix for file name
    filePrefix = GetFileDateStamp()
    # added str() around this expression to satisfy sphinx auto code documentation
    # it will throw an exception when concatenating the string in the return statement
    name = str(Path.GetFileNameWithoutExtension(revitFilePath))
    return filePrefix + '_' + name + fileSuffix + fileExtension


def GetFileNameWithoutExt(filePath):
    '''
    Returns the file name without the file extension.

    :param filePath: Fully qualified file path to file
    :type filePath: str
    
    :return: The file name.
    :rtype: str
    '''
    
    name = Path.GetFileNameWithoutExtension(filePath)
    return name

def ConvertRelativePathToFullPath(relativeFilePath, fullFilePath):
    '''
    removes '../..' or '../' from relative file path string and replaces it with full path derived path past in sample path.

    - relative path sample: 'C:/temp/../myfile.ext'
    - full file path sample: 'C:/temp/Sample/someOtherFile.ext'
    - returns: 'C:/temp/Sample/myfile.ext'

    :param relativeFilePath: String containing relative file path annotation.
    :type relativeFilePath: str
    :param fullFilePath: A fully qualified file path of which the relative file path is a sub set.
    :type fullFilePath: str
    
    :return: A fully qualified file path.
    :rtype: str
    '''

    if( r'..\..' in relativeFilePath):
        two_up = path.abspath(path.join(fullFilePath ,r'..\..'))
        return two_up + relativeFilePath[5:]
    elif('..' in relativeFilePath):
        one_up = path.abspath(path.join(fullFilePath ,'..'))
        return one_up + relativeFilePath[2:]
    else:
        return relativeFilePath

def ReadCSVfile(filepathCSV, increaseMaxFieldSizeLimit = False):
    '''
    Read a csv file into a list of rows, where each row is another list.

    :param filepathCSV: The fully qualified file path to the csv file.
    :type filepathCSV: str

    :return: A list of list of strings representing the data in each row.
    :rtype: list of list of str
    '''

    rowList = []

    # hard coded hack
    if(increaseMaxFieldSizeLimit):
        csv.field_size_limit(2147483647)

    try:
        with open(filepathCSV) as csvFile:
            reader = csv.reader(csvFile)
            for row in reader: # each row is a list
                rowList.append(row)
    except Exception as e:
        print (str(e))
        rowList = []
    return rowList

def GetFirstRowInCSVFile(filePath):
    '''
    Reads the first line of a csv text file and returns it as a list of strings

    :param filePath: The fully qualified file path.
    :type filePath: str

    :return: The first row of a text file.
    :rtype: str
    '''

    row = []
    try:
        with open(filePath) as f:
            reader = csv.reader(f)
            row = f.readline()
            row = row.strip()
    except Exception:
        row = []
    return row

def ReadTabSeparatedFile(filePath, increaseMaxFieldSizeLimit = False):
    '''
    Read a tab separated text file into a list of rows, where each row is another list.

    :param filePath: The fully qualified file path to the tab separated text file.
    :type filePath: str

    :return:  A list of list of strings representing the data in each row.
    :rtype: list of list of str
    '''

    rowList = []

    # hard coded hack
    if(increaseMaxFieldSizeLimit):
        csv.field_size_limit(2147483647)

    try:
        with open (filePath) as f:
            reader = csv.reader(f, dialect='excel-tab')
            for row in reader: # each row is a list
                rowList.append(row)
            f.close()
    except Exception as e:
        print (filePath, str(e))
        rowList = []
    return rowList

def GetFirstRowInFile(filePath):
    '''
    Reads the first line of a text file and returns it as a single string

    :param filePath: The fully qualified file path.
    :type filePath: str

    :return: The first row of a text file.
    :rtype: str
    '''

    row = ''
    try:
        with open(filePath) as f:
            row = f.readline().strip()
    except Exception:
        row = None
    return row
# ---------------------------------------------------------------------------------------------------------------------------------

def ConDoesNotEqual (valueOne, valueTwo):
    '''
    Returns True if valueOne does not match valueTwo.

    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    
    :return: True if valueOne does not match valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne != valueTwo):
        return True
    else:
        return False

# 
def ConDoesEqual (valueOne, valueTwo):
    '''
    Returns True if valueOne does match valueTwo.

    :param valueOne: a value
    :type valueOne: var
    :param valueTwo: another value
    :type valueTwo: var
    
    :return: True if valueOne does match valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne == valueTwo):
        return True
    else:
        return False

def ConOneStartWithTwo (valueOne, valueTwo):
    '''
    Returns True if valueOne starts with valueTwo.

    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    
    :return: True if valueOne starts with valueTwo, otherwise False
    :rtype: bool
    '''

    if (valueOne.startswith(valueTwo)):
        return True
    else:
        return False

def ConTwoStartWithOne (valueOne, valueTwo):
    '''
    Returns True if valueTwo starts with valueOne.

    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    
    :return: True if valueTwo starts with valueOne, otherwise False
    :rtype: bool
    '''

    if (valueTwo.startswith(valueOne)):
        return True
    else:
        return False

# returns True if valueTwo does not starts with valueOne
def ConTwoDoesNotStartWithOne (valueOne, valueTwo):
    '''
    Returns True if valueTwo does not starts with valueOne.

    :param valueOne: a value
    :type valueOne: str
    :param valueTwo: another value
    :type valueTwo: str
    
    :return: True if valueTwo does not starts with valueOne, otherwise False
    :rtype: bool
    '''

    if (valueTwo.startswith(valueOne)):
        return False
    else:
        return True

# ---------------------------------------------------------------------------------------------------------------------------------

def ParsStringToBool(text):
    '''
    Converts a string to lower case and then to bool. Will throw an exception if it fails to do so.

    ( 'true' = True, 'false' = False)

    :param text: The string representing a bool.
    :type text: str
    :raises Exception: If string to bool conversion fails the 'String cant be converted to bool' exception will be raised.
    
    :return: True or False
    :rtype: bool
    '''

    if(text.lower() == 'true'):
        return True
    elif (text.lower() == 'false'):
        return False
    else:
         raise Exception('String cant be converted to bool')

# ---------------------------------------------------------------------------------------------------------------------------------

#: two digit padding
PAD_SINGLE_DIGIT_TO_TWO = '%02d'
#: three digit padding
PAD_SINGLE_DIGIT_TO_THREE = '%03d'


def PadSingleDigitNumericString(numericString, format = PAD_SINGLE_DIGIT_TO_TWO):
    '''
    Pads a single digit integer (past in as a string) with a leading zero (default)

    :param numericString: Integer as string.
    :type numericString: str
    :param format: The integer padding format, defaults to PAD_SINGLE_DIGIT_TO_TWO
    :type format: str, optional
    
    :return: The padded integer as string.
    :rtype: str
    '''

    # attempt to convert string to int first
    try:
        value = int(numericString)
        return str(format%value)
    except Exception:
        #string was not an integer...
        return numericString

def EncodeAscii (string):
    '''
    Encode a string as ascii and replaces all non ascii characters

    If a non string is past in the value will be returned unchanged.
    
    :param string: The string to be ascii encoded.
    :type string: str

    :return: ascii encoded string
    :rtype: str
    '''
    if (type(string) == str):
        return string.encode('ascii','replace')
    else:
        return string

def GetFirst(iterable, default, condition = lambda x: True):
    '''
    Returns the first value in a list matching condition. If no value found returns the specified default value.

    :param iterable: the list to be searched.
    :type iterable: iterable
    :param default: The default value
    :type default: var
    :param condition: The condition to be checked, defaults to lambda x:True
    :type condition: _type_, optional
    
    :return: First value matching condition, otherwise default value
    :rtype: var
    '''

    return next((x for x in iterable if condition(x)),default)

def ConvertImperialToMetricMM(value):
    '''
    Converts feet and inches to mm

    :param value: The value in feet to be converted
    :type value: float
    
    :return: The converted value
    :rtype: float
    '''

    return value * 304.8

def IndexOf(list, item):
    '''
    Gets the index of item in list

    :param list: The list
    :type list: list
    :param item: The item of which to return the index.
    :type item: var

    :return: The index of the item in the list, if no match -1 will be returned
    :rtype: int
    '''
    try:
        return list.index(item)
    except:
        return -1

def RemoveItemsFromList(sourceList, removeIdsList):
    '''
    helper removes items from a source list

    :param sourceList: The list containing items
    :type sourceList: list var
    :param removeIdsList: the list containing items to be removed
    :type removeIdsList: list var
    
    :return: The filtered source list.
    :rtype: list var
    '''

    try:
        for item in removeIdsList:
            sourceList.remove(item)
    except:
        pass
    return sourceList


def flatten(d, parent_key='', sep='_'):
    '''
    Flattens a dictionary as per stack overflow

    https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys/6027615#6027615

    :param d: _description_
    :type d: _type_
    :param parent_key: _description_, defaults to ''
    :type parent_key: str, optional
    :param sep: _description_, defaults to '_'
    :type sep: str, optional
    :return: _description_
    :rtype: _type_
    '''
    
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
