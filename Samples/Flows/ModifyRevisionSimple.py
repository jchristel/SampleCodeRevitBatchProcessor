'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create a revision.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to 

- add a revision (or multiple) to a document

Likely scenarios for this flows are:

- You may want to add a revision to multiple documents

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
import datetime

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import libraries
import RevitCommonAPI as com
import RevitRevisions as rRev
import Result as res

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

def AddRevToDocument(doc):
    '''
    Adds a number of revisions to the document

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:  
        Result class instance.
        
        - Revision(s) created status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision created successfully.
        - result.result: will contain list of id's of new revision created
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # store rev id's in list 
    ids=[]
    try:
        for rev in revisionsToAdd_:
            # create new revision
            newRevStatus = rRev.CreateRevision(doc, rev)
            if(newRevStatus.status):
                # append to existing revisions
                newRev = newRevStatus.result[0]
                ids.Add(newRev.Id)
        returnValue.result = ids
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to create revisions: ' + str(e))
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# list of revisions in format:
revisionsToAdd_ = [
    rRev.revisionData(
        'Revision description text',
        'Issue to text',
        'Issue from text',
        rdb.RevisionNumberType.Numeric, # this is a numeric revision 
        datetime.datetime.now().strftime("%d/%m/%y"), # put the current date
        rdb.RevisionVisibility.Hidden # hide revision clouds and tags
    )
]

Output('Add revision.... start')

# add revision to doc
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
      Output('Add revision.... Saving non workshared file: start')
      doc.SaveAs(revitFilePath_)
      Output('Add revision.... Saving non workshared file: finished')

Output('Add revision.... finished ')