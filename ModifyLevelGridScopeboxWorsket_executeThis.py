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

# sample description
# This modifies the worksets of levels, grids, scope boxes and reference planes
# A list provides per file the default workset these elements should be on

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
    #get default revit file name
    revitFilePath = debugRevitFileName

#set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)

#import common libraries
import Common as com
from Common import *
import Result as res

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

# -------------
# main:
# -------------

def Modify(doc, revitFilePath, gridData):
    returnvalue = res.Result()
    revitFileName = com.GetRevitFileName(revitFilePath)
    flag = False
    for fileName, defaultWorksetName in gridData:
        if (revitFileName.startswith(fileName)):
            flag = True
            collectorGrids = FilteredElementCollector(doc).OfClass(Grid)
            grids = com.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
            returnvalue.Update(grids)

            collectorLevels = FilteredElementCollector(doc).OfClass(Level)
            levels = com.ModifyElementWorkset(doc, defaultWorksetName, collectorLevels, 'levels')
            returnvalue.Update(levels)

            collectorScopeBoxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest)
            sboxes = com.ModifyElementWorkset(doc, defaultWorksetName, collectorScopeBoxes, 'scope boxes')
            returnvalue.Update(sboxes)
            
            #fix up ref planes
            collectorRefPlanes = FilteredElementCollector(doc).OfClass(ReferencePlane)
            refPlanes = com.ModifyElementWorkset(doc, defaultWorksetName, collectorRefPlanes,  'reference planes')
            returnvalue.Update(refPlanes)
            
            break
    if (flag == False):
        returnvalue.status = False
        returnvalue.message = 'No grid data provided for current Revit file '+ revitFileName
    return returnvalue

Output('Checking levels and grids.... start')

#a list in format
#[
#['Revit file name','workset levels, grids, scope boxes should be on'],
#['Revit file name','workset levels, grids, scope boxes should be on']
#]

defaultWorksets_ = [
['Test_grids', 'Shared Levels & Grids']
]

#modify workset of levels, grids ands scope boxes
flagModifyWorkSets_ = Modify(doc, revitFilePath, defaultWorksets_)
Output(flagModifyWorkSets_.message + ' :: ' + str(flagModifyWorkSets_.status))

#sync changes back to central
if (doc.IsWorkshared and debug == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Checking levels and grids.... finished ')
