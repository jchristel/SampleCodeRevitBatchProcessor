"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit sub-category helper functions.
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

import Autodesk.Revit.DB as rdb

from duHast.Utilities.Objects import result as res
from duHast.Revit.Categories.categories import (
    delete_main_sub_category,
    does_main_sub_category_exists,
    get_main_sub_categories,
)
from duHast.Revit.Categories.Utility.elements_by_category_utils import (
    move_elements_from_sub_category_to_sub_category,
)
from duHast.Revit.Categories.Utility.category_properties_set_utils import (
    set_category_properties,
)
from duHast.Revit.Categories.Utility.category_properties_get_utils import (
    get_category_properties,
)
from duHast.Revit.Common import transaction as rTran


def create_new_sub_category_to_family_category(doc, new_sub_category_name):
    """
    Creates a new subcategory to the family category and returns it.

    Note: if a subcategory with the name provided already exist it will be returned instead of trying to create another one with the same name.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param new_sub_category_name: The new subcategory name
    :type new_sub_category_name: str
    :return: The new subcategory. Exception "The name 'xys' is already in use" if subcategory with the same name is already in file.
    :rtype: A category. (or str if exception occurred)
    """

    return_value = res.Result()
    if doc.IsFamilyDocument:
        # check if subcategory already exists
        if does_main_sub_category_exists(doc, new_sub_category_name):
            # just return the already existing subcategory
            main_sub_categories = get_main_sub_categories(doc)
            return_value.update_sep(True, "Subcategory already in family.")
            return_value.result = main_sub_categories[new_sub_category_name]
        else:
            # create a new subcategory
            # get the family category
            current_fam_cat = doc.OwnerFamily.FamilyCategory
            parent_category = None
            # get parent category object from Revit internal settings
            for main_cat in doc.Settings.Categories:
                if main_cat.Name == current_fam_cat.Name:
                    parent_category = main_cat
                    break
            if new_sub_category_name != parent_category.Name:

                def action():
                    action_return_value = res.Result()
                    try:
                        new_sub_category = doc.Settings.Categories.NewSubcategory(
                            parent_category, new_sub_category_name
                        )
                        action_return_value.update_sep(
                            True,
                            "Created subcategory: {}".format(new_sub_category_name),
                        )
                        action_return_value.result = new_sub_category
                    except Exception as e:
                        action_return_value.update_sep(
                            False,
                            "Failed to create: {} with exception: {}".format(
                                new_sub_category_name, e
                            ),
                        )
                    return action_return_value

                transaction = rdb.Transaction(
                    doc, "Creating subcategory: {}".format(new_sub_category_name)
                )
                return_value = rTran.in_transaction(transaction, action)
            else:
                return_value.update_sep(
                    False,
                    "Cant create subcategory with the same name as the family category!",
                )
    else:
        return_value.update_sep(False, "This is not a family document!")
    return return_value


def create_new_category_from_saved_properties(
    doc, new_cat_name, saved_cat_props, ignore_missing_cut_style=False
):
    """
    Creates a new category and applies properties stored.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param new_cat_name: The new sub category name.
    :type new_cat_name: str
    :param saved_cat_props: Dictionary containing subcategory properties.
    :type saved_cat_props: list of dictionaries in format as per GetCategoryProperties(cat) method.
    :param ignore_missing_cut_style: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignore_missing_cut_style: bool
    :return:
        Result class instance.
        - result.status. True if category was created or already existed in file, otherwise False.
        - result.message will contain the name of the category created.
        - result.result returns new category, if category already exists in file it will return that
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    result_new_sub_cat = create_new_sub_category_to_family_category(doc, new_cat_name)
    if result_new_sub_cat.status:
        new_sub_cat = result_new_sub_cat.result
        flag = set_category_properties(
            doc, new_sub_cat, saved_cat_props, ignore_missing_cut_style
        )
        if flag:
            return_value.update_sep(
                True, "Successfully created category: {}".format(new_cat_name)
            )
            return_value.result = new_sub_cat
        else:
            return_value.update_sep(
                False,
                "Failed to apply properties to new category: {}".format(new_cat_name),
            )
    else:
        return_value.update_sep(
            False, "Failed to create new subcategory: {}".format(new_cat_name)
        )
    return return_value


def create_new_category_and_transfer_properties(doc, new_cat_name, existing_cat_name):
    """
    Creates a new subcategory and transfer properties from existing subcategory.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param new_cat_name: The new sub category name.
    :type new_cat_name: str
    :param existing_cat_name: The existing subcategory name
    :type existing_cat_name: str
    :return:
        Result class instance.
        - result.status. True if category was created or already existed in file, otherwise False.
        - result.message will contain the name of the category created.
        - result.result returns new category, if category already exists in file it will return that
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    cats = get_main_sub_categories(doc)
    # check if existing category actually exists in family
    if existing_cat_name in cats:
        # check whether the new category already exists!
        if new_cat_name not in cats:
            copy_from_cat = cats[existing_cat_name]
            cat_props = get_category_properties(copy_from_cat, doc)
            result_new_sub_cat = create_new_category_from_saved_properties(
                doc, new_cat_name, cat_props
            )
            return_value.update(result_new_sub_cat)
        else:
            return_value.update_sep(
                True, "Category already in file: {}".format(new_cat_name)
            )
            return_value.result = cats[new_cat_name]
    else:
        return_value.update_sep(
            False,
            "Template category: {} does not exist in file!".format(existing_cat_name),
        )
    return return_value


def rename_sub_category(doc, old_sub_cat_name, new_sub_cat_name):
    """
    Renames a family custom subcategory.
    Note: Only subcategory directly belonging to the family category will be checked for a match.
    - Revit API does currently not allow to change a subcategory name. This method instead:
        - duplicates the old subcategory with the new name
        - moves all elements belonging to the old subcategory to the new subcategory
        - deletes the old subcategory
    - If the new subcategory already exists in the file:
        - moves all elements belonging to the old subcategory to the new subcategory
        - deletes the old subcategory

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param old_sub_cat_name: The subcategory name to be re-named
    :type old_sub_cat_name: str
    :param new_sub_cat_name: The new subcategory name.
    :type new_sub_cat_name: str
    :return:
        Result class instance.
        - result.status. True if subcategory was renamed successfully , otherwise False.
        - result.message will contain rename process messages.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # check whether ol;d subcategory exists in family file
    already_in_family_old = does_main_sub_category_exists(doc, old_sub_cat_name)
    if already_in_family_old:
        # check whether new subcategory already in family
        already_in_family = does_main_sub_category_exists(doc, new_sub_cat_name)
        if already_in_family:
            # just move elements from old sub category to new one
            return_value.append_message(
                "Subcategory: {} already in family.".format(new_sub_cat_name)
            )
        else:
            # duplicate old sub category
            create_new_status = create_new_category_and_transfer_properties(
                doc, new_sub_cat_name, old_sub_cat_name
            )
            return_value.update(create_new_status)
        # check if we have a subcategory to move elements to
        if return_value.status:
            # move elements
            move_status = move_elements_from_sub_category_to_sub_category(
                doc, old_sub_cat_name, new_sub_cat_name
            )
            return_value.update(move_status)
            if move_status.status:
                deleted_old_sub_category = delete_main_sub_category(
                    doc, old_sub_cat_name
                )
                if deleted_old_sub_category:
                    return_value.update_sep(
                        True,
                        "Subcategory: {} deleted successfully.".format(
                            old_sub_cat_name
                        ),
                    )
                else:
                    return_value.update_sep(
                        True,
                        "Subcategory: {} failed to delete subcategory...Exiting".format(
                            old_sub_cat_name
                        ),
                    )
            else:
                return_value.update_sep(
                    False,
                    "Subcategory: {} failed to move elements to new subcategory. Exiting...".format(
                        new_sub_cat_name
                    ),
                )
        else:
            return_value.update_sep(
                False,
                "Subcategory: {} failed to create in family. Exiting...".format(
                    new_sub_cat_name
                ),
            )
    else:
        return_value.update_sep(
            False,
            "Base subcategory: {} does not exist in family. Exiting...".format(
                old_sub_cat_name
            ),
        )
    return return_value
