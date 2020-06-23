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
rootPath = r'C:\temp'
#path to Common.py
commonlibraryDebugLocation = r'C:\temp'
#debug mode revit project file name
debugRevitFileName = r'C:\temp\Test_grids.rvt'

# Add batch processor scripting references
if not debug:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
     # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath = revit_script_util.GetRevitFilePath()
else:
    #set path to common library
    import sys
    sys.path.append(commonlibraryDebugLocation)
    #get default revit file name
    revitFilePath = debugRevitFileName

#import common library
import Common
from Common import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

#build output file name
fileName = rootPath + '\\'+ GetOutPutFileName(revitFilePath)

def GetWorksetName(doc, idInteger):
    name = 'unknown'
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if(p.Id.IntegerValue == idInteger):
            name = p.Name
            break
    return name

def GetMaxExtentAsString(grid):
    ex = grid.GetExtents()
    max = '['+ ','.join([str(ex.MaximumPoint.X), str(ex.MaximumPoint.Y), str(ex.MaximumPoint.Z)]) + ']'
    min = '['+ ','.join([str(ex.MinimumPoint.X), str(ex.MinimumPoint.Y), str(ex.MinimumPoint.Z)]) + ']'    
    return '\t'.join([min, max])

#method writing out grid information
def writeGridData(doc, fileName):
    status = True
    try:
        f = open(fileName, 'w')
        f.write('\t'.join(['ID', 'NAME', 'WORKSETNAME', 'EXTENTMAX', 'EXTENTMIN', '\n']))
        for p in FilteredElementCollector(doc).OfClass(Grid):
            f.write('\t'.join([str(p.Id.IntegerValue), EncodeAscii(p.Name), GetWorksetName(doc, p.WorksetId.IntegerValue), GetMaxExtentAsString(p), '\n']))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

# -------------
# main:
# -------------

Output('Writing Grid Data.... start')

#write out shared parameter data
result = writeGridData(doc, fileName)

Output('Writing Grid Data.... status: ' + str(result))
Output('Writing Grid Data.... finished ' + fileName)
