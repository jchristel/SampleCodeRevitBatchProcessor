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
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import from duHast
from duHast.APISamples.Views import RevitViewsDelete as rViewDel
from duHast.Utilities import FilesIO as fileIO
from duHast.Utilities import Result as res
from duHast.Utilities import Compare as compare
from duHast.APISamples.Common import RevitFileIO as rFileIO

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
     # NOTE: these only make sense for batch Revit file processing mode.
    DOC = revit_script_util.GetScriptDocument()
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    REVIT_FILE_PATH = DEBUG_REVIT_FILE_NAME
    # get document from python shell
    DOC = doc

# -------------
# my code here:
# -------------

def output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not DEBUG:
        revit_script_util.Output(str(message))
    else:
        print (message)

# 
def check_name(view):
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

def modify_views(doc, revit_file_path, view_data):
    '''
    Deletes views based on rules

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model (document) file path.
    :type revit_file_path: str
    :param view_data: List of files and associated view filter rules. Refer to `viewRules_` below.
    :type view_data: [[filename,[conditions]]]

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
    return_value = res.Result()
    return_value.status = False
    return_value.message = 'No view data provided for current Revit file'

    revit_file_name =  fileIO.GetFileNameWithoutExt(revit_file_path)
    for file_name, view_rules in view_data:
        if (revit_file_name.startswith(file_name)):
            collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = rViewDel.DeleteViews(doc, view_rules, collector_views)
            break
    return return_value


def modify_sheets(doc, sheets_data):
    '''
    Deletes sheets based on rules.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param sheets_data: List of files and associated sheet filter rules. Refer to `sheetRules_` below.
    :type sheets_data: [[filename,[conditions]]]

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
    return_value = res.Result()
    return_value.UpdateSep(False,'No sheet data provided for current Revit file')
    
    revit_file_name = fileIO.GetFileNameWithoutExt(REVIT_FILE_PATH)
    # Output(sheets)
    for file_name, sheet_rules in sheets_data:
        # check if set of rules applies to this particular project file
        if (revit_file_name.startswith(file_name)):
            collector_sheets = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = rViewDel.DeleteSheets(doc, sheet_rules, collector_sheets)
            break
    return return_value

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

# sheets to delete rules 
SHEET_RULES = [
    ['FileOne', # project file name start (would apply to files FileOneOne and FileOneTwo)
        [
            ['Parameter Name', compare.ConDoesNotEqual, 'Parameter Value'] # sheet condition rule
        ]
    ],
    ['FileTwo', # project file name start
        [
            ['Parameter Name', compare.ConDoesNotEqual, 'Parameter Value'], # sheet condition rule
            ['Parameter Name', compare.ConDoesNotEqual, 'Parameter Value'] # sheet condition rule
        ]
    ]
]

'''
List containing the sheet rules by project file
'''

# views to delete rules
VIEW_RULES = [
    ['File', # project file name start
        [
            ['Parameter Name', compare.ConDoesNotEqual, 'Parameter Value'], # view condition rule
            ['Parameter Name', compare.ConDoesNotEqual, 'Parameter Value'], # view condition rule
            ['Parameter Name', compare.ConDoesNotEqual, 'Parameter Value'] # view condition rule
        ]
    ]
]

'''
List containing the view rules by project file
'''

#s ave revit file to new location
output('Modifying Revit File.... start')

# delete sheets
RESULT_DELETE_SHEETS = modify_sheets(DOC, SHEET_RULES)
output('{} .... status: [{}]'.format( RESULT_DELETE_SHEETS.message,RESULT_DELETE_SHEETS.status))

# delete views
RESULT_DELETE_VIEWS = modify_views(DOC, REVIT_FILE_PATH, VIEW_RULES)
output(RESULT_DELETE_VIEWS.message + '.... status: ' + str(RESULT_DELETE_VIEWS.status))

# delete views not on sheets
RESULT_DELETE_VIEWS_NOT_ON_SHEETS = rViewDel.DeleteViewsNotOnSheets(DOC, check_name)
output(str(RESULT_DELETE_VIEWS_NOT_ON_SHEETS.message)+ '.... status: ' + str(RESULT_DELETE_VIEWS_NOT_ON_SHEETS.status))
 
# sync changes back to central, non workshared files will not be saved!
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    SYNCING = rFileIO.SyncFile (DOC)
    output('Syncing to Central: finished ' + str(SYNCING.status))

output('Modifying Revit File.... finished ')