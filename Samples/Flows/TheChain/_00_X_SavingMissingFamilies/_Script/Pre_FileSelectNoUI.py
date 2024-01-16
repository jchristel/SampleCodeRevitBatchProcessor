'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains pre task function(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Writes out a task lists of files to be processed based on missing families host report

- Host report is located in /Users/Username/_Input directory
- Number of task files in specified in global variable.
- Task file location is specified in global varaible.

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

# this sample shows how to write out a number of task files using bucket distribution

# --------------------------
# Imports
# --------------------------

import sys, os

import utilDataBVN as utilData # sets up all commonly used variables and path locations!
# import file list module
import FileList as fl
import Utility as util

# -------------
# my code here:
# -------------

def Output(message = ''):
    '''
    Print message to console.

    :param message: The message, defaults to ''
    :type message: str, optional
    '''

    # 08/09/2022 19:09:19 :
    timestamp = util.GetDateStamp('%d/%m/%Y %H_%M_%S : ')
    print (timestamp + message)

# -------------
# main:
# -------------

# build file path to missing families host family report 
processPath_ =  utilData.INPUT_DIRECTORY + '\\' + utilData.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT

if(util.FileExist(processPath_)):
    # give user feed back
    Output ('Collecting files from: ' + processPath_)

    # write out task lists
    result_ = fl.WriteFileList(
        processPath_,
        utilData.FILE_EXTENSION_OF_FILES_TO_PROCESS, 
        utilData.TASK_FILE_DIRECTORY, 
        utilData.NUMBER_OF_TASK_FILES, 
        fl.GetRevitFilesForProcessingSimpleRootDirOnly)
    
    # check if any file to be processed where found!
    if (result_.status and len(result_.result) == 0):
        # no file found...: write out empty task lists!
        for i in range (util.NUMBER_OF_TASK_FILES):
            fileName = fl.getTaskFileName(utilData.TASK_FILE_DIRECTORY, i)
            resultEmpty_ = fl.writeEmptyTaskList(fileName)
            result_.Update(resultEmpty_)

    # give user feed back
    Output (result_.message)
    Output('Writing file Data.... status: ' + str(result_.status))
else:
    Output('Missing families host report does not exist: ' + processPath_) 
    # exit with error
    sys.exit(2)