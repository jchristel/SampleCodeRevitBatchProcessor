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
import glob
import datetime
import os
import Result as res

# get the date stamp prefix of report files
def GetFileDateStamp():
    d = datetime.datetime.now()
    return d.strftime('%y_%m_%d')


# get the date stamp prefix of report files
def GetFolderDateStamp():
    d = datetime.datetime.now()
    return d.strftime('%Y%m%d')

# used to combine report files into one
# files are combined pased on thsi search pattern: folderPath + '\\' + filePreffix + '*' + fileSuffix + fileExtension
# prefix is usually the time stamp in format  '%y_%m_%d'
def CombineFiles(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt'):
    resultFileAppend = res.Result()
    file_list = glob.glob(folderPath + '\\' + filePrefix + '*' + fileSuffix + fileExtension)
    resultFileAppend.AppendMessage('Found files: ' + str(len(file_list)))
    f = open(folderPath + '\\' + outPutFileName, 'w' )
    fileCounter = 0
    for file_ in file_list:
        resultFileAppend.AppendMessage('...Adding lines from file: ' + file_)
        lineCounter = 0
        lineCounterAdded = 0
        for line in open( file_, 'r' ):
            # ensure header from first file is copied over
            if(fileCounter == 0 and lineCounter == 0 or lineCounter != 0):
                f.write( line + '\n')
                lineCounterAdded += 1
            lineCounter += 1
        resultFileAppend.AppendMessage('......Added lines: ' + str(lineCounterAdded))
        fileCounter += 1
    f.close()
    return resultFileAppend

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
