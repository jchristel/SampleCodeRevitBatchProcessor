'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create a revision and add it to a specific sheet.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to 

- add a revision (or multiple) to a document
- apply those revisions to sheets (filtered selection)
- mark the revision(s) as issued

Likely scenarios for this flows are:

- You may want to add a revision to a splash ( start up view) sheet for QA purposes every time you issue the model

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
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Views import RevitViews as rView
from duHast.APISamples import RevitRevisions as rRev
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

# output messages either to batch processor (debug = False) or console (debug = True)
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

def GetSheets(doc, sheetFilterRules):
    '''
    Get all sheets from the model matching filters supplied. 

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheetFilterRules: A set of rules. If sheet matches rule it will be returned. Defaults to None which will return all sheets. Refer to `sheetRules_` below.
    :type sheetFilterRules: [[filename,[[filter rules]]]]

    :return: List of sheets matching filter(s)
    :rtype: [Autodesk.Revit.DB.View]
    '''

    results = []
    # get sheets where revisions need to be applied to:
    revitFileName = util.GetFileNameWithoutExt(revitFilePath_)
    for fileName, sheetRules in sheetFilterRules:
        if (revitFileName.startswith(fileName)):
            results = rView.GetSheetsByFilters(doc, sheetRules)
            break
    return results

def MarkRevisionsAsIssued(doc, revIds):
    '''
    Marks revisions as issued.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revIds: List of revision ids identifying revisions to be marked as issued.
    :type revIds: [Autodesk.Revit.DB.ElementId]

    :return:  
        Result class instance.
        
        - Revisions marked as issued status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message(s) revision marked as issued successfully.
        - result.result: empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get all revisions in file
    revsInModel = rdb.Revision.GetAllRevisionIds(doc)
    # check against what was applied
    idsToBeMarkedIssued = set(revIds).intersection(revsInModel)
    for id in idsToBeMarkedIssued:
        # set revision status to issued
        resultSetToIssued = rRev.MarkRevisionAsIssuedByRevisionId(doc, id)
        returnValue.Update(resultSetToIssued)
    return returnValue

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

# main function of this sample
def AddRevsToSheetsRequired(doc, sheetFilterRules):
    '''
    Adds revision(s) to documents, applies revision(s) to sheet(s) and then sets the revision status to 'issued'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheetFilterRules: A set of rules. If sheet matches rule it will be returned. Defaults to None which will return all sheets. Refer to `sheetRules_` below.
    :type sheetFilterRules: [[filename,[[filter rules]]]]

    :return:  
        Result class instance.
        
        - Revision(s) created, added to sheets, set to 'issued' status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the messages of each step required to create a revision, apply it to a sheet and set it to issued.
        - result.result: will contain list of id's of new revision created
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get sheet to which revisions are to be applied
    sheetsInModelFiltered = GetSheets(doc, sheetFilterRules)
    if(len(sheetsInModelFiltered) > 0 ):
        # set up revision
        revIdResult = AddRevToDocument(doc)
        returnValue.Update(revIdResult)
        # check what came back
        if(revIdResult.status):
            revIds = revIdResult.result
            # get sheets where revisions need to be applied to:
            revitFileName = util.GetFileNameWithoutExt(revitFilePath_)
            for fileName, sheetRules in sheetFilterRules:
                if (revitFileName.startswith(fileName)):
                    # add revisions to sheets:
                    for sheet in sheetsInModelFiltered:
                        resultAddRevisionsToSheet = rRev.AddRevisionsToSheet(doc, sheet, revIds)
                        returnValue.Update(resultAddRevisionsToSheet)
            # set revisions as issued
            resultMarkAsIssued = MarkRevisionsAsIssued(doc, revIds)
            returnValue.Update(resultMarkAsIssued)
    else:
        returnValue.UpdateSep(False, 'No sheet(s) matching filter(s) found')
    # wipe result list since it contains a mix of ids no longer required
    returnValue.result = []
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# list of revisions to be added to each model
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

# sheets to add revisions to rules 
sheetRules_ = [
    [
        'FileOne',[
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value']
        ]
    ],# applies to files FileOneOneBeforeName and FileOneTwoBeforeName
    [
        'FileTwo', [
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'],
            ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value']
        ]
    ]# applies to file FileTwoBeforeName
]

Output('Add revision.... start')

#add revision to doc and to sheet named 'Splashscreen'
result_  = AddRevsToSheetsRequired(doc, sheetRules_)
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