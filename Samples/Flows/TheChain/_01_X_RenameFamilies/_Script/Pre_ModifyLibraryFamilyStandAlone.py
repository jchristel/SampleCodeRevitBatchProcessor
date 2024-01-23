'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a pre - processing module creating task files for revit batch processor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module generates batch processor task files by :

- Combining any number of task files.

    - csv separatd text files
    - file extension .task 
    - first colum contains the fully qualified file path to a Revit family file which requires processing
    - no header row

or if no pre defined list is provided:

-   generates batch processor task files including all Revit family files in a given library directory and its sub directories.

'''

#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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



# --------------------------
# default file path locations
# --------------------------
# directory containing families to be processed
rootPath_ = ''

import sys, os

import utilModifyBVN as utilR # sets up all commonly used variables and path locations!
# import file list module
import FileList as fl
import FileItem as fi
import Utility as util
# import workloader utils
import Workloader as wl
import Result as res

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    print (message)

def _taskFilesPresent(directoryPath):
    '''
    Checks whether task list files are present in given dirtectory.

    :param directoryPath: A fully qualified directory path.
    :type directoryPath: str

    :return: True if at least one task list file is present, otherwise false.
    :rtype: bool
    '''

    taskListFiles = util.GetFilesWithFilter(
        directoryPath,
        utilR.PREDEFINED_TASK_FILE_EXTENSION
        )
    if(len(taskListFiles) > 0):
        return True
    else:
        return False

def _GetTaskListFiles(directoryPath):
    '''
    Get any pre defined task files containing the path to a subset of families in the library. This is done as to not having to process all\
        families in the library for the task at hand.

    :return: List of file path
    :rtype: list of str
    '''

    taskListFiles = util.GetFilesWithFilter(
        directoryPath,
        utilR.PREDEFINED_TASK_FILE_EXTENSION
        )
    return taskListFiles

def _combineTaskListFiles(files):
    '''
    Reads the content of each pre defined task file.
    Expected format is : csv separated text file where first column is a file path to a revit family.

    :param files: List of predefined task files
    :type files: [str]
    :return: List of file items
    :rtype: [:class:`.FileItem`]
    '''

    revitFiles = []
    for taskFilePath in files:
        rows = util.ReadCSVfile(taskFilePath)
        for row in rows:
            # make sure row contains at least one column (hopefully containing a file path)
            if(len(row) >= 1 ):
                # does the file still exists?
                if(util.FileExist(row[0])):
                    size = os.path.getsize(row[0])
                    myFileItem = fi.MyFileItem(row[0],size)
                    # make sure list is of unique files
                    if(myFileItem  not in revitFiles):
                        revitFiles.append(myFileItem )
    return revitFiles

# -------------
# main:
# -------------

result_ = res.Result()
print( 'Python pre process script Generate Task list ...')
# check if a folder path was passt in...otherwise check  for a task list file ... if neither go with default
if (len(sys.argv) == 2):
    rootPath_ = sys.argv[1]
    Output ('Collecting files from passt in path: ' + rootPath_)
elif(_taskFilesPresent(utilR.PREDEFINED_TASK_FILE_DIRECTORY)):
    # check if any task files are present
    rootPath_ = utilR.PREDEFINED_TASK_FILE_DIRECTORY
    Output ('Collecting files from task list located: ' + rootPath_)
else:
    rootPath_ = utilR.REVIT_LIBRARY_PATH
    Output ("Using default library directory path: " + rootPath_)

# check whether folder contains any task files
# if not process files in entire library
taskListFiles = _GetTaskListFiles(rootPath_)
if(len(taskListFiles) > 0):
    revitFiles = _combineTaskListFiles(taskListFiles)
    # build bucket list
    buckets = wl.DistributeWorkload(
        utilR.TASK_FILE_NO, 
        revitFiles, 
        fl.getFileSize
    )
    # write out file lists
    counter = 0
    for bucket in buckets:
        fileName =  os.path.join(utilR.TASK_FILE_DIRECTORY, 'Tasklist_' + str(counter)+ '.txt')
        statusWrite = fl.writeRevitTaskFile(
            fileName, 
            bucket, 
            fl.BucketToTaskListFileSystem
        )
        result_.update(statusWrite)
        Output (statusWrite.message)
        counter += 1
    Output('Finished writing out task files')
else:
    Output ('No task files found, using directory instead:')
    Output ('Collecting files from ' + utilR.REVIT_LIBRARY_PATH )
    # get file data
    Output('Writing file Data.... start')
    result_ = fl.WriteFileList(
        utilR.REVIT_LIBRARY_PATH,
        utilR.FILE_EXTENSION_OF_FILES_TO_PROCESS, 
        utilR.TASK_FILE_DIRECTORY, 
        utilR.TASK_FILE_NO, 
        fl.GetRevitFilesInclSubDirs
    )
    Output (result_.message)
    Output('Writing file Data.... status: ' + str(result_.status))
if(result_.status):
    sys.exit(0)
else:
    sys.exit(2)