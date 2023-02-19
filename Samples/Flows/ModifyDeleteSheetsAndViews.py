'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Delete sheets and views from project files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to delete sheets and views from workshared Revit project files using filters.
A likely scenario for this is models being send out for coordination requiring some clean up prior issue.

This sample:

- deletes all views where given parameter(s) fails value tests(s)
- deletes all sheets where given parameter(s) fails value test(s)
- any views not on sheets with exception of views starting with a given string

Note:

- Filters are defined by project file to allow for maximum flexibility.
- If multiple filters are defined, a sheet or view must not meet any of them in order to be deleted. (logical AND condition)

'''
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
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitViews as rView
from duHast.Utilities import Utility as util
from duHast.Utilities import Result as res

# autodesk API
import Autodesk.Revit.DB as rdb

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

def Output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# 
def CheckName(view):
    '''
    Checks whether view names starts with a number of given strings.

    :param view: A view.
    :type view: Autodesk.Revit.DB.View

    :return: True if view name starts with any of the given strings. Otherwise False.
    :rtype: bool
    '''

    if(view.Name.lower().startswith('test1') or view.Name.lower().startswith('test2') or view.Name.lower().startswith('test3')):
        return False
    else:
        return True

def ModifyViews(doc, revitFilePath, viewData):
    '''
    Deletes views based on rules

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The current model (document) file path.
    :type revitFilePath: str
    :param viewData: List of files and associated view filter rules. Refer to `viewRules_` below.
    :type viewData: [[filename,[conditions]]]

    :return: 
        Result class instance.

        - result.status: View deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain deletion status of each view deleted.
        - result.result will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    #set default values
    returnValue = res.Result()
    returnValue.status = False
    returnValue.message = 'No view data provided for current Revit file'

    revitFileName =  util.GetFileNameWithoutExt(revitFilePath)
    for fileName, viewRules in viewData:
        if (revitFileName.startswith(fileName)):
            collectorViews = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            returnValue = rView.DeleteViews(doc, viewRules, collectorViews)
            break
    return returnValue


def ModifySheets(doc, sheetsData):
    '''
    Deletes sheets based on rules.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param sheetsData: List of files and associated sheet filter rules. Refer to `sheetRules_` below.
    :type sheetsData: [[filename,[conditions]]]

    :return: 
        Result class instance.

        - result.status: Sheet deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain deletion status of each sheet deleted.
        - result.result will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    # set default values
    returnValue = res.Result()
    returnValue.UpdateSep(False,'No sheet data provided for current Revit file')
    
    revitFileName = util.GetFileNameWithoutExt(revitFilePath_)
    # Output(sheets)
    for fileName, sheetRules in sheetsData:
        # check if set of rules applies to this particular project file
        if (revitFileName.startswith(fileName)):
            collectorSheets = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            returnValue = rView.DeleteSheets(doc, sheetRules, collectorSheets)
            break
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# sheets to delete rules 
sheetRules_ = [
    ['FileOne', # project file name start (would apply to files FileOneOne and FileOneTwo)
        [
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'] # sheet condition rule
        ]
    ],
    ['FileTwo', # project file name start
        [
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'], # sheet condition rule
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'] # sheet condition rule
        ]
    ]
]

'''
List containing the sheet rules by project file
'''

# views to delete rules
viewRules_ = [
    ['File', # project file name start
        [
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'], # view condition rule
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'], # view condition rule
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'] # view condition rule
        ]
    ]
]

'''
List containing the view rules by project file
'''

#s ave revit file to new location
Output('Modifying Revit File.... start')

# delete sheets
resultDeleteSheets_ = ModifySheets(doc, sheetRules_)
Output(resultDeleteSheets_.message + '.... status: ' + str(resultDeleteSheets_.status))

# delete views
resultDeleteViews_ = ModifyViews(doc, revitFilePath_, viewRules_)
Output(resultDeleteViews_.message + '.... status: ' + str(resultDeleteViews_.status))

# delete views not on sheets
resultDeleteViewsNotOnSheets_ = rView.DeleteViewsNotOnSheets(doc, CheckName)
Output(str(resultDeleteViewsNotOnSheets_.message)+ '.... status: ' + str(resultDeleteViewsNotOnSheets_.status))
 
# sync changes back to central, non workshared files will not be saved!
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit File.... finished ')