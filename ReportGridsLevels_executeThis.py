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

# sample description
# how to report on grids and levels properties

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
#debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_grids.rvt'

# Add batch processor scripting references
if not debug:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
     # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    revitFilePath_ = debugRevitFileName_

#set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)

#import common library
import Common as com
from Common import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

#build output file names
fileNameGrid_ = rootPath + '\\'+ com.GetOutPutFileName(revitFilePath_,'.txt', '_grids')
fileNameLevel_ = rootPath + '\\'+ com.GetOutPutFileName(revitFilePath_,'.txt', '_levels')

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
        f.write('\t'.join(['HOSTFILE','ID', 'NAME', 'WORKSETNAME', 'EXTENTMAX', 'EXTENTMIN', '\n']))
        for p in FilteredElementCollector(doc).OfClass(Grid):
            f.write('\t'.join([com.GetRevitFileName(revitFilePath_), str(p.Id.IntegerValue), com.EncodeAscii(p.Name), GetWorksetName(doc, p.WorksetId.IntegerValue), GetMaxExtentAsString(p), '\n']))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

#method writing out level information
def writeLevelData(doc, fileName):
    status = True
    try:
        f = open(fileName, 'w')
        f.write('\t'.join(['HOSTFILE', 'ID', 'NAME', 'WORKSETNAME', 'ELEVATION', '\n']))
        for p in FilteredElementCollector(doc).OfClass(Level):
            f.write('\t'.join([com.GetRevitFileName(revitFilePath_), str(p.Id.IntegerValue), com.EncodeAscii(p.Name), GetWorksetName(doc, p.WorksetId.IntegerValue), str(p.Elevation), '\n']))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

# -------------
# main:
# -------------

#write out grid data
Output('Writing Grid Data.... start')
result_ = writeGridData(doc, fileNameGrid_)
Output('Writing Grid Data.... status: ' + str(result_))
Output('Writing Grid Data.... finished ' + fileNameGrid_)

#write out Level data
Output('Writing Level Data.... start')
result_ = writeLevelData(doc, fileNameLevel)
Output('Writing Level Data.... status: ' + str(result_))
Output('Writing Level Data.... finished ' + fileNameLevel_)
