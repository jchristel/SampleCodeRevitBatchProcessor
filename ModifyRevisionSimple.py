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

# this sample demonstrates how to:
# - add a revision (or multiple) to a document

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

# import libraries
import CommonRevitAPI as com
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

def AddRevisionToDocument (doc, revData):
    result = res.Result()
    newRevision = None
    def action():
        newRevision = Revision.Create(doc)
        newRevision.Description = revData[0]
        newRevision.IssuedBy = revData[1]
        newRevision.NumberType = revData[2]
        newRevision.RevisionDate = revData[3]
        newRevision.Visibility = RevisionVisibility.Hidden
        return newRevision
    transaction = Transaction(doc, "adding revision to file")
    result = com.InTransaction(transaction, action)
    return result 

def AddRevToDocument(doc):
    result = res.Result()
    # store rev id's in list
    ids=[]
    try:
        for rev in revisionsToAdd_:
            # create new revision
            newRev = AddRevisionToDocument (doc, rev)
            # append to existing revisions
            ids.Add(newRev.Id)
        result.result = ids
    except Exception as e:
        result.UpdateSep(False, 'Failed to create revisions: ' + str(e))
    return result

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# list of revisions in format:
# {'Description', 'IssuedBy', RevisionNumberType.Numeric, 'date'}
# datetime.datetime.now().strftime("%d/%m/%y")

revisionsToAdd_ = [
    ['FOR INFORMATION','your initials', RevisionNumberType.Numeric, r'22/12/20']
]

Output('Add revision.... start')

#add revision to doc and to sheet named 'Splashscreen'
result_  = AddRevToDocument(doc)
Output('Add revision.... status: ' + str(result_.status))

# synch the file
if(debug_ == False):
  if (doc.IsWorkshared):
      Output('Add revision.... Syncing to Central: start')
      result_ = com.SyncFile (doc)
      Output('Add revision.... Syncing to Central: finished '+ str(result_.status))
  else:
      #none work shared
      Output('Add revision.... Saving non norkshared file: start')
      doc.SaveAs(revitFilePath_)
      Output('Add revision.... Saving non norkshared file: finished')

Output('Add revision.... finished ')