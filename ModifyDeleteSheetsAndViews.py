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

# this sample:
# - deletes all views where given parameter(s) fails value tests(s)
# - deletes all sheets where given parameter(s) fails value test(s)
# - any views not on sheets with exception of views starting with a given string

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

#import common libraries
import CommonRevitAPI as com
import Utility as util
import Result as res

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
     # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    revitFilePath_ = debugRevitFileName_

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

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

    revitFileName =  util.GetFileNameWithoutExt(revitFilePath)
    for fileName, viewRules in viewData:
        if (revitFileName.startswith(fileName)):
            collectorViews = FilteredElementCollector(doc).OfClass(View)
            returnvalue = com.DeleteViews(doc, viewRules, collectorViews)
            break
    return returnvalue

# deletes sheets based on rules
def ModifySheets(doc, sheets):
    
    # set default values
    returnvalue = res.Result()
    returnvalue.UpdateSep(False,'No sheet data provided for current Revit file')
    
    revitFileName = util.GetFileNameWithoutExt(revitFilePath_)
    # Output(sheets)
    for fileName, sheetRules in sheets:
        if (revitFileName.startswith(fileName)):
            collectorSheets = FilteredElementCollector(doc).OfClass(View)
            returnvalue = com.DeleteSheets(doc, sheetRules, collectorSheets)
            break
    return returnvalue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# sheets to delete rules 
sheetRules_ = [
    ['FileOne',[
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value']
        ]],# applies to files FileOneOneBeforeName and FileOneTwoBeforeName
    ['FileTwo', [
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'],
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value']
    ]]# applies to file FileTwoBeforeName
]

# views to delete rules
viewRules_ = [
    ['File',[
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'],
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'],
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value']
    ]]
]

#s ave revit file to new location
Output('Modifying Revit File.... start')

# delete sheets
resultDeleteSheets_ = ModifySheets(doc, sheetRules_)
Output(resultDeleteSheets_.message + '.... status: ' + str(resultDeleteSheets_.status))

# delete views
resultDeleteViews_ = ModifyViews(doc, revitFilePath_, viewRules_)
Output(resultDeleteViews_.message + '.... status: ' + str(resultDeleteViews_.status))

# delete views not on sheets
resultDeleteViewsNotOnSheets_ = com.DeleteViewsNotOnSheets(doc, CheckName)
Output(str(resultDeleteViewsNotOnSheets_.message)+ '.... status: ' + str(resultDeleteViewsNotOnSheets_.status))
 
# sync changes back to central, non workshared files will not be saved!
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit File.... finished ')