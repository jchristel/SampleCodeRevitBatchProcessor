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
debug = True

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath = r'C:\temp'
#path to Common.py
commonlibraryDebugLocation = r'C:\Project\Git\RB'
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

def InTransaction(tranny, action):
    result = None
    tranny.Start()
    try:
        result = action()
        tranny.Commit()
    except Exception as e:
        Output ("exception: " + str(e))
        tranny.RollBack()
    return result

def GetWorksetIdByName(doc, worksetName):
    id = ElementId.InvalidElementId
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if(p.Name == worksetName):
            id = p.Id
            break
    return id

def ModifyWorkset(doc, defaultWorksetName, collector):
    #get the ID of the default grids workset
    defaultId = GetWorksetIdByName(doc, defaultWorksetName)
    #check if invalid id came back..workset no longer exists..
    if(defaultId != ElementId.InvalidElementId):
        #get all grids in model and check their workset
        for p in collector:
            if (p.WorksetId != defaultId):
                #move grid to new workset
                def action():
                    wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
                    wsparam.Set(defaultId.IntegerValue )
                transaction = Transaction(doc, "Changing workset " + p.Name)
                result = InTransaction(transaction, action)
                Output(p.Name + ' ' + str(result))
            else:
                Output(p.Name + ' is already on default workset ' + defaultWorksetName) 
    else:
        Output('Default workset '+ defaultWorksetName + ' does no longer exists in file!')

# -------------
# main:
# -------------

def Modify(doc, revitFilePath, gridData):
    revitFileName = GetRevitFileName(revitFilePath)
    flag = False
    for fileName, defaultWorksetName in gridData:
        if (revitFileName.startswith(fileName)):
            flag = True
            collectorGrids = FilteredElementCollector(doc).OfClass(Grid)
            ModifyWorkset(doc, defaultWorksetName, collectorGrids)
            collectorLevels = FilteredElementCollector(doc).OfClass(Level)
            ModifyWorkset(doc, defaultWorksetName, collectorLevels)
            collectorScopeBoxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest)
            ModifyWorkset(doc, defaultWorksetName, collectorScopeBoxes)
            break
    if (flag == False):
        Output('No grid data provided for current Revit file')
    return flag

Output('Checking levels and grids.... start')

defaultWorksets = [
['Test_grids', '99_LEVELS AND GRIDS']
]

#write out shared parameter data
result = Modify(doc, revitFilePath, defaultWorksets)
Output('Checking levels and grids.... status: ' + str(result))

#sync changes back to central
if (doc.IsWorkshared and debug == False):
    Output('Syncing to Central: start')
    SyncFile (doc, fileName)
    Output('Syncing to Central: finished')

Output('Checking levels and grids.... finished ')
