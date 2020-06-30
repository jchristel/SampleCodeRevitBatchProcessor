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

import clr
import System

# flag whether this runs in debug or not
debug = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath = r'P:\18\1803009.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\ReportLinks\_Output'
#path to Common.py
commonlibraryDebugLocation_ = r'P:\18\1803009.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\_Common'

# Add batch processor scripting references
if not debug:
    import script_util

#set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)

#import common library
import Common_Post as cp
from Common_Post import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug:
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
dateStamp = cp.GetFileDateStamp()
cp.CombineFiles(rootPath, dateStamp, '_CAD','.txt', dateStamp + '_CAD_Links_summary.txt')
Output('Writing summary Data.... finished: ' + dateStamp + '_CAD_Links_summary.txt')
cp.CombineFiles(rootPath, dateStamp, '_RVT','.txt', dateStamp + '_RVT_Links_summary.txt')
Output('Writing summary Data.... finished: ' + dateStamp + '_RVT_Links_summary.txt')
