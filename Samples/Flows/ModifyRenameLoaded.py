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
from duHast.APISamples import RevitCommonAPI as com
from duHast.Utilities import Utility as util
from duHast.APISamples.Family import RevitFamilyUtils as rFamU
from duHast.Utilities import Result as res
from duHast.APISamples import RevitTransaction as rTran

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
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    revitFilePath_ = debugRevitFileName_





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

    returnValue = res.Result()
    famIds = rFamU.GetAllLoadableFamilyIdsThroughTypes(doc)
    counter = 0
    for familyID in famIds:
        # retrieve the family through the id
        family = doc.GetElement(familyID)
        # loop over rename directives from csv file
        for oldname,newname in LIST_OF_FAMILY_NAMES:
            # remove file extension to old and new name
            if(oldname.lower().endswith('.rfa')):
                oldname = oldname[:-4]
            if(newname.lower().endswith('.rfa')):
                newname = newname[:-4]
            if oldname == family.Name:
                counter = counter + 1
                Output ('Found: ' + oldname)
            	# rename the family within an action ( needs to be wrapped into a Revit transaction)
                def action():
                    actionReturnValue = res.Result()
                    Output ('Attempting to rename family: '+ oldname)
                    try:
                        family.Name = newname
                        actionReturnValue.UpdateSep(True, 'Renamed old: ' + oldname + ' to new: ' + newname)
                    except Exception as e:
                        actionReturnValue.UpdateSep(False, 'Failed to rename family: ' + oldname + ' with exception: ' + str(e))
                    return actionReturnValue
                transaction = rdb.Transaction(doc, 'Renaming: ' + newname)
                returnValue.Update( rTran.in_transaction(transaction, action) )
    Output(returnValue.message)

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
        Output('Read: ' + str(len(LIST_OF_FAMILY_NAMES)) + ' rename rules')
    except Exception as e:
        Output('Failed to read family name file: ' + str(e))

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
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit File.... finished ')