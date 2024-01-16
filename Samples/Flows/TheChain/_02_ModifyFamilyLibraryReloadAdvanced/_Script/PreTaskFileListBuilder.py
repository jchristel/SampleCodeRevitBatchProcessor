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

# this sample shows how to write out a number of task files using bucket distribution

# --------------------------
# default file path locations1
# --------------------------

import sys, os
import utilReloadBVN as utilR # sets up all commonly used variables and path locations!
# import file list module
import FileList as fl
# import workloader utils
import Workloader as wl
import Utility as util

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    print (message)

# -------------
# main:
# -------------
print( 'Python pre process script: Task list builder start ...')
# check if a folder path was passt in...otherwise go with default
if (len(sys.argv) == 3):
    rootPath_ = sys.argv[1]
    fileName_ = sys.argv[2]
    Output('Using passt in path: ' + rootPath_)
    Output('Using passt in file name: ' + fileName_)
    # get files to be processed
    revitFiles = fl.GetRevitFilesForProcessing(
                rootPath_ + '\\' + fileName_, 
                False, 
                utilR.REVIT_FAMILY_FILE_EXTENSION)
    if(len(revitFiles) > 0):
        #for rf in revitFiles:
        #    Output(rf.name + ' :: ' + str(rf.size))
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
            Output (statusWrite.message)
            counter += 1
        Output('Finished writing out task files')
        sys.exit(0)
    else:
        # do nothing...
        Output ('No files selected!')
        sys.exit(2)
else:
    rootPath_ = r'C:\Users\jchristel\Documents\DebugRevitBP\FamReload'
    Output ('Aborted with default file path: ' + rootPath_)
    sys.exit(2)
