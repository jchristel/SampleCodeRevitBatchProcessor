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
COMMON_LIBRARY_LOCATION = r'C:\temp'

ROOT_PATH = r'C:\temp'
#debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Files.rvt'

import clr
import System
import csv
import sys
sys.path.append(COMMON_LIBRARY_LOCATION)

# import common library
from duHast.Revit.Common import file_io as rFileIO, transaction as rTran
from duHast.Utilities import result as res, utility as util
from duHast.Revit.Family import family_utils as rFamU

# flag whether this runs in debug or not
DEBUG = False

# --------------------------
#default file path locations
# --------------------------
#store output here:


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


clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

import Autodesk.Revit.DB as rdb

#output messages either to batch processor (debug = False) or console (debug = True)
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

# -------------
# my code here:
# -------------

def rename_loaded_families(doc):
    '''
    Loops over global family list and renames all matches.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    '''

    return_value = res.Result()
    family_ids = rFamU.get_all_loadable_family_ids_through_types(doc)
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
                output ('Found: {}'.format(old_name))
            	# rename the family within an action ( needs to be wrapped into a Revit transaction)
                def action():
                    action_return_value = res.Result()
                    output ('Attempting to rename family: {}'.format(old_name))
                    try:
                        family.Name = new_name
                        action_return_value.update_sep(True, 'Renamed old: {} to new: {}'.format(old_name, new_name))
                    except Exception as e:
                        action_return_value.update_sep(False, 'Failed to rename family: {} with exception: {}'.format(old_name,e))
                    return action_return_value
                transaction = rdb.Transaction(doc, 'Renaming: {}'.format(new_name))
                return_value.update( rTran.in_transaction(transaction, action) )
    output(return_value.message)

def read_family_names():
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
        output('Read: {} rename rules.'.format(len(LIST_OF_FAMILY_NAMES)))
    except Exception as e:
        output('Failed to read family name file: {}'.format(e))

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

output('Updating Family Names .... start')

# read rename rules
read_family_names()
# rename families
rename_loaded_families(DOC)

#sync changes back to central
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    SYNCING = rFileIO.sync_file (DOC)
    output('Syncing to Central: finished [{}]'.format (SYNCING.status))

output('Modifying Revit File.... finished ')