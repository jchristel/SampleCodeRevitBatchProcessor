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
import sys, getopt, os

# import file item class
import FileItem as fi
# import workloader utils
import Workloader as wl
import WorkloadBucket as wlb
# custom result class
import Result as res


clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# -------------
# my code here:
# -------------

# method creating a number of task list files
# directoryPath         directory containing files to be added to task lists
# fileExtension         file extenision in format .rvt
# tasklistDirectory     the directory path where the task files will be written to
# taskFilesNumbes       number of task files to be written
def WriteFileList(directoryPath, fileExtension, taskListDirectory, taskFilesNumber, fileGetter):
    returnvalue = res.Result()
    # get revit files in input dir
    revitfiles = fileGetter(directoryPath,'.rvt')
    # build bucket list
    buckets = wl.DistributeWorkload(taskFilesNumber, revitfiles, getFileSize)
    try:
        # write out file lists
        counter = 0
        for bucket in buckets:
            fileName =  os.path.join(taskListDirectory, 'Tasklist_' + str(counter)+ '.txt')
            statusWrite = writeRevitTaskFile(fileName, bucket)
            returnvalue.Update(statusWrite)
            counter += 1
        returnvalue.AppendMessage('Finished writing out task files')
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed to save file list! '  + str(e))
    return returnvalue

# helper method retrieving files in a given directory and of a given file extension
# directory              directory containing files to be retrived
# fileExtension         file extenision in format .rvt
def getRevitFiles(directory, fileExtension):
    files = []
    listOfFiles = os.listdir(directory)
    for f in listOfFiles:
        # check for file extension match
        if(f.lower().endswith(fileExtension.lower())):
            # Use join to get full file path.
            location = os.path.join(directory, f)
            # Get size and add to list of files.
            size = os.path.getsize(location)
            files.append(fi.MyFileItem(location,size))
    return files

# helper method retrieving files in a given directory and its subdirectories with a give extension
# directory              directory containing files to be retrived
# fileExtension         file extenision in format .rvt
def getRevitFilesInclSubDirs(directory, fileExtension):
    files = []
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(directory):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    for f in listOfFiles:
        # check for file extension match
        if(f.lower().endswith(fileExtension.lower())):
            # Get size and add to list of files.
            size = os.path.getsize(f)
            files.append(fi.MyFileItem(f,size))
    return files

# helper used to define workload size (same as file size)
def getFileSize(item):
    return item.size

# default task list content for files on a file server location
def BucketToTaskListFileSystem(item):
    return item.name

# default task list content for files on a BIM 360 cloud drive
def BucketToTaskListBIM360(item):
    return ' '.join([item.BIM360RevitVersion, item.BIM360ProjectGUID, item.BIM360FileGUID])

# method writing out task files
# filename      fully qualified file path of the task file name including extension
# bucket        workload bucket containing fully qualified file path in .name property
# GetData       method writing out file data required ()
def writeRevitTaskFile(fileName, bucket, GetData = BucketToTaskListFileSystem):
    returnvalue = res.Result()
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
            f.write(data)
        f.close()
        returnvalue.AppendMessage('wrote task list: ' + fileName + ' [TRUE]')
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed to write task list: ' + fileName + ' with exception ' + str(e))
    return returnvalue