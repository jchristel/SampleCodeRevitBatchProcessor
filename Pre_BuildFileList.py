#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# sample description
# this sample shows how to build a task list file (used as a pre-process)

import clr
import System

# flag whether this runs in debug or not
debug_ = True

# --------------------------
# default file path locations
# --------------------------
# store output here:
rootPath_ = r'C:\temp'
# path to Common.py
commonlibraryDebugLocation_ = r'C:\Project\Git\SampleCodeRevitBatchProcessor'
# directory containing files
sourcePath_ = r'C:\temp'

# Add batch processor scripting references
if not debug_:
    import script_util

# set path to common_Post library
import sys
sys.path.append(commonlibraryDebugLocation_)

# import common library (in this case the post lib since it got the methods we are after)
import Common_Post as cp
from Common_Post import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

def WriteFileList():
    status = True
    try:
        f = open(rootPath_ + '\\ProcessThis.txt', 'w')
        files = cp.GetFiles(sourcePath_)
        if(files != None and len(files) > 0):
            for file in files:
                f.write(file + '\n')
        f.close()
    except Exception as e:
        status = False
        Output('Failed to save file list!')
        Output (str(e))
    return status

# -------------
# main:
# -------------

# get file data
Output('Writing file Data.... start')
result_ = WriteFileList()
Output('Writing file Data.... status: ' + str(result_))
Output('Writing file Data.... finished: ' + rootPath_  + '\\ProcessThis.txt')
