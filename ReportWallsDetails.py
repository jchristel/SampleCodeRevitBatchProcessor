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
# how to report on wall types
# note: in place families of category wall and curtain wall do not have a valid Compound structure

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_walls.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import common library
import Utility as util
import RevitWalls as rWall

# autodesk API
from Autodesk.Revit.DB import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    revitFilePath_ = debugRevitFileName_

# -------------
# my code here:
# -------------

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# method writing out material information
# doc:          current model document
# fileName:     fully qualified file path
def WriteWallTypeData(doc, fileName):
    status = True
    try:
        status = util.writeReportData(
            fileName, 
            rWall.REPORT_WALLS_HEADER, 
            rWall.GetWallReportData(doc, revitFilePath_))
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# build output file name
fileName_ =  rootPath_ + '\\'+ util.GetOutPutFileName(revitFilePath_,'.txt', '_WallTypes')

Output('Writing Wall Type Data.... start')
#write out wall type data
result_ = WriteWallTypeData (doc, fileName_)
Output('Writing Wall Type Data.... status: ' + str(result_))
Output('Writing Wall Type Data.... finished ' + fileName_)