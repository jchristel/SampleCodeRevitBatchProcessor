'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a pre - processing module creating task files for Revit batch processor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module generates batch processor task files by :

- Combining any number of task files.

    - comma separated text files
    - file extension .task 
    - first colum contains the fully qualified file path to a Revit family file which requires processing
    - no header row

or if no pre defined list is provided:

-   generates batch processor task files including all Revit family files in a given library directory and its sub directories.

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
    Checks whether task list files are present in given directory.

    :param directoryPath: A fully qualified directory path.
    :type directoryPath: str

    :return: True if at least one task list file is present, otherwise false.
    :rtype: bool
    '''

    taskListFiles = util.GetFilesWithFilter(
        directoryPath,
        utilR.REPORT_FILE_EXTENSION 
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
        utilR.REPORT_FILE_EXTENSION 
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
if(_taskFilesPresent(utilR.FAMILY_CHANGE_DIRECTIVE_DIRECTORY)):
    # check if any task files are present
    rootPath_ = utilR.FAMILY_CHANGE_DIRECTIVE_DIRECTORY
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
    Output('Number of Revit files in task files found: ' + str(len(revitFiles)))
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
    Output ('Task file did not contain any families...Exiting process.')
    result_.update_sep(False, 'Task file did not contain any families...Exiting process.')

if(result_.status):
    sys.exit(0)
else:
    sys.exit(2)