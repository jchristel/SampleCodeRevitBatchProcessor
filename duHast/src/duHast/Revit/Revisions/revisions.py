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
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

#import System
from collections import namedtuple

from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Utilities import result as res
from duHast.Revit.Common import transaction as rTran

# import Autodesk
import Autodesk.Revit.DB as rdb

# tuples containing revision information
REVISION_DATA = namedtuple('revisionData', 'description issuedBy issuedTo revisionNumberType revisionDate tagCloudVisibility')


def create_revision (doc, revision_data):
    '''
    Creates a revision in the document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_data: Named tuple containing revision data
    :type revision_data: :class:`.revisionData`

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

    return_value = res.Result()
    def action():
        action_return_value = res.Result()
        try:
            new_revision = rdb.Revision.Create(doc)
            new_revision.Description = revision_data.description
            new_revision.IssuedBy = revision_data.issuedBy
            new_revision.IssuedTo = revision_data.issuedTo
            new_revision.NumberType = revision_data.revisionNumberType
            new_revision.RevisionDate = revision_data.revisionDate
            new_revision.Visibility = revision_data.tagCloudVisibility #rdb.RevisionVisibility.Hidden
            action_return_value.result.append(new_revision)
            action_return_value.update_sep(True, 'Created new revision in document.')
        except Exception as e:
            action_return_value.update_sep(False, 'Failed to create new revision in document with exception: ' + str(e))
        return action_return_value
    transaction = rdb.Transaction(doc, "adding revision to file")
    return_value = rTran.in_transaction(transaction, action)
    return return_value

def mark_revision_as_issued(doc, revision):
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

    return_value = res.Result()
    def action():
        action_return_value = res.Result()
        try:
            revision.Issued = True
            action_return_value.update_sep(True, 'Marked revision as issued.')
        except Exception as e:
            action_return_value.update_sep(False,'Failed to mark revision as issued with exception: '+ str(e))
        return action_return_value
    transaction = rdb.Transaction(doc, "Setting revision to issued")
    return_value = rTran.in_transaction(transaction, action)
    return return_value

def mark_revision_as_issued_by_revision_id(doc, revision_id):
    '''
    Sets a revision, identified by its id, status to 'Issued'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_id: The Id of the revision.
    :type revision_id: Autodesk.Revit.DB.ElementId

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

    return_value = res.Result()
    # get all revisions in file
    revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
    if(revision_id in revisions_in_model):
        # get the revision element
        revision = doc.GetElement(revision_id)
        # mark revision as issued
        return_value = mark_revision_as_issued(doc, revision)
    else:
        return_value.update_sep(False,'Revision with id provided does not exist in model.')
    return return_value

def add_revisions_to_sheet(doc, sheet, revision_ids):
    '''
    Adds revisions to single sheet

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: The sheet to add the revision to.
    :type sheet: Autodesk.Revit.DB.SheetView
    :param revision_ids: List of revision ids
    :type revision_ids: [Autodesk.Revit.ElementId]

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

    return_value = res.Result()
    # get revisions already on sheet (this is important, since they need to be passed in again when adding a new revision!)
    # this call converts ids to a c# List<ElementId> : ids.ToList[ElementId]()
    ids = sheet.GetAdditionalRevisionIds()
    # add new revisions to sheet
    for revision_id in revision_ids:
        ids.Add(revision_id)
    # commit new revisions in a transaction
    def action():
        action_return_value = res.Result()
        try:
            sheet.SetAdditionalRevisionIds(ids)
            action_return_value.update_sep(True, 'Added revision(s) to sheet.')
        except Exception as e:
            action_return_value.update_sep(False,'Failed to add revision(s) to sheet with exception: '+ str(e))
        return action_return_value
    transaction = rdb.Transaction(doc, "adding revision to sheet")
    return_value = rTran.in_transaction(transaction, action)
    return return_value

# ---------------------------------------- deleting revisions --------------------------------------------

def _check_Revision_against_filters(revision, revision_description_filter):
    '''
    Checks a revision against a list of revision filters and returns the outcome of all checks.

    :param revision: The revision to be checked
    :type revision: Autodesk.Revit.DB.Revision
    :param revision_description_filter: List of revision filters (refer to REVISION_KEEP_RULES at end of script)
    :type revision_description_filter: [parameter name, comparison function, comparison value]
    
    :return: A boolean representing the outcome of all checks performed (logical AND)
    :rtype: bool
    '''

    paras = revision.GetOrderedParameters()
    rule_match = True
    for para_name, para_condition, condition_value in revision_description_filter:
        for p in paras:
            if(p.Definition.Name == para_name):
                match = rParaGet.check_parameter_value(p, para_condition, condition_value)
                rule_match = rule_match and match
    return rule_match

def delete_all_revisions_in_model(doc, revision_description_filter = []):
    '''
    Deletes all revision in file passing filter in one transaction.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param revision_description_filter: list of filters, defaults to []
    :type revision_description_filter: list, optional

    :return: 
        Result class instance.

        - result.status. True if all possible revisions where deleted successfully, otherwise False.
        - result.message will contain the name(s) of the revisions excluded by filter and number of revisions deleted.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    to_delete = []
    filtered_at_least_one = False
    revisions = rdb.FilteredElementCollector(doc).OfClass(rdb.Revision)
    for rev in revisions:
        if(len(revision_description_filter) > 0):
            ruleMatch = _check_Revision_against_filters(rev, revision_description_filter)
            if (ruleMatch == True):
                # delete view
                to_delete.append(rev.Id)
                return_value.append_message('Revision: {} {} will be deleted.'.format(rev.Description, rev.RevisionDate))
            else:
                filtered_at_least_one = True
                return_value.append_message('Revision: {} {} will not be deleted.'.format(rev.Description, rev.RevisionDate))
        else:
            to_delete.append(rev.Id)
            return_value.append_message('Revision: {} {} will be deleted.'.format(rev.Description, rev.RevisionDate))
       
    # check if any revisions to delete
    if(len(to_delete) > 0 ): 
        # check if at least one revision was filtered out and will therefore remain in the file
        # if not remove one manually since Revit requires at least one revision in the file
        if(filtered_at_least_one == False):
            # one revision need to stay in file...
            to_delete.pop()
            return_value.append_message('Removing at one revision from selection since Revit requires at least one revision in the model.')
        # delete them 
        def action():
            action_return_value = res.Result()
            action_return_value.append_message ('Attempting to delete revisions: {}'.format(len(to_delete)))
            try:
                doc.Delete(to_delete.ToList[rdb.ElementId]())
                action_return_value.append_message('Deleted {} revisions.'.format(len(to_delete)))              
            except Exception as e:
                action_return_value.update_sep(False, 'Failed to delete revisions with exception: {}'.format(e))
            return action_return_value
        transaction = rdb.Transaction(doc, 'Deleting Revisions')
        return_value.update(rTran.in_transaction(transaction, action))
    else:
        return_value.update_sep(False, 'Only one revision in file which can not be deleted!')
    return return_value