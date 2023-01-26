'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit revisions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import clr
import System
from collections import namedtuple

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import Result as res

# import Autodesk
import Autodesk.Revit.DB as rdb

# tuples containing revision information
revisionData = namedtuple('revisionData', 'description issuedBy issuedTo revisionNumberType revisionDate tagCloudVisibility')


def CreateRevision (doc, revData):
    '''
    Creates a revision in the document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revData: Named tuple containing revision data
    :type revData: :class:`.revisionData`

    :return:  
        Result class instance.
        
        - Revision created status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision created successfully.
        - result.result: will contain list with single entry: the new revision created
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    def action():
        actionReturnValue = res.Result()
        try:
            newRevision = rdb.Revision.Create(doc)
            newRevision.Description = revData.description
            newRevision.IssuedBy = revData.issuedBy
            newRevision.IssuedTo = revData.issuedTo
            newRevision.NumberType = revData.revisionNumberType
            newRevision.RevisionDate = revData.revisionDate
            newRevision.Visibility = revData.tagCloudVisibility #rdb.RevisionVisibility.Hidden
            actionReturnValue.result.append(newRevision)
            actionReturnValue.UpdateSep(True, 'Created new revision in document.')
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed to create new revision in document with exception: ' + str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc, "adding revision to file")
    returnValue = com.InTransaction(transaction, action)
    return returnValue

def MarkRevisionAsIssued(doc, revision):
    '''
    Sets a revision status to 'Issued'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision: The revision
    :type revision: Autodesk.REvit.DB.Revision

    :return:  
        Result class instance.
        
        - Revision status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision marked as issued successfully.
        - result.result: empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    def action():
        actionReturnValue = res.Result()
        try:
            revision.Issued = True
            actionReturnValue.UpdateSep(True, 'Marked revision as issued.')
        except Exception as e:
            actionReturnValue.UpdateSep(False,'Failed to mark revision as issued with exception: '+ str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc, "Setting revision to issued")
    returnValue = com.InTransaction(transaction, action)
    return returnValue

def MarkRevisionAsIssuedByRevisionId(doc, revisionId):
    '''
    Sets a revision, identified by its id, status to 'Issued'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revisionId: The Id of the revision.
    :type revisionId: Autodesk.Revit.DB.ElementId

    :return:  
        Result class instance.
        
        - Revision marked as issued status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision marked as issued successfully.
        - result.result: empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get all revisions in file
    revsInModel = rdb.Revision.GetAllRevisionIds(doc)
    if(revisionId in revsInModel):
        # get the revision element
        revision = doc.GetElement(revisionId)
        # mark revision as issued
        returnValue = MarkRevisionAsIssued(doc, revision)
    else:
        returnValue.UpdateSep(False,'Revision with id provided does not exist in model.')
    return returnValue

def AddRevisionsToSheet(doc, sheet, revIds):
    '''
    Adds revisions to single sheet

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: The sheet to add the revision to.
    :type sheet: Autodesk.Revit.DB.SheetView
    :param revIds: List of revision ids
    :type revIds: [Autodesk.Revit.ElementId]

    :return:  
        Result class instance.
        
        - Revision adding to sheet status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision added to sheet  successfully.
        - result.result: empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get revisions already on sheet (this is important, since they need to be passed in again when adding a new revision!)
    # this call converts ids to a c# List<ElementId> : ids.ToList[ElementId]()
    ids = sheet.GetAdditionalRevisionIds()
    # add new revisions to sheet
    for revId in revIds:
        ids.Add(revId)
    # commit new revisions in a transaction
    def action():
        actionReturnValue = res.Result()
        try:
            sheet.SetAdditionalRevisionIds(ids)
            actionReturnValue.UpdateSep(True, 'Added revision(s) to sheet.')
        except Exception as e:
            actionReturnValue.UpdateSep(False,'Failed to add revision(s) to sheet with exception: '+ str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc, "adding revision to sheet")
    returnValue = com.InTransaction(transaction, action)
    return returnValue