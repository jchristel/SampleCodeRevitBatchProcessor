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
import RevitCommonAPI as com
import RevitWorksets as rWork
import Utility as util
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
    returnValue = res.Result()
    revitFileName = util.GetFileNameWithoutExt(revitFilePath)
    flag = False
    for fileName, defaultWorksetName in gridData:
        if (revitFileName.startswith(fileName)):
            flag = True
            collectorGrids = FilteredElementCollector(doc).OfClass(Grid)
            grids = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
            returnValue.Update(grids)

            collectorLevels = FilteredElementCollector(doc).OfClass(Level)
            levels = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorLevels, 'levels')
            returnValue.Update(levels)

            collectorScopeBoxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest)
            sboxes = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorScopeBoxes, 'scope boxes')
            returnValue.Update(sboxes)
            
            # fix up ref planes
            collectorRefPlanes = FilteredElementCollector(doc).OfClass(ReferencePlane)
            refPlanes = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorRefPlanes,  'reference planes')
            returnValue.Update(refPlanes)
            
            break
    if (flag == False):
        returnValue.UpdateSep(False, 'No grid data provided for current Revit file ' + revitFileName)
    return returnValue

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