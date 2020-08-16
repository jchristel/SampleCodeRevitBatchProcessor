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

# this sample creates a detached copy of project files and
# deletes all views where given parameter(s) fails value tests(s)
# deletes all sheets where given parameter(s) fails value test(s)
# any views not on sheets with exception of views starting with a given string


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
debugRevitFileName_ = r'C:\temp\Test_Files.rvt'

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

#import common libraries
import Common as com
from Common import *
import Result as res

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

#-------------------view related

# checks whether view names starts with given strings
def CheckName(view):
    if(view.Name.lower().startswith('test1') or view.Name.lower().startswith('test2') or view.Name.lower().startswith('test3')):
        return False
    else:
        return True

# deletes views based on rules
def ModifyViews(doc, revitFilePath, viewData):
    
    #set default values
    returnvalue = res.Result()
    returnvalue.status = False
    returnvalue.message = 'No view data provided for current Revit file'

    revitFileName = com.GetRevitFileName(revitFilePath)
    for fileName, viewRules in viewData:
        if (revitFileName.startswith(fileName)):
            collectorViews = FilteredElementCollector(doc).OfClass(View)
            returnvalue = com.DeleteViews(doc, viewRules, collectorViews)
            break
    return returnvalue

# deletes sheets based on rules
def ModifySheets(doc, sheets):
    
    #set default values
    returnvalue = res.Result()
    returnvalue.status = False
    returnvalue.message = 'No sheet data provided for current Revit file'

    revitFileName = com.GetRevitFileName(revitFilePath_)
    #Output(sheets)
    for fileName, sheetRules in sheets:
        if (revitFileName.startswith(fileName)):
            collectorSheets = FilteredElementCollector(doc).OfClass(View)
            returnvalue = com.DeleteSheets(doc, sheetRules, collectorSheets)
            break
    return returnvalue

#------------------view related end-----------------------

#------------------ workset related

# modifies worksets of levels, grids, scope boxes
def Modify(doc, revitFilePath, gridData):
    revitFileName = com.GetRevitFileName(revitFilePath)
    foundMatch = False
    returnvalue = res.Result()
    for fileName, defaultWorksetName in gridData:
        if (revitFileName.startswith(fileName)):
            foundMatch = True
            #fix uyp grids
            collectorGrids = FilteredElementCollector(doc).OfClass(Grid)
            grids = com.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids)
            returnvalue.status = returnvalue.status & grids.status
            returnvalue.message = returnvalue.message + '\n' + grids.message
            
            #fix up levels
            collectorLevels = FilteredElementCollector(doc).OfClass(Level)
            levels = com.ModifyElementWorkset(doc, defaultWorksetName, collectorLevels)
            returnvalue.status = returnvalue.status & levels.status
            returnvalue.message = returnvalue.message + '\n' + levels.message

            #fix up scope boxes
            collectorScopeBoxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest)
            sboxes = com.ModifyElementWorkset(doc, defaultWorksetName, collectorScopeBoxes)
            returnvalue.status = returnvalue.status & sboxes.status
            returnvalue.message = returnvalue.message + '\n' + sboxes.message

            break
    if (foundMatch == False):
        returnvalue.status = False
        returnvalue.message = 'No workset data provided for current Revit file '+ revitFileName
    return returnvalue
#------------------ workset related end-----------------------

# -------------
# main:
# -------------


# list containing the default file names:
# [[revit host file name before save, revit host file name after save]]
defaultFileNames_ = [
    ['FileOneOneBeforeName', 'FileOneOneAfterName'],
    ['FileOneTwoBeforeName', 'FileOneTwoAfterName'],
    ['FileTwoBeforeName', 'FileTwoAfterName']
]

# list containing default worksets for levels grids, scope boxes
defaultWorksets_ = [
    ['FileOne', 'LEVELS AND GRIDS'],# applies to files FileOneOneBeforeName and FileOneTwoBeforeName
    ['FileTwo', 'SHARED LEVELS AND GRIDS']# applies to file FileTwoBeforeName
]

# sheets to delete rules 
sheetRules_ = [
    ['FileOne',[['Parameter Name', com.ConDoesNotEqual, 'Parameter Value']]],# applies to files FileOneOneBeforeName and FileOneTwoBeforeName
    ['FileTwo', [
        ['Parameter Name', com.ConDoesNotEqual, 'Parameter Value'],
        ['Parameter Name', com.ConDoesNotEqual, 'Parameter Value']
    ]]# applies to file FileTwoBeforeName
]

#views to delete rules
viewRules_ = [
    ['File',[
        ['Parameter Name', com.ConDoesNotEqual, 'Parameter Value'],
        ['Parameter Name', com.ConDoesNotEqual, 'Parameter Value'],
        ['Parameter Name', com.ConDoesNotEqual, 'Parameter Value']
    ]]
]

#save revit file to new location
Output('Modifying Revit File.... start')

# flag indicating whether the file can be saved
saveFile = True

# check if worksharing needs to be enabled
if (doc.IsWorkshared == False):
    saveFile = com.EnableWorksharing(doc)
    Output('Enabled worksharing.... status: ' + str(saveFile.status))

if (saveFile):
    result_ = com.SaveAs(doc, rootPath_ , revitFilePath_, defaultFileNames_)
    Output(result_.message + ' :: ' + str(result_.status))
else:
    Output('Not Saving Revit File!!!')

# fix up worksets....
flagModifyWorkSets_ = Modify(doc, revitFilePath_, defaultWorksets_)
Output('Changing levels and grids.... status: ' + str(flagModifyWorkSets_.status))

# delete sheets
resultDeleteSheets_ = ModifySheets(doc, sheetRules_)
Output(resultDeleteSheets_.message + '.... status: ' + str(resultDeleteSheets_.status))

# delete views
resultDeleteViews_ = ModifyViews(doc, revitFilePath_, viewRules_)
Output(resultDeleteViews_.message + '.... status: ' + str(resultDeleteViews_.status))

# delete views not on sheets
resultDeleteViewsNotOnSheets_ = com.DeleteViewsNotOnSheets(doc, CheckName)
Output(str(resultDeleteViewsNotOnSheets_.message)+ '.... status: ' + str(resultDeleteViewsNotOnSheets_.status))
 
# sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit File.... finished ')
