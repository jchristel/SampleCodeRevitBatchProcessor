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

#renames worksets based on a list specifying the current workset name and the new workset name

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
debugRevitFileName_ = r'C:\temp\Test_Workset.rvt'

# Add batch processor scripting references
if not debug_:
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
import Common
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

# -------------
# main:
# -------------

#modifies a workset name
def Modify(doc, revitFilePath, worksetData):
    revitFileName = GetRevitFileName(revitFilePath)
    flag = False
    flagRenamed = False
    for fileName, defaultWorksetName in worksetData:
        if (revitFileName.startswith(fileName)):
            flag = True
            for currentName, newName in defaultWorksetName:
                for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
                    if(p.Name == currentName):
                        def action():
                            WorksetTable.RenameWorkset(doc, p.Id, newName)
                        transaction = Transaction(doc, "Changing workset name from: " + str(currentName) + ' to ' + str(newName))
                        result = InTransaction(transaction, action)
                        Output("Changing workset name from: " + str(currentName) + ' to ' + str(newName) + ' ' + str(result))
                        flagRenamed = True
            break
    if (flag == False):
        Output('No workset data provided for current Revit file!')
    elif(flagRenamed == False):
        Output('No matching workset names provided for current set of worksets!')
    return flag & flagRenamed

Output('Modifying Worksets.... start')


#list of worksets to be renamed
#format
#[host file name,[[current workset name, new workset name]]]
defaultWorksets_ = [
['Test_Workset', [['AR_LEVELS AND GRIDS','99_LEVELS AND GRIDS']]]
]

#modify workset naming
result_ = Modify(doc, revitFilePath_, defaultWorksets_)
Output('Modifying Worksets.... status: ' + str(result_))

#sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    SyncFile (doc)
    Output('Syncing to Central: finished')

Output('Modifying Worksets.... finished ')
