"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view sets. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import Transaction


from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, ViewSheetSet


def get_view_sets(doc):
    """
    Get all view sets in the Revit document.
    :param doc: The Revit document to search for view sets.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing all view sets.
    :rtype: FilteredElementCollector
    """

    # set up a filtered element collector to get all view sets in the document
    view_set_collector = FilteredElementCollector(doc).OfClass(ViewSheetSet)
    return view_set_collector


def get_sheet_and_view_ids_from_view_set(view_set):
    """
    Extracts sheet and view IDs from a given view set.
    :param view_set: The view set from which to extract sheet and view IDs.
    :type view_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A tuple containing two lists: sheet IDs and view IDs.
    :rtype: tuple
    """

    # Initialize lists to hold sheet and view IDs
    sheet_ids = []
    view_ids = []

    # Iterate through the ordered view list in the view set
    for element_in_set in view_set.OrderedViewList:

        # Check if the element is a ViewSheet
        if (isinstance(element_in_set, ViewSheet)):
            sheet_ids.append(element_in_set.Id)
        else: 
            view_ids.append(element_in_set.Id)
    
    return (sheet_ids, view_ids)


def get_sheets_and_views_from_view_set(view_set):
    """
    Extracts sheets and views from a given view set.
    :param view_set: The view set from which to extract sheet and view IDs.
    :type view_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A tuple containing two lists: sheet IDs and view IDs.
    :rtype: tuple
    """

    # Initialize lists to hold sheet and view IDs
    sheets = []
    views = []

    # Iterate through the ordered view list in the view set
    for element_in_set in view_set.OrderedViewList:

        # Check if the element is a ViewSheet
        if (isinstance(element_in_set, ViewSheet)):
            sheets.append(element_in_set)
        else: 
            views.append(element_in_set)
    
    return (sheets, views)


def get_sheets_from_view_set(view_set):
    
    """
    Extracts only the sheets from a given view set.

    :param view_set: The view set from which to extract sheet objects.
    :type view_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of sheet objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    sheets, _ = get_sheets_and_views_from_view_set(view_set)

    # Return only the sheets
    return sheets


def get_views_from_view_set(view_set):
    
    """
    Extracts only the views from a given view set.

    :param view_set: The view set from which to extract sheet objects.
    :type view_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of view objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    _, views = get_sheets_and_views_from_view_set(view_set)

    # Return only the sheets
    return views


def get_sheet_ids_from_view_set(view_set):
    
    """
    Extracts only the sheet ids from a given view set.

    :param view_set: The view set from which to extract sheet objects.
    :type view_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of Element Id objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    sheet_ids, _ = get_sheet_and_view_ids_from_view_set(view_set)

    # Return only the sheets
    return sheet_ids


def get_view_ids_from_view_set(view_set):
    
    """
    Extracts only the view ids from a given view set.

    :param view_set: The view set from which to extract sheet objects.
    :type view_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of Element Id objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    _, view_ids = get_sheet_and_view_ids_from_view_set(view_set)

    # Return only the sheets
    return view_ids


def update_view_set(view_set, sheets, views, clear_existing=True, transaction_manager = in_transaction):
    """
    Updates the view set with the given sheets and views.

    If either views or sheets list is empty, the function will clear the existing sheets or views if clear_existing is set to true. 
    Otherwise it will maintain those types of views unchanged (clear_existing=False).

    :param view_set: The view set to update.
    :type view_set: Autodesk.Revit.DB.ViewSheetSet
    :param sheets: The list of sheets to add to the view set.
    :type sheets: list
    :param views: The list of views to add to the view set.
    :type views: list
    :param clear_existing: Whether to clear existing sheets or views before adding new ones.
    :type clear_existing: bool
    :param transaction_manager: The transaction manager to use for the operation. If none is provided, the action will be executed assuming there is an open transaction already set up by the caller.
    :type transaction_manager: function

    :return: A Result object indicating the success or failure of the operation.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    # check if the view_set is None
    if not isinstance(view_set, ViewSheetSet):
        raise ValueError("view_set needs to be of type:  ViewSheetSet.  Got instead: {}".format(type(view_set)))
    
    # get the ids of what is currently in the view set
    existing_sheets, existing_views = get_sheets_and_views_from_view_set(view_set)

    # set up an action to be executed in a transaction
    def action():
        action_return_value = Result()
        
        try:
            # clear the set
            view_set.Clear()

            # check if we have any sheets past in
            if sheets is None or len(sheets) == 0:
                # if no sheets are passed in, clear existing sheets
                if not clear_existing:
                    # add existing sheets back to the view set
                    for sheet in existing_sheets:
                        view_set.Insert(sheet)
            else:
                # if sheets are passed in, add them to the view set
                for sheet in sheets:
                    view_set.Insert(sheet)
            
            # check if we have any views past in
            if views is None or len(views) == 0:
                # if no views are passed in, clear existing views
                if not clear_existing:
                    # add existing views back to the view set
                    for view in existing_views:
                        view_set.Insert(view)
            else:
                # if views are passed in, add them to the view set
                for view in views:
                    view_set.Insert(view)
            
            action_return_value.append_message("Successfully updated view set: {}".format(view_set))

        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to update view set: {} with error: {}".format(view_set, e),
            )
        
        return action_return_value

    # check if a transaction manager is provided
    if not transaction_manager:
        # if no transaction manager is provided, run the action assuming there is an open transaction already set up by the caller
        return_value = action()
    else:
        transaction = Transaction(doc, "Updating view set")
        return_value = transaction_manager(transaction, action)
   
    return return_value


def create_new_view_set(doc, view_set_name, sheets, views, transaction_manager = in_transaction):
    pass