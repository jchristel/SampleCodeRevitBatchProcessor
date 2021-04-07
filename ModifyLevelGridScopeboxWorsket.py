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

# this sample demonstrates how to 
# modify the worksets of levels, grids, scope boxes and reference planes
# A list provides per file the default workset these elements should be on

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import common libraries
import CommonRevitAPI as com
import Result as res

# autodesk API
from Autodesk.Revit.DB import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
debug = False

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
    # get default revit file name
    revitFilePath = debugRevitFileName_

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug:
        revit_script_util.Output(str(message))
    else:
        print (message)

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
            
            # fix up ref planes
            collectorRefPlanes = FilteredElementCollector(doc).OfClass(ReferencePlane)
            refPlanes = com.ModifyElementWorkset(doc, defaultWorksetName, collectorRefPlanes,  'reference planes')
            returnvalue.Update(refPlanes)
            
            break
    if (flag == False):
        returnvalue.UpdateSep(False, 'No grid data provided for current Revit file ' + revitFileName)
    return returnvalue

# -------------
# main:
# -------------

# store output here:
rootPath = r'C:\temp'

Output('Checking levels and grids.... start')

# a list in format
#[
#['Revit file name','workset levels, grids, scope boxes should be on'],
#['Revit file name','workset levels, grids, scope boxes should be on']
#]

defaultWorksets_ = [
['Test_grids', 'Shared Levels & Grids']
]

# modify workset of levels, grids ands scope boxes
statusModifyWorkSets_ = Modify(doc, revitFilePath, defaultWorksets_)
Output(statusModifyWorkSets_.message + ' :: ' + str(statusModifyWorkSets_.status))

# sync changes back to central
if (doc.IsWorkshared and debug == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Checking levels and grids.... finished ')