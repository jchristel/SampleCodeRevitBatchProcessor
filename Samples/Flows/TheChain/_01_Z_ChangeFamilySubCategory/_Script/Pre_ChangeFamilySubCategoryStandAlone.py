'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a pre - processing module creating task files for revit batch processor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module generates batch processor task files by :

- Combining any number of task files.

    - comma separatd text files
    - file extension .task 
    - first colum contains the fully qualified file path to a Revit family file which requires processing
    - no header row

or if no pre defined list is provided:

-   terminates with error status 2.

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

import utilModifyBVN as utilM # sets up all commonly used variables and path locations!
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
    Checks whether task list files are present in given directory.

    :param directoryPath: A fully qualified directory path.
    :type directoryPath: str

    :return: True if at least one task list file is present, otherwise false.
    :rtype: bool
    '''

    taskListFiles = util.GetFilesWithFilter(
        directoryPath,
        utilM.PREDEFINED_TASK_FILE_EXTENSION
        )
    if(len(taskListFiles) > 0):
        return True
    else:
        return False

def _GetTaskListFiles(directoryPath):
    '''
    Get any pre defined task files containing the path to a subset of families in the library.
    
    :return: List of file path
    :rtype: list of str
    '''

    taskListFiles = util.GetFilesWithFilter(
        directoryPath,
        utilM.PREDEFINED_TASK_FILE_EXTENSION 
        )
    return taskListFiles

def _combineTaskListFiles(files):
    '''
    Reads the content of each pre defined task file.
    Expected format is : comma separated text file where first column is a file path to a revit family.

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
                    if(myFileItem not in revitFiles):
                        revitFiles.append(myFileItem )
    return revitFiles

# -------------
# main:
# -------------

result_ = res.Result()
Output( 'Python pre process script Generate Task list ...')
# check  for a task list file ... otherwise exit
if(_taskFilesPresent(utilM.TASK_FILE_DIRECTORY)):
    # check if any task files are present
    rootPath_ = utilM.TASK_FILE_DIRECTORY
    Output ('Collecting files from task list(s) located: ' + rootPath_)
else:
    Output ('No task files found! Exiting process.')
    # time to get out
    sys.exit(2)

# check whether folder contains any task files
# if not process files in entire library
taskListFiles = _GetTaskListFiles(rootPath_)
Output('Number of task files found: ' + str(len(taskListFiles)))
if(len(taskListFiles) > 0):
    revitFiles = _combineTaskListFiles(taskListFiles)
    Output('Number of files in task files found: ' + str(len(revitFiles)))
    # build bucket list
    buckets = wl.DistributeWorkload(
        utilM.TASK_FILE_NO, 
        revitFiles, 
        fl.getFileSize
    )
    # write out file lists
    counter = 0
    for bucket in buckets:
        fileName =  os.path.join(utilM.TASK_FILE_DIRECTORY, 'Tasklist_' + str(counter)+ '.txt')
        statusWrite = fl.writeRevitTaskFile(
            fileName, 
            bucket, 
            fl.BucketToTaskListFileSystem
        )
        result_.Update(statusWrite)
        Output (statusWrite.message)
        counter += 1
    Output('Finished writing out task files')
else:
    Output ('Task file did not contain any families...Exiting process.')
    result_.UpdateSep(False, 'Task file did not contain any families...Exiting process.')

if(result_.status):
    sys.exit(0)
else:
    sys.exit(2)