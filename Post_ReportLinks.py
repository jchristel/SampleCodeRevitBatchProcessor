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
# this sample shows how to merge a number of text report files created on the same day with the same suffix (from the same report)
# into a single report file for ease of reviewing

import clr
import System

# flag whether this runs in debug or not
debug_ = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath_ = r'C:\temp'
#path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'

# Add batch processor scripting references
if not debug_:
    import script_util

#set path to common_Post library
import sys
sys.path.append(commonlibraryDebugLocation_)

#import common library
import Common_Post as cp
from Common_Post import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

# -------------
# main:
# -------------

#combine data
Output('Writing summary Data.... start')
dateStamp_ = cp.GetFileDateStamp()
cp.CombineFiles(rootPath_, dateStamp_, '_CAD','.txt', dateStamp_ + '_CAD_Links_summary.txt')
Output('Writing summary Data.... finished: ' + dateStamp + '_CAD_Links_summary.txt')
cp.CombineFiles(rootPath_, dateStamp_, '_RVT','.txt', dateStamp_ + '_RVT_Links_summary.txt')
Output('Writing summary Data.... finished: ' + dateStamp + '_RVT_Links_summary.txt')
