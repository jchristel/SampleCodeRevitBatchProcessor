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
# - apply those revisions to sheets (filtered selection)
# - mark the revision(s) as issued

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
import CommonRevitAPI as com
import Utility as util
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

# returns the sheets in this file matching provided filter(s)
def GetSheets(doc, sheetFilterRules):
    results = []
    # get sheets where revisions need to be applied to:
    revitFileName = util.GetFileNameWithoutExt(revitFilePath_)
    for fileName, sheetRules in sheetFilterRules:
        if (revitFileName.startswith(fileName)):
            results = com.GetSheetsByFilters(doc, sheetRules)
            break
    return results

# adds a revision to the document
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

# marks a revisions as issued
# reIds is a list of revision id's to be marked issued
def MarkRevisonsAsIssued(doc, revIds):
    result = res.Result()
    # get all revisions in file
    revsInModel = Revision.GetAllRevisionIds(doc)
    # check against what was applied
    idsToBeMarkedIssued = set(revIds).intersection(revsInModel)
    #print (idsToBeMarkedIssued)
    for id in idsToBeMarkedIssued:
        # get the element
        revision = doc.GetElement(id)
        def action():
            revision.Issued = True
        transaction = Transaction(doc, "Setting revision to issued")
        resultSetToIssued = com.InTransaction(transaction, action)
        result.Update(resultSetToIssued)
    return result

# adds a number of revisions to the document
# revision information is stored in global list
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

# adds revisions to single sheet
def AddRevsToSheet(doc, sheet, revIds):
    result = res.Result()
    # get revisions allready on sheet (this is improtant, since they need to be passed in again when adding a new revision!)
    # this call converts ids to a c# List<ElementId> : ids.ToList[ElementId]()
    ids = sheet.GetAdditionalRevisionIds()
    for revId in revIds:
        ids.Add(revId)
    def action():
            sheet.SetAdditionalRevisionIds(ids)
    transaction = Transaction(doc, "adding revision to sheet")
    result = com.InTransaction(transaction, action)
    return result

# main function of this sample
def AddRevsToSheetsRequired(doc, sheetFilterRules):
    result = res.Result()
    # get sheet to which revisions are to be appliedß
    sheetsInModelFiltered = GetSheets(doc, sheetFilterRules)
    if(len(sheetsInModelFiltered) > 0 ):
        # set up revision
        revIdResult = AddRevToDocument(doc)
        # check what came back
        if(revIdResult.status):
            revIds = revIdResult.result
            # get sheets where revisions need to be applied to:
            revitFileName = util.GetFileNameWithoutExt(revitFilePath_)
            for fileName, sheetRules in sheetFilterRules:
                if (revitFileName.startswith(fileName)):
                    # add revisions to sheets:
                    for sheet in sheetsInModelFiltered:
                        resultAddRevoToSheet = AddRevsToSheet(doc, sheet, revIds)
                        result.Update(resultAddRevoToSheet)
            # set revisions as issued
            resultMarkasIssued = MarkRevisonsAsIssued(doc, revIds)
            result.Update(resultMarkasIssued)
        else:
            result = revIdResult
    else:
        result.UpdateSep(False, 'No sheet(s) matching filter(s) found')
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
    ['MODEL ISSUE - FOR INFORMATION','JC', RevisionNumberType.Numeric, datetime.datetime.now().strftime("%d/%m/%y")]
]

# sheets to add revisions to rules 
sheetRules_ = [
    ['FileOne',[['Parameter Name', util.ConDoesNotEqual, 'Parameter Value']]],# applies to files FileOneOneBeforeName and FileOneTwoBeforeName
    ['FileTwo', [
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value'],
        ['Parameter Name', util.ConDoesNotEqual, 'Parameter Value']
    ]]# applies to file FileTwoBeforeName
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
      Output('Add revision.... Saving non norkshared file: start')
      doc.SaveAs(revitFilePath_)
      Output('Add revision.... Saving non norkshared file: finished')

Output('Add revision.... finished ')