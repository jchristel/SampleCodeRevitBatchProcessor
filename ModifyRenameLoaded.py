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

# this sample renames loaded families based on data read from CSV file

import clr
import System
import csv

# flag whether this runs in debug or not
debug_ = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
#rootPath_ = r'C:\temp'
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

# import common library
import RevitCommonAPI as com
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

def renameLoadedFamilies(doc):
    '''loops over global family list and renames all matches'''
    eq = FilteredElementCollector(doc).OfClass(Family)
    counter = 0
    for e in eq:
        for oldname,newname in LIST_OF_FAMILY_NAMES:
            # remove file extension to old and new name
            if(oldname.lower().endswith('.rfa')):
                oldname = oldname[:-4]
            if(newname.lower().endswith('.rfa')):
                newname = newname[:-4]
            if oldname == e.Name:
                counter = counter + 1
            	Output ('Found: ' + oldname)
            	# rename
            	def action():
                	Output ('Attempting to rename family: '+ oldname)
                	e.Name = newname
                	Output ('old: ' + oldname + ' new: ' + newname)
                	return
            	transaction = Transaction(doc, 'Renaming: ' + newname)
            	com.InTransaction(transaction, action)
    Output('Renamed: ' + str(counter) + ' families')

def readFamilyNames():
    '''reads family list from csv file'''
    try:
        with open(FAMILY_NAME_FILE_PATH) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader: # each row is a list
                # read information
                LIST_OF_FAMILY_NAMES.append(row)
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
FAMILY_NAME_FILE_PATH = r'C:\temp\RenameLoadedFamilies.csv'

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