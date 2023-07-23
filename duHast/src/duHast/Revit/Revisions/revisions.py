"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit revisions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import System
from collections import namedtuple

from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import (
    transaction as rTran,
    revit_version as rRev,
    parameter_get_utils as rParaGet,
)

from duHast.Revit.Revisions import new_revision as rNewRev

# import Autodesk
import Autodesk.Revit.DB as rdb

# tuples containing revision information
REVISION_DATA = namedtuple(
    "revisionData",
    "description issued_by issued_to revision_number_type revision_date tag_cloud_visibility",
)


def create_revision(doc, revision_data):
    """
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
    """

    return_value = res.Result()

    revit_version = rRev.get_revit_version_number(doc)

    def action():
        action_return_value = res.Result()
        if revit_version <= 2022:
            action_return_value = rNewRev.new_revision_action_2022(doc, revision_data)
        else:
            action_return_value = rNewRev.new_revision_action_2023(doc, revision_data)
        return action_return_value

    transaction = rdb.Transaction(doc, "adding revision to file")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def mark_revision_as_issued(doc, revision):
    """
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
    """

    return_value = res.Result()

    def action():
        action_return_value = res.Result()
        try:
            revision.Issued = True
            action_return_value.update_sep(True, "Marked revision as issued.")
        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to mark revision as issued with exception: " + str(e)
            )
        return action_return_value

    transaction = rdb.Transaction(doc, "Setting revision to issued")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def mark_revision_as_issued_by_revision_id(doc, revision_id):
    """
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
    """

    return_value = res.Result()
    # get all revisions in file
    revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
    if revision_id in revisions_in_model:
        # get the revision element
        revision = doc.GetElement(revision_id)
        # mark revision as issued
        return_value = mark_revision_as_issued(doc, revision)
    else:
        return_value.update_sep(
            False, "Revision with id provided does not exist in model."
        )
    return return_value


def add_revisions_to_sheet(doc, sheet, revision_ids):
    """
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
    """

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
            action_return_value.update_sep(True, "Added revision(s) to sheet.")
        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to add revision(s) to sheet with exception: " + str(e)
            )
        return action_return_value

    transaction = rdb.Transaction(doc, "adding revision to sheet")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def get_issued_revisions(doc):
    """
    Get all issued revisions in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of revision objects
    :rtype: [Autodesk.Revit.DB.Revision]
    """

    issued_revisions = []
    # get all revisions in file
    revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
    for revision_id in revisions_in_model:
        rev = doc.GetElement(revision_id)
        if rev.Issued == True:
            issued_revisions.append(rev)
    return issued_revisions


def get_last_issued_revision(doc):
    """
    Get the last issued revision from a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A revision object or None if no issued revision in the model
    :rtype: Autodesk.Revit.DB.Revision or None
    """

    issued_revs = get_issued_revisions(doc)
    if len(issued_revs) > 0:
        issued_revs.sort(key=lambda x: x.SequenceNumber)
        return issued_revs[-1]
    else:
        return None


def change_revision_sequence_number(doc, revision, new_sequence_number):
    """
    Updates the revision sequence number of a revision.

    Pop the revision from its current index in the revision sequence list.
    Insert it again at the new index

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision: the revision
    :type revision: Autodesk.Revit.DB.Revision
    :param new_sequence_number: The new index (sequence number ) of the revision. 1 based!!
    :type new_sequence_number: int

    :return:
        Result class instance.

        - Revision re-ordering status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision re-ordered successfully.
        - result.result: new revision sequence list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
    """

    return_value = res.Result()
    try:
        # note revision sequence list starts with 1 with internal revision id index list starts at 0!
        new_sequence_number = new_sequence_number - 1
        revision_id = revision.Id
        revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
        if revision_id in revisions_in_model:
            # this is a c# list: List[ElementId] hence .IndexOf
            current_index = revisions_in_model.IndexOf(revision_id)
            if new_sequence_number != current_index:
                # remove the revision at the current index
                # this is a c# list: List[ElementId] hence .RemoveAt
                revisions_in_model.RemoveAt(current_index)
                # and add at the new index
                # this is a c# list: List[ElementId] hence .Insert
                revisions_in_model.Insert(new_sequence_number, revision_id)
                # update the revision sequence in the model
                return_value.update(re_order_revisions(doc, revisions_in_model))
            else:
                return_value.update_sep(
                    True,
                    "New sequence number: {} is identical to current sequence number: {}.".format(
                        new_sequence_number, current_index
                    ),
                )
        else:
            return_value.update_sep(
                False,
                "Invalid revision provided. Id {} does not exist in model revision sequence".format(
                    revision_id
                ),
            )
    except Exception as e:
        return_value.update_sep(
            False,
            "An exception occurred in change revision sequence number: {}".format(e),
        )
    return return_value


def re_order_revisions(doc, revision_sequence):
    """
    Attempts to replace the current revision sequence with the one past in.

    Note: both sequences must contain the same revisions...just in a different order.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_sequence: List of revision element ids describing the new sequence.
    :type revision_sequence: IList<ElementId>
    :return:
        Result class instance.

        - Revision re-ordering status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision re-ordered successfully.
        - result.result: new revision sequence list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    def action():
        action_return_value = res.Result()
        try:
            rdb.Revision.ReorderRevisionSequence(doc, revision_sequence)
            action_return_value.update_sep(True, "Re-ordered revisions in model.")
            action_return_value.result = rdb.Revision.GetAllRevisionIds(doc)
        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to re-order revision(s) with exception: {}".format(e)
            )
        return action_return_value

    transaction = rdb.Transaction(doc, "Re-ordering revisions in model.")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


# ---------------------------------------- deleting revisions --------------------------------------------


def _check_Revision_against_filters(revision, revision_description_filter):
    """
    Checks a revision against a list of revision filters and returns the outcome of all checks.

    :param revision: The revision to be checked
    :type revision: Autodesk.Revit.DB.Revision
    :param revision_description_filter: List of revision filters (refer to REVISION_KEEP_RULES at end of script)
    :type revision_description_filter: [parameter name, comparison function, comparison value]

    :return: A boolean representing the outcome of all checks performed (logical AND)
    :rtype: bool
    """

    paras = revision.GetOrderedParameters()
    rule_match = True
    for para_name, para_condition, condition_value in revision_description_filter:
        for p in paras:
            if p.Definition.Name == para_name:
                match = rParaGet.check_parameter_value(
                    p, para_condition, condition_value
                )
                rule_match = rule_match and match
    return rule_match


def delete_all_revisions_in_model(doc, revision_description_filter=[]):
    """
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
    """

    return_value = res.Result()
    to_delete = []
    filtered_at_least_one = False
    revisions = rdb.FilteredElementCollector(doc).OfClass(rdb.Revision)
    for rev in revisions:
        if len(revision_description_filter) > 0:
            ruleMatch = _check_Revision_against_filters(
                rev, revision_description_filter
            )
            if ruleMatch == True:
                # delete view
                to_delete.append(rev.Id)
                return_value.append_message(
                    "Revision: {} {} will be deleted.".format(
                        rev.Description, rev.RevisionDate
                    )
                )
            else:
                filtered_at_least_one = True
                return_value.append_message(
                    "Revision: {} {} will not be deleted.".format(
                        rev.Description, rev.RevisionDate
                    )
                )
        else:
            to_delete.append(rev.Id)
            return_value.append_message(
                "Revision: {} {} will be deleted.".format(
                    rev.Description, rev.RevisionDate
                )
            )

    # check if any revisions to delete
    if len(to_delete) > 0:
        # check if at least one revision was filtered out and will therefore remain in the file
        # if not remove one manually since Revit requires at least one revision in the file
        if filtered_at_least_one == False:
            # one revision need to stay in file...
            to_delete.pop()
            return_value.append_message(
                "Removing at one revision from selection since Revit requires at least one revision in the model."
            )

        # delete them
        def action():
            action_return_value = res.Result()
            action_return_value.append_message(
                "Attempting to delete revisions: {}".format(len(to_delete))
            )
            try:
                doc.Delete(to_delete.ToList[rdb.ElementId]())
                action_return_value.append_message(
                    "Deleted {} revisions.".format(len(to_delete))
                )
            except Exception as e:
                action_return_value.update_sep(
                    False, "Failed to delete revisions with exception: {}".format(e)
                )
            return action_return_value

        transaction = rdb.Transaction(doc, "Deleting Revisions")
        return_value.update(rTran.in_transaction(transaction, action))
    else:
        return_value.update_sep(
            False, "Only one revision in file which can not be deleted!"
        )
    return return_value
