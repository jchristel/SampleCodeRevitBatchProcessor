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

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import common library
import Utility as util

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import script_util

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# combine data
Output('Writing summary Data.... start')
dateStamp_ = util.GetFileDateStamp()
util.CombineFiles(rootPath_, dateStamp_, '_CAD','.txt', dateStamp_ + '_CAD_Links_summary.txt')
Output('Writing summary Data.... finished: ' + dateStamp_ + '_CAD_Links_summary.txt')
util.CombineFiles(rootPath_, dateStamp_, '_RVT','.txt', dateStamp_ + '_RVT_Links_summary.txt')
Output('Writing summary Data.... finished: ' + dateStamp_ + '_RVT_Links_summary.txt')
