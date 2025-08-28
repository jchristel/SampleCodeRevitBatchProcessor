# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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
from duHast.pyRevit.console_output import print_header, print_error
from duHast.Revit.Views.view_sheet_sets import delete_view_sheet_set_by_name, create_new_view_sheet_set,update_view_sheet_set
from duHast.pyRevit.net_dll_loader import load_net_dll_path

from Autodesk.Revit.DB import ElementId

def get_sheets_from_print_set(doc, print_set):
    """
    Get sheets from a print set.

    :param doc: The document containing the print set.
    :param printSet: The print set to get sheets from.

    :return: List of sheet elements in the print set.
    """

    # set up a status tracker
    return_value = Result()
    try:
        for sheet_data in print_set.RevitSheets:
            return_value.append_data(sheet_data)
            revit_sheet = doc.GetElement(ElementId(int(sheet_data.RevitElementId.Value)))
            return_value.result.append(revit_sheet)

    except Exception as e:
        # handle any exceptions that occur during the retrieval process
        message = "An error occurred while retrieving sheets from print set '{}': {}".format(print_set.Name, e)
        return_value.update_sep(
            False, message
        )
        print_error(message)

    return return_value



def delete_print_sets(doc, print_sets):
    """
    Delete print sets from the document.

    :param doc: The document containing print sets to delete.
    :param printSets: A list of print sets to delete.

    :return: Result object indicating success or failure.
    """

    # set up a status tracker
    return_value = Result()
    try:
        # loop over sets and delete them
        for print_set in print_sets:
            # get the set name
            print_set_name = print_set.Name
            # delete the set
            delete_result = delete_view_sheet_set_by_name(doc, print_set_name)
            # give user feedback
            print(delete_result.message)
            # log result
            return_value.update(delete_result)

    except Exception as e:
        # handle any exceptions that occur during the deletion process
        message = "An error occurred while deleting print sets: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)

    return return_value


def create_print_sets(doc, print_sets):
    """
    Create print sets in the document.

    :param doc: The document containing print sets to create.
    :type doc: Autodesk.Revit.DB.Document
    :param printSets: A list of print sets to create.
    :type printSets: list

    :return: Result object indicating success or failure.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()
    try:
        # loop over sets and delete them
        for print_set in print_sets:
            # get the set name
            print_set_name = print_set.Name

            # get sheet elements
            sheets_result = get_sheets_from_print_set(doc, print_set)

            # check if successful
            if not sheets_result.status:
                return_value.update(sheets_result)
                print_error(sheets_result.message)
                continue

            if len(sheets_result.result) == 0:
                message = "No sheets found for print set '{}'.".format(print_set_name)
                return_value.update_sep(False, message)
                print_error(message)
                continue
            
            # create the set
            create_result = create_new_view_sheet_set(
                doc=doc, 
                view_sheet_set_name=print_set_name, 
                sheets = sheets_result.result, 
                views=None
            )

            # give user feedback
            print(create_result.message)
            # log result
            return_value.update(create_result)
        
    except Exception as e:
        # handle any exceptions that occur during the creation process
        message = "An error occurred while creating print sets: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)
    return return_value


def update_print_sets(doc, print_sets):
    # set up a status tracker
    return_value = Result()
    try:
        pass
    except Exception as e:
        # handle any exceptions that occur during the update process
        message = "An error occurred while updating print sets: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)
    return return_value


def update_print_sets_from_ui(doc, printSets=None):
    """
    Update print sets from the UI.
    
   
    
    :param doc: The document containing print sets to update.
    """

    # set up a status tracker
    return_value = Result()
    try:

        # load .net interface dlls
        set_dll_path_result = load_net_dll_path([ "PDFDWGExporterSelectionUI.dll"]) #"Utils.23.0.0.3.dll",

        # check if the dlls were loaded successfully
        if not set_dll_path_result.status:
            print_error(set_dll_path_result.message)
            return_value.update_sep(False, set_dll_path_result.message)
            return return_value

        # import the UI class from the PDFDWGExporterUI namespace
        from duHastNet.UI.PDFDWGExporterSelectionUI.Models import PrintSetUpdateType

        # get the sheets sets from the settings object and check for any sets to update
        print_header("Updating print sets from UI")

        # check if printSets is None or empty
        if printSets is None or len(printSets) == 0:
            message = "No print sets to update."
            return_value.update_sep(
                True, message
            )
            print(message)
            return return_value

        print_set_delete = []
        print_set_update = []
        print_set_create = []

        for print_set in printSets:
            # sort print set actions
            if print_set.UpdateAction == PrintSetUpdateType.Delete:
                print_set_delete.append(print_set)
            elif print_set.UpdateAction == PrintSetUpdateType.Update:
                print_set_update.append(print_set)
            elif print_set.UpdateAction == PrintSetUpdateType.New:
                print_set_create.append(print_set)
        
        if len(print_set_delete) > 0:
            print_header("Deleting print sets")
            delete_result = delete_print_sets(doc, print_set_delete)
            return_value.update(delete_result)
        else:
            print("No print sets to delete.")
            return_value.append_message(
                 "No print sets to delete."
            )
        
        if len(print_set_update) > 0:
            print_header("Updating print sets")
            update_result = update_print_sets(doc, print_set_update)
            return_value.update(update_result)
        else:
            print("No print sets to update.")
            return_value.append_message(
                 "No print sets to update."
            )
        
        if len(print_set_create) > 0:
            print_header("Creating print sets")
            create_result = create_print_sets(doc, print_set_create)
            return_value.update(create_result)
        else:
            print("No print sets to create.")
            return_value.append_message(
                 "No print sets to create."
            )


    except Exception as e:
        # handle any exceptions that occur during the update process
        message = "An error occurred while updating print sets: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    return return_value