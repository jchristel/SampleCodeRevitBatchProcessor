"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view sheet sets. 
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


from Autodesk.Revit.DB import FilteredElementCollector, PrintRange, ViewSheet, ViewSheetSet, ViewSet


def get_view_sheet_sets(doc):
    """
    Get all view sets in the Revit document.
    :param doc: The Revit document to search for view sets.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing all view sets.
    :rtype: FilteredElementCollector
    """

    # set up a filtered element collector to get all view sets in the document
    view_sheet_set_collector = FilteredElementCollector(doc).OfClass(ViewSheetSet)
    return view_sheet_set_collector


def get_sheet_and_view_ids_from_view_sheet_set(view_sheet_set):
    """
    Extracts sheet and view IDs from a given view set.
    :param view_sheet_set: The view set from which to extract sheet and view IDs.
    :type view_sheet_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A tuple containing two lists: sheet IDs and view IDs.
    :rtype: tuple
    """

    # Initialize lists to hold sheet and view IDs
    sheet_ids = []
    view_ids = []

    # Iterate through the ordered view list in the view set
    for element_in_set in view_sheet_set.OrderedViewList:

        # Check if the element is a ViewSheet
        if (isinstance(element_in_set, ViewSheet)):
            sheet_ids.append(element_in_set.Id)
        else: 
            view_ids.append(element_in_set.Id)
    
    return (sheet_ids, view_ids)


def get_sheets_and_views_from_view_sheet_set(view_sheet_set):
    """
    Extracts sheets and views from a given view set.
    :param view_sheet_set: The view set from which to extract sheet and view IDs.
    :type view_sheet_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A tuple containing two lists: sheet IDs and view IDs.
    :rtype: tuple
    """

    # Initialize lists to hold sheet and view IDs
    sheets = []
    views = []

    # Iterate through the ordered view list in the view set
    for element_in_set in view_sheet_set.OrderedViewList:

        # Check if the element is a ViewSheet
        if (isinstance(element_in_set, ViewSheet)):
            sheets.append(element_in_set)
        else: 
            views.append(element_in_set)
    
    return (sheets, views)


def get_sheets_from_view_sheet_set(view_sheet_set):
    
    """
    Extracts only the sheets from a given view set.

    :param view_sheet_set: The view set from which to extract sheet objects.
    :type view_sheet_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of sheet objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    sheets, _ = get_sheets_and_views_from_view_sheet_set(view_sheet_set)

    # Return only the sheets
    return sheets


def get_views_from_view_sheet_set(view_sheet_set):
    
    """
    Extracts only the views from a given view set.

    :param view_sheet_set: The view set from which to extract sheet objects.
    :type view_sheet_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of view objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    _, views = get_sheets_and_views_from_view_sheet_set(view_sheet_set)

    # Return only the sheets
    return views


def get_sheet_ids_from_view_sheet_set(view_sheet_set):
    
    """
    Extracts only the sheet ids from a given view set.

    :param view_sheet_set: The view set from which to extract sheet objects.
    :type view_sheet_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of Element Id objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    sheet_ids, _ = get_sheet_and_view_ids_from_view_sheet_set(view_sheet_set)

    # Return only the sheets
    return sheet_ids


def get_view_ids_from_view_sheet_set(view_sheet_set):
    
    """
    Extracts only the view ids from a given view set.

    :param view_sheet_set: The view set from which to extract sheet objects.
    :type view_sheet_set: Autodesk.Revit.DB.ViewSheetSet

    :return: A list of Element Id objects.
    :rtype: list
    """

    # Initialize lists to hold sheet and view IDs
    _, view_ids = get_sheet_and_view_ids_from_view_sheet_set(view_sheet_set)

    # Return only the sheets
    return view_ids


def update_view_sheet_set(doc, view_sheet_set, sheets, views, clear_existing=True, transaction_manager = in_transaction):
    """
    Updates the view set with the given sheets and views.

    If either views or sheets list is empty, the function will clear the existing sheets or views if clear_existing is set to true. 
    Otherwise it will maintain those types of views unchanged (clear_existing=False).

    :param view_sheet_set: The view set to update.
    :type view_sheet_set: Autodesk.Revit.DB.ViewSheetSet
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

     # set up a return object
    return_value = Result()

    # check if the view_sheet_set is None
    if not isinstance(view_sheet_set, ViewSheetSet):
        return_value.update_sep(False, "view_sheet_set needs to be of type:  ViewSheetSet.  Got instead: {}".format(type(view_sheet_set)))
        return return_value
    
    # get the ids of what is currently in the view set
    existing_sheets, existing_views = get_sheets_and_views_from_view_sheet_set(view_sheet_set)

    # set up an action to be executed in a transaction
    def action():
        action_return_value = Result()
        
        try:

            # set up a new view set ( not ot be confused with view sheet set...)
            empty_set = ViewSet()
           
            # check if we have any sheets past in
            if sheets is None or len(sheets) == 0:
                # if no sheets are passed in, clear existing sheets
                if not clear_existing:
                    # add existing sheets back to the view set
                    for sheet in existing_sheets:
                        empty_set.Insert(sheet)
            else:
                # if sheets are passed in, add them to the view set
                for sheet in sheets:
                    empty_set.Insert(sheet)
            
            # check if we have any views past in
            if views is None or len(views) == 0:
                # if no views are passed in, clear existing views
                if not clear_existing:
                    # add existing views back to the view set
                    for view in existing_views:
                        empty_set.Insert(view)
            else:
                # if views are passed in, add them to the view set
                for view in views:
                   empty_set.Insert(view)
        
            # assign the view set to the view sheet set
            # not sure as to whether this is the correct way to do this
            view_sheet_set.Views = empty_set
            
            action_return_value.append_message("Successfully updated view set: {}".format(view_sheet_set))

        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to update view set: {} with error: {}".format(view_sheet_set, e),
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


def get_view_sheet_set_by_name(doc, view_sheet_set_name):
    """
    Retrieves a view set by its name from the Revit document.

    :param doc: The Revit document to search for the view set.
    :type doc: Autodesk.Revit.DB.Document
    :param view_sheet_set_name: The name of the view set to retrieve.
    :type view_sheet_set_name: str

    :return: The ViewSheetSet object if found, otherwise None.
    :rtype: Autodesk.Revit.DB.ViewSheetSet or None
    """

    # get all view sets in the document
    view_sheet_sets = get_view_sheet_sets(doc)

    # iterate through the view sets and return the one with the matching name
    for view_sheet_set in view_sheet_sets:
        if view_sheet_set.Name == view_sheet_set_name:
            return view_sheet_set
    
    return None


def create_new_view_sheet_set(doc, view_sheet_set_name, sheets, views, transaction_manager = in_transaction):
    """
    Creates a new view set with the given name, sheets, and views in the Revit document.

    :param doc: The Revit document in which to create the view set.
    :type doc: Autodesk.Revit.DB.Document
    :param view_sheet_set_name: The name of the new view set to create.
    :type view_sheet_set_name: str
    :param sheets: A list of sheets to include in the new view set.
    :type sheets: list
    :param views: A list of views to include in the new view set.
    :type views: list
    :param transaction_manager: The transaction manager to use for the operation. If none is provided, the action will be executed assuming there is an open transaction already set up by the caller.
    :type transaction_manager: function

    :return: A Result object indicating the success or failure of the operation.
    :rtype: duHast.Utilities.Objects.result.Result
    """
    # set up a return object
    return_value = Result()

    # check if the view_sheet_set_name is a string
    if not isinstance(view_sheet_set_name, str):
        return_value.update_sep(False, "view_sheet_set_name needs to be of type: str. Got instead: {}".format(type(view_sheet_set_name)))
        return return_value

    if view_sheet_set_name == "":
        return_value.update_sep(False, "view_sheet_set_name cannot be an empty string.")
        return return_value

    # check view set with given name already exists?
    # if it does, return an error
    # otherwise duplicate the current set, rename it , clear it and update it with the given sheets and views
    existing_view_sheet_set = get_view_sheet_set_by_name(doc, view_sheet_set_name)

    if existing_view_sheet_set:
        return_value.update_sep(False, "View set with name '{}' already exists.".format(view_sheet_set_name))
        return return_value
    
    # Access the PrintManager
    print_manager = doc.PrintManager

    # Set the PrintRange to Select - this is required!
    print_manager.PrintRange = PrintRange.Select

    # Now you can access the ViewSheetSetting
    view_sheet_setting = print_manager.ViewSheetSetting

    # set up an action to be executed in a transaction
    def action():
        action_return_value = Result()
        
        try:
            # create a new view sheet set by saving the current view sheet set with the given name
            new_view_sheet_set_flag = view_sheet_setting.SaveAs(view_sheet_set_name)

            # check if the new view set is None
            if not new_view_sheet_set_flag :
                action_return_value.update_sep(False, "Failed to create new view set.")
                return action_return_value
            
            # get the newly created view set
            new_view_sheet_set = view_sheet_setting.CurrentViewSheetSet
            
            # update the view set with the given sheets and views
            update_view_sheet_set(doc, new_view_sheet_set, sheets, views, clear_existing=True, transaction_manager=None)

            action_return_value.append_message("Successfully created new view set: {}".format(new_view_sheet_set))

            # return the newly created view set
            action_return_value.result.append(new_view_sheet_set)

        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to create new view set: {} with error: {}".format(view_sheet_set_name, e),
            )
        
        return action_return_value

    # check if a transaction manager is provided
    if not transaction_manager:
        # if no transaction manager is provided, run the action assuming there is an open transaction already set up by the caller
        return_value = action()
    else:
        transaction = Transaction(doc, "Creating view set: {}".format(view_sheet_set_name))
        return_value = transaction_manager(transaction, action)
   
    return return_value