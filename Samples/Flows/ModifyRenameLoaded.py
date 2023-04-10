'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Rename loaded families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to rename loaded families based on a CSV file.

Likely scenarios for this flows are:

- Your project library is undergoing a change... 

Notes:

- Revit Batch Processor settings:
    
    - all worksets closed
    - create new Local file

'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

#set path to common library
#path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'

rootPath_ = r'C:\temp'
#debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Files.rvt'

import clr
import System
import csv
import sys
sys.path.append(commonlibraryDebugLocation_)

# import common library
from duHast.APISamples.Common import RevitFileIO as rFileIO, RevitTransaction as rTran
from duHast.Utilities import Utility as util, Result as res
from duHast.APISamples.Family import RevitFamilyUtils as rFamU

# flag whether this runs in debug or not
debug_ = False

# --------------------------
#default file path locations
# --------------------------
#store output here:


# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
     # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revit_file_path_ = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    revit_file_path_ = debugRevitFileName_


clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

import Autodesk.Revit.DB as rdb

#output messages either to batch processor (debug = False) or console (debug = True)
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

# -------------
# my code here:
# -------------

def renameLoadedFamilies(doc):
    '''
    Loops over global family list and renames all matches.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    '''

    return_value = res.Result()
    family_ids = rFamU.GetAllLoadableFamilyIdsThroughTypes(doc)
    counter = 0
    for family_id in family_ids:
        # retrieve the family through the id
        family = doc.GetElement(family_id)
        # loop over rename directives from csv file
        for old_name,new_name in LIST_OF_FAMILY_NAMES:
            # remove file extension to old and new name
            if(old_name.lower().endswith('.rfa')):
                old_name = old_name[:-4]
            if(new_name.lower().endswith('.rfa')):
                new_name = new_name[:-4]
            if old_name == family.Name:
                counter = counter + 1
                Output ('Found: {}'.format(old_name))
            	# rename the family within an action ( needs to be wrapped into a Revit transaction)
                def action():
                    action_return_value = res.Result()
                    Output ('Attempting to rename family: {}'.format(old_name))
                    try:
                        family.Name = new_name
                        action_return_value.UpdateSep(True, 'Renamed old: {} to new: {}'.format(old_name, new_name))
                    except Exception as e:
                        action_return_value.UpdateSep(False, 'Failed to rename family: {} with exception: {}'.format(old_name,e))
                    return action_return_value
                transaction = rdb.Transaction(doc, 'Renaming: {}'.format(new_name))
                return_value.Update( rTran.in_transaction(transaction, action) )
    Output(return_value.message)

def readFamilyNames():
    '''
    Reads family list from csv file.

    Note: 
    
    - CSV file path is stored in global variable: FAMILY_NAME_FILE_PATH
    - CSV file contains of 2 columns

        - column one: old family name
        - column two: new family name
        - no header row!
    
    - rows are read into global variable: LIST_OF_FAMILY_NAMES

    '''

    try:
        LIST_OF_FAMILY_NAMES = util.ReadCSVfile(FAMILY_NAME_FILE_PATH)
        Output('Read: {} rename rules.'.format(len(LIST_OF_FAMILY_NAMES)))
    except Exception as e:
        Output('Failed to read family name file: {}'.format(e))

# -------------
# main:
# -------------

# global list which will contain the rename rules
# populated from csv file
LIST_OF_FAMILY_NAMES = []

# path to rename rules csv file
# format per row is
# old name.rfa, new name.rfa
FAMILY_NAME_FILE_PATH = r''

Output('Updating Family Names .... start')

# read rename rules
readFamilyNames()
# rename families
renameLoadedFamilies(doc)

#sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = rFileIO.SyncFile (doc)
    Output('Syncing to Central: finished [{}]'.format (syncing_.status))

Output('Modifying Revit File.... finished ')