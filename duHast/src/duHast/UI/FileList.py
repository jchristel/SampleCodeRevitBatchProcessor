'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions for the file selection GUI.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

# this sample shows how to write out a number of task files using bucket distribution by file size

import clr
import System
import os


# import file item class
from duHast.UI import FileItem as fi
# import workloader utils
from duHast.UI import Workloader as wl

# custom result class
from duHast.Utilities import Result as res

# -------------
# my code here:
# -------------

def getRevitFiles(directory, fileExtension):
    '''
    Returns files in a given directory and of a given file extension.

    :param directory: The fully qualified directory path.
    :type directory: str
    :param fileExtension: The file extension filter in format '.ext'
    :type fileExtension: str

    :return: List of file items
    :rtype: [:class:`.FileItem`]
    '''

    files = []
    listOfFiles = os.listdir(directory)
    for f in listOfFiles:
        # check for file extension match
        if(f.lower().endswith(fileExtension.lower())):
            # check if this is a back up file, remove the file extension
            filePath = f[:-len(fileExtension)]
            if(isBackUpFile(filePath) == False):
                # Use join to get full file path.
                location = os.path.join(directory, f)
                # Get size and add to list of files.
                size = os.path.getsize(location)
                files.append(fi.MyFileItem(location,size))
    return files

def getRevitFilesInclSubDirs(directory, fileExtension):
    '''
    Returns files in a given directory and its sub directories of a given file extension.

    :param directory: The fully qualified directory path.
    :type directory: str
    :param fileExtension: The file extension filter in format '.ext'
    :type fileExtension: str

    :return: List of file items
    :rtype: [:class:`.FileItem`]
    '''

    files = []
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(directory):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    for f in listOfFiles:
        # check for file extension match
        if(f.lower().endswith(fileExtension.lower())):
            # check if this is a back up file, remove the file extension
            filePath = f[:-len(fileExtension)]
            if(isBackUpFile(filePath) == False):
                # Get size and add to list of files.
                size = os.path.getsize(f)
                files.append(fi.MyFileItem(f,size))
    return files

def isBackUpFile(filePath):
    '''
    Checks whether a file is a Revit back up file.
    
    Backup files are usually in format 'filename.01234.ext'
    
    Method of checking:

    - splitting file name at every full stop
    - check whether a list with more more then 2 entries came back ?
    
        - no: 
            - not a back up
        - yes: 
            - check last list entry whether it is 4 characters in length and can it be convert it into an integer?
        
                - yes: 
                    - backup file
                - no
                    - normal file
    
    :param filePath: A fully qualified file path.
    :type filePath: str

    :return: True if a back up file, otherwise False.
    :rtype: bool
    '''

    isBackup = False
    chunks = filePath.split('.')
    if(len(chunks)>2):
        lastChunk = chunks[len(chunks)-2]
        try:
            converted_num = int(lastChunk)
            isBackup = True
        except Exception:
            pass
    return isBackup

def getFileSize(item):
    '''
    Helper used to define workload size (same as file size)

    :param item: A file item object instance.
    :type item: :class:`.FileItem`

    :return: The file size.
    :rtype: int
    '''

    return item.size

def BucketToTaskListFileSystem(item):
    '''
    Default task list content for files on a file server location.

    :param item: A file item object instance.
    :type item: :class:`.FileItem`

    :return: The item name.(fully qualified file path)
    :rtype: str
    '''

    return item.name

def BucketToTaskListBIM360(item):
    '''
    Default task list content for files on a BIM 360 cloud drive.

    :param item: A file item object instance.
    :type item: :class:`.FileItem`

    :return: The revit version, project guid, file guid separated by a space ' '
    :rtype: str
    '''

    return ' '.join([item.BIM360RevitVersion, item.BIM360ProjectGUID, item.BIM360FileGUID])

def writeRevitTaskFile(fileName, bucket, GetData = BucketToTaskListFileSystem):
    '''
    Writes out a task list file.

    :param fileName: Fully qualified file path of the task file name including extension.
    :type fileName: str
    :param bucket: Workload bucket object instance.
    :type bucket: :class:`.WorkloadBucket`
    :param GetData: Returns data from file item object to be written to file, defaults to BucketToTaskListFileSystem
    :type GetData: func(:class:`.FileItem`) -> str, optional

    :return: 
        Result class instance.

        - Write file status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message property contains fully qualified file path to task list file.
        
        On exception:
        
        - .status (bool) will be False.
        - .message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        f = open(fileName, 'w')
        rowCounter = 0
        for p in bucket.items:
            data = GetData(p)
            # check whether first row
            if(rowCounter != 0):
                # if not first row add line feed character before data written
                data = '\n' + data
            else:
                rowCounter += 1
            f.write(data.encode('utf-8'))
        f.close()
        returnValue.AppendMessage('wrote task list: ' + fileName + ' [TRUE]')
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to write task list: ' + fileName + ' with exception ' + str(e))
    return returnValue

def WriteFileList(directoryPath, fileExtension, taskListDirectory, taskFilesNumber, fileGetter, fileDataProcessor = BucketToTaskListFileSystem):
    '''
    Writes out all task list(s) to file(s).

    :param directoryPath: Fully qualified directory path containing files to be added to task lists.
    :type directoryPath: str
    :param fileExtension: A file extension filter in format '.ext'
    :type fileExtension: str
    :param taskListDirectory: The fully qualified directory path where the task files will be written .
    :type taskListDirectory: str
    :param taskFilesNumber: The number of task files to be written.
    :type taskFilesNumber: int
    :param fileGetter: Function accepting a directory and file extension filter and returns file items from directory.
    :type fileGetter: func(str, str) -> :class:`.FileItem`
    :param fileDataProcessor: Function processing file item and returns a string to be written to task list file, defaults to BucketToTaskListFileSystem
    :type fileDataProcessor: func(:class:`.FileItem`) -> str, optional
    
    :return: 
        Result class instance.

        - Write file status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message property contains fully qualified file path for each task list file.
        
        On exception:
        
        - .status (bool) will be False.
        - .message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    returnValue.status = True
    # get revit files in input dir
    revitFiles = fileGetter(directoryPath, fileExtension)
    # build bucket list
    buckets = wl.DistributeWorkload(taskFilesNumber, revitFiles, getFileSize)
    try:
        # write out file lists
        counter = 0
        for bucket in buckets:
            fileName =  os.path.join(taskListDirectory, 'Tasklist_' + str(counter)+ '.txt')
            statusWrite = writeRevitTaskFile(fileName, bucket, fileDataProcessor)
            returnValue.Update(statusWrite)
            counter += 1
        returnValue.AppendMessage('Finished writing out task files')
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to save file list! '  + str(e))
    return returnValue
