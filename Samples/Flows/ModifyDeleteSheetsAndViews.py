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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
from duHast.Revit.Views import delete as rViewDel
from duHast.Utilities import files_io as fileIO
from duHast.Utilities.Objects import result as res
from duHast.Utilities import compare as compare
from duHast.Revit.Common import file_io as rFileIO

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = True

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

    revit_file_name =  fileIO.get_file_name_without_ext(revit_file_path)
    for file_name, view_rules in view_data:
        if (revit_file_name.startswith(file_name)):
            collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = rViewDel.delete_views(doc, view_rules, collector_views)
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
    return_value.update_sep(False,'No sheet data provided for current Revit file')
    
    revit_file_name = fileIO.get_file_name_without_ext(REVIT_FILE_PATH)
    # Output(sheets)
    for file_name, sheet_rules in sheets_data:
        # check if set of rules applies to this particular project file
        if (revit_file_name.startswith(file_name)):
            collector_sheets = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = rViewDel.delete_sheets(doc, sheet_rules, collector_sheets)
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
            ['Parameter Name', compare.does_not_equal, 'Parameter Value'] # sheet condition rule
        ]
    ],
    ['FileTwo', # project file name start
        [
            ['Parameter Name', compare.does_not_equal, 'Parameter Value'], # sheet condition rule
            ['Parameter Name', compare.does_not_equal, 'Parameter Value'] # sheet condition rule
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
            ['Parameter Name', compare.does_not_equal, 'Parameter Value'], # view condition rule
            ['Parameter Name', compare.does_not_equal, 'Parameter Value'], # view condition rule
            ['Parameter Name', compare.does_not_equal, 'Parameter Value'] # view condition rule
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
RESULT_DELETE_VIEWS_NOT_ON_SHEETS = rViewDel.delete_views_not_on_sheets(DOC, check_name)
output(str(RESULT_DELETE_VIEWS_NOT_ON_SHEETS.message)+ '.... status: ' + str(RESULT_DELETE_VIEWS_NOT_ON_SHEETS.status))
 
# sync changes back to central, non workshared files will not be saved!
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    SYNCING = rFileIO.sync_file (DOC)
    output('Syncing to Central: finished ' + str(SYNCING.status))

output('Modifying Revit File.... finished ')