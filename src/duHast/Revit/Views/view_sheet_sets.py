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


from Autodesk.Revit.DB import Element, FilteredElementCollector, PrintRange, ViewSheet, ViewSheetSet, ViewSet


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


def get_current_view_sheet_settings_element(doc):
    """
    Retrieves the current ViewSheetSetting element from the Revit document.

    :param doc: The Revit document from which to retrieve the ViewSheetSetting.
    :type doc: Autodesk.Revit.DB.Document
    :return: The ViewSheetSetting element if found, otherwise None.
    :rtype: Autodesk.Revit.DB.ViewSheetSetting or None
    """

    # Access the PrintManager
    print_manager = doc.PrintManager

    # Set the PrintRange to Select - this is required!
    print_manager.PrintRange = PrintRange.Select

    # Now you can access the ViewSheetSetting
    view_sheet_setting = print_manager.ViewSheetSetting

    return view_sheet_setting


def update_view_sheet_set(doc, view_sheet_set, view_sheet_setting, sheets, views, clear_existing=True, transaction_manager = in_transaction, save_after_update=True):
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

    :return: A Result object indicating the success or failure of the operation. Messages are quite detailed to allow for debugging and understanding what is happening in the function.
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

    # store the name
    view_sheet_set_name = view_sheet_set.Name

    # check if the view_sheet_setting is None
    if view_sheet_setting is None:
        return_value.append_message("No view_sheet_setting provided, trying to get the current ViewSheetSetting element from the document.")
        view_sheet_setting = get_current_view_sheet_settings_element(doc)

    # make sure the we got the settings, otherwise we cant update
    if view_sheet_setting:
        return_value.append_message("Setting current view sheet set to: {}".format(view_sheet_set_name))
        view_sheet_setting.CurrentViewSheetSet = view_sheet_set
    else:
        return_value.update_sep(False, "Failed to get current ViewSheetSetting element.")
        return return_value

    # set up an action to be executed in a transaction
    def action():
        action_return_value = Result()
        
        try:

            # set up a new view set ( not ot be confused with view sheet set...)
            empty_set = ViewSet()
           
            # check if we have any sheets past in
            if sheets is None or len(sheets) == 0:
                action_return_value.append_message("No sheets provided")
                # if no sheets are passed in, clear existing sheets
                if not clear_existing:
                    action_return_value.append_message("adding existing sheets back to the view set")
                    # add existing sheets back to the view set
                    for sheet in existing_sheets:
                        action_return_value.append_message("Adding existing sheet: {}".format(Element.Name.GetValue(sheet)))
                        empty_set.Insert(sheet)
                else:
                    action_return_value.append_message("Not adding existing sheets back to the view set, as clear_existing is set to True")
                   
            else:
                action_return_value.append_message("Adding sheets past in to the view set")
                # if sheets are passed in, add them to the view set
                for sheet in sheets:
                    action_return_value.append_message("Adding sheet: {}".format(Element.Name.GetValue(sheet)))
                    empty_set.Insert(sheet)
            
            # check if we have any views past in
            if views is None or len(views) == 0:
                action_return_value.append_message("No views provided")
                # if no views are passed in, clear existing views
                if not clear_existing:
                    action_return_value.append_message("Adding existing views back to the view set")
                    # add existing views back to the view set
                    for view in existing_views:
                        action_return_value.append_message("Adding existing view: {}".format(Element.Name.GetValue(view)))
                        empty_set.Insert(view)
            else:
                action_return_value.append_message("Adding views past in to the view set")
                # if views are passed in, add them to the view set
                for view in views:
                    action_return_value.append_message("Adding view: {}".format(Element.Name.GetValue(view)))
                    empty_set.Insert(view)
        
            # assign the view set to the view sheet set
            action_return_value.append_message("Assigning the view set to the view sheet set: {}".format(view_sheet_set_name))
            #for element in empty_set:
            #    action_return_value.append_message("Element in view set: {}".format(Element.Name.GetValue(element)))
            
            # need to update the CurrentViewSheetSet views directly via the settings
            # otherwise update does not stick!
            view_sheet_setting.CurrentViewSheetSet.Views = empty_set

            # print the current view sheet set
            #for sheet in view_sheet_setting.CurrentViewSheetSet.Views:
            #    action_return_value.append_message("Sheet in current view sheet set: {}".format(Element.Name.GetValue(sheet)))

            # save the view sheet set
            save_flag = True
            
            if save_after_update:
                try:
                    
                    # print the current view sheet set
                    action_return_value.append_message("Current view sheet set: {}".format(view_sheet_setting.CurrentViewSheetSet.Name))
                    #for sheet in view_sheet_setting.CurrentViewSheetSet.OrderedViewList:
                    #    action_return_value.append_message("Sheet in current view sheet set: {}".format(Element.Name.GetValue(sheet)))


                    # this can throw an exception if the set is unchanged...
                    save_flag = view_sheet_setting.Save()
                except Exception as ex:
                    action_return_value.append_message("Failed to save the updated view sheet set: {} with error: {}".format(view_sheet_set_name, ex))

            # update the action return value with the result of the save operation
            action_return_value.append_message("Updated view set: {} with status: {}".format(view_sheet_set_name, save_flag))

            # return the newly created view set
            action_return_value.result.append(view_sheet_set)

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
        transaction = Transaction(doc, "Updating view set {}".format(view_sheet_set_name))
        return_value = transaction_manager(transaction, action)
   
    return return_value


def update_view_sheet_set_by_name(doc, view_sheet_set_name, sheets, views, clear_existing=True, transaction_manager = in_transaction):
    """
    Updates a view set with the given name, sheets, and views in the Revit document.

    :param doc: The Revit document in which to update the view set.
    :type doc: Autodesk.Revit.DB.Document
    :param view_sheet_set_name: The name of the view set to update.
    :type view_sheet_set_name: str
    :param sheets: A list of sheets to include in the view set.
    :type sheets: list
    :param views: A list of views to include in the view set.
    :type views: list
    :param clear_existing: Whether to clear existing sheets or views before adding new ones.
    :type clear_existing: bool
    :param transaction_manager: The transaction manager to use for the operation. If none is provided, the action will be executed assuming there is an open transaction already set up by the caller.
    :type transaction_manager: function

    :return: A Result object indicating the success or failure of the operation. Messages are quite detailed to allow for debugging and understanding what is happening in the function.
                if the view set does not exist, the result will contain the name of the view set that was not found. ( that is the only time the result will contain as single string)
    :rtype: duHast.Utilities.Objects.result.Result
    """

    # set up a return object
    return_value = Result()

    try:

        # check if the view_sheet_set_name is a string
        if not isinstance(view_sheet_set_name, str):
            return_value.update_sep(False, "view_sheet_set_name needs to be of type: str. Got instead: {}".format(type(view_sheet_set_name)))
            return return_value

        if view_sheet_set_name == "":
            return_value.update_sep(False, "view_sheet_set_name cannot be an empty string.")
            return return_value

        # check view set with given name already exists?
        # if it does not, return an error
        existing_view_sheet_set = get_view_sheet_set_by_name(doc, view_sheet_set_name)

        # check if the view sheet set exists
        if not existing_view_sheet_set:
            return_value.update_sep(False, "View set with name '{}' does not exist.".format(view_sheet_set_name))
            return_value.result.append(view_sheet_set_name)
            return return_value

        # Now you can access the ViewSheetSetting
        view_sheet_setting = get_current_view_sheet_settings_element(doc)

        # check if the view_sheet_setting is None
        if not view_sheet_setting:
            return_value.update_sep(False, "Failed to get current ViewSheetSetting element.")
            return return_value
        
        # update the view set with the given sheets and views
        return_value = update_view_sheet_set(
            doc=doc, 
            view_sheet_set= existing_view_sheet_set, 
            view_sheet_setting=view_sheet_setting, 
            sheets=sheets, 
            views= views, 
            clear_existing=True, 
            transaction_manager = in_transaction, 
            save_after_update=True
        )

    except Exception as e:
        return_value.update_sep(False, "Failed to update view set with name: {} with error: {}".format(view_sheet_set_name, e))


    return return_value


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

    :return: A Result object indicating the success or failure of the operation. Messages are quite detailed to allow for debugging and understanding what is happening in the function.
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

    # Now you can access the ViewSheetSetting
    view_sheet_setting = get_current_view_sheet_settings_element(doc)

    # check if the view_sheet_setting is None
    if not view_sheet_setting:
        return_value.update_sep(False, "Failed to get current ViewSheetSetting element.")
        return return_value


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
            update_status = update_view_sheet_set(
                doc, 
                new_view_sheet_set,
                view_sheet_setting,
                sheets, 
                views, 
                clear_existing=True, 
                transaction_manager=None, 
                save_after_update=False
            )

            # check if successful update
            if not update_status.status:
                action_return_value.update_sep(False, "Failed to update new view set: {} with error: {}".format(view_sheet_set_name, update_status.message))
                return action_return_value

            action_return_value.update(update_status)
            save_flag = True

            try:
                # save the set
                # this can throw an exception if the set is unchanged...
                save_flag = view_sheet_setting.Save()
            except Exception as ex:
                action_return_value.append_message("Failed to save newly created view sheet set: {} with error: {} ".format(view_sheet_set_name, ex))

            # update the action return value with the result of the save operation
            action_return_value.append_message("Created new view set: {} with status: {}".format(view_sheet_set_name, save_flag))

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


def delete_view_sheet_set_by_name(doc, view_sheet_set_name, transaction_manager = in_transaction):
    """
    Deletes a view sheet set by its name from the Revit document.

    :param doc: The Revit document from which to delete the view sheet set.
    :type doc: Autodesk.Revit.DB.Document
    :param view_sheet_set_name: The name of the view sheet set to delete.
    :type view_sheet_set_name: str
    :param transaction_manager: The transaction manager to use for the operation. If none is provided, the action will be executed assuming there is an open transaction already set up by the caller.
    :type transaction_manager: function

    :return: A Result object indicating the success or failure of the operation. Messages are quite detailed to allow for debugging and understanding what is happening in the function.
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

    view_sheet_setting = get_current_view_sheet_settings_element(doc)

    # check view set with given name already exists?
    # if it does, return an error
    # otherwise duplicate the current set, rename it , clear it and update it with the given sheets and views
    existing_view_sheet_set = get_view_sheet_set_by_name(doc, view_sheet_set_name)

    # check if the view sheet set exists
    if not existing_view_sheet_set:
        return_value.update_sep(False, "View set with name '{}' does not exist.".format(view_sheet_set_name))
        return return_value

    # make sure the we got the settings, otherwise we cant update
    if view_sheet_setting:
        return_value.append_message("Setting current view sheet set to: {}".format(view_sheet_set_name))
    else:
        return_value.update_sep(False, "Failed to get current ViewSheetSetting element.")
        return return_value
    
    # set up an action to be executed in a transaction
    def action():
        action_return_value = Result()
        
        try:
            # set the current view sheet set to the one we want to delete
            view_sheet_setting.CurrentViewSheetSet = existing_view_sheet_set
            # attempt to delete the view sheet set
            view_sheet_setting.Delete()

            action_return_value.append_message("Deleted view sheet set: {}".format(view_sheet_set_name))

        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to delete view set: {} with error: {}".format(view_sheet_set_name, e),
            )
        
        return action_return_value

    # check if a transaction manager is provided
    if not transaction_manager:
        # if no transaction manager is provided, run the action assuming there is an open transaction already set up by the caller
        return_value = action()
    else:
        transaction = Transaction(doc, "Deleting view set: {}".format(view_sheet_set_name))
        return_value = transaction_manager(transaction, action)
   
    return return_value