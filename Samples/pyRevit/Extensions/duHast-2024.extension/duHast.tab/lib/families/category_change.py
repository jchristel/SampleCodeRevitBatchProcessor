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

from duHast.pyRevit.console_output import print_header
from duHast.pyRevit.ui_element_selection import get_element_selection_from_user
from duHast.Revit.Categories.change_family_category import change_family_category
from duHast.Revit.Categories.categories import get_category_by_id, get_available_categories_depending_on_category_type_owner



def ui_category_name_builder(element):
    """
    Builds the name for the category selection dialog.

    :param element: Category to build the name for.
    :type element: Category

    :return: Name of the category.
    :rtype: str
    """

    return element.Name


def change_category_entry(doc, output, forms):
    """
    Changes the category of the open family to the selected category.
    Preserves any subcategories in the process and re-assigns elements to the new categories to maintain the family structure.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # check if the document is a family document
        if not doc.IsFamilyDocument:
            message = "This is not a family document."
            print(message)
            return_value.update_sep(False, message)
            return return_value
        
        # get the user to select the new category
        new_category_selection = get_element_selection_from_user(
            doc=doc, 
            forms = forms, 
            element_getter=get_available_categories_depending_on_category_type_owner,
            element_selection_description = "Select new category",
            multiselect = False, 
            ui_element_name_builder = ui_category_name_builder,
        )
        
        # check if the user selected a category
        if new_category_selection is None:
            message = "No target category selected."
            print(message)
            return_value.update_sep(False, message)
            return return_value
        
        # get the selected category
        print_header("Selected Category")
        target_category_id =  new_category_selection[0]
        # get the category from the Id
        target_category = get_category_by_id(doc, target_category_id)
        if target_category is None:
            message = "Failed to get target category."
            print(message)
            return_value.update_sep(False, message)
            return return_value
        
        # time to swap
        print("Attempting to change category to: {}".format(target_category.Name))
        change_result = change_family_category(doc, target_category.Name)

        # check if the category change was successful
        if change_result.status:
            message = "Successfully changed category to: {}".format(target_category.Name)
            print(message)
            return_value.update_sep(True, message)
        else:
            message = "Failed to change category with message: {}".format(change_result.message)
            print(message)
            return_value.update_sep(False, message)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to change family category with exception: {}".format(e)
        )

    print("Finished!")

    return return_value
