"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category helper functions.
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


import clr
import System
from System.Collections.Generic import List

from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import BuiltInParameter, Transaction

#: subcategory renaming sampled dictionary
#: key is the current subcategory name, value is the new subcategory name
CAT_RENAMING = {"Clearance Zones": "AMAZING"}

#: list of built in parameters attached to family elements containing subcategory ids
ELEMENTS_PARAS_SUB = [
    BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE,
    BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE_MINUS_ANALYTICAL,
    BuiltInParameter.FAMILY_ELEM_SUBCATEGORY,
    BuiltInParameter.CLINE_SUBCATEGORY,
]


def get_main_sub_categories(doc):
    """
    Returns all subcategories of the family category in a dictionary where\
        key: sub category name
        value: sub category 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: Autodesk.Revit.DB.Category}
    """

    cat_data = {}
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if main_cat.Name == family_category_name:
            # loop over all sub categories
            for sub_cat in main_cat.SubCategories:
                cat_data[sub_cat.Name] = sub_cat
    return cat_data


def does_main_sub_category_exists(doc, sub_cat_name):
    """
    Checks whether a given subcategory exists in the family.

    Note: Only subcategory directly belonging to the family category will be checked for a match.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param sub_cat_name: The name of the subcategory to be checked against.
    :type sub_cat_name: str

    :return: True if subcategory exists in family, otherwise False
    :rtype: bool
    """

    # get all sub categories belonging to family category
    sub_cats = get_main_sub_categories(doc)
    if sub_cat_name in sub_cats:
        return True
    else:
        return False


def delete_main_sub_category(doc, sub_cat_name):
    """
    Deletes a given subcategory from the family.

    Note: Only subcategory directly belonging to the family category will be checked for a match.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param sub_cat_name: The name of the subcategory to be deleted.
    :type sub_cat_name: str

    :return: True if subcategory exists in family and was deleted successfully, otherwise False
    :rtype: bool
    """

    # get all sub categories belonging to family category
    sub_cats = get_main_sub_categories(doc)
    if sub_cat_name in sub_cats:
        # delete subcategory
        status_delete = delete_by_element_ids(
            doc,
            [sub_cats[sub_cat_name].Id],
            "delete subcategory: " + sub_cat_name,
            "subcategory",
        )
        return status_delete.status
    else:
        return False


def get_family_category(doc):
    """
    Gets the family category in a dictionary where\
        key: category name
        value: category 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: Autodesk.Revit.DB.Category}
    """

    cat_data = {}
    # get the family category
    current_fam_cat = doc.OwnerFamily.FamilyCategory
    cat_data[current_fam_cat.Name] = current_fam_cat
    return cat_data


def get_other_sub_categories(doc):
    """
    Returns all family subcategories which do not belong to the actual family category.

    key: category name
    value: dictionary : key sub cat name, value: subcategory

    Note: custom subcategories have an Id greater 0

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: {str:Autodesk.Revit.DB.Category} }
    """

    cat_data = {}
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if main_cat.Name != family_category_name:
            if main_cat.Name not in cat_data:
                cat_data[main_cat.Name] = {}
            # loop over all sub categories
            for sub_cat in main_cat.SubCategories:
                cat_data[main_cat.Name][sub_cat.Name] = sub_cat

    return cat_data


def get_other_custom_sub_categories(doc):
    """
    Returns all family custom subcategories which do not belong to the actual family category.
    Custom categories have an Id greater then 0.

    key: category name
    value: dictionary : key sub cat name, value: subcategory

    Note: custom subcategories have an Id greater 0

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: {str:Autodesk.Revit.DB.Category} }
    """

    cat_data = {}
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if main_cat.Name != family_category_name:
            if main_cat.Name not in cat_data:
                cat_data[main_cat.Name] = {}
            # loop over all sub categories
            for sub_cat in main_cat.SubCategories:
                if sub_cat.Id.IntegerValue > 0:
                    cat_data[main_cat.Name][sub_cat.Name] = sub_cat
    return cat_data


def get_other_categories(doc):
    """
    Returns all family pre defined categories which do not belong to the actual family category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of categories.
    :rtype: [Autodesk.Revit.DB.Category]
    """

    cat_data = []
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for main_cat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if main_cat.Name != family_category_name:
            if main_cat not in cat_data:
                cat_data.append(main_cat)
    return cat_data


def get_category_by_built_in_def_name(doc, built_in_defs):
    """
    Returns categories by their built in definition

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_defs: list of BuiltInCategory Enumeration values
    :type built_in_defs: [Autodesk.Revit.DB.BuiltInCategory]

    :return: list of categories
    :rtype: [Autodesk.Revit.DB.Category]
    """

    cats = []
    document_settings = doc.Settings
    groups = document_settings.Categories
    for built_in_def in built_in_defs:
        cat = groups.get_Item(built_in_def)
        if cat != None:
            cats.append(cat)
    return cats


def set_family_category(doc, new_category_name):
    """
    Changes the family category to new one specified by name. (this will not re-instate any custom sub categories created under the new family category)

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param new_category_name: The name of the new family category.
    :type new_category_name: str

    :return: True only if the category was changed successfully. Any other case False! (That includes situations when the family is already of the new category)
    :rtype: bool
    """

    return_value = res.Result()
    cat = doc.OwnerFamily.FamilyCategory
    if cat.Name != new_category_name:
        if doc.Settings.Categories.Contains(new_category_name):

            def action():
                doc.OwnerFamily.FamilyCategory = doc.Settings.Categories.get_Item(
                    new_category_name
                )

            transaction = Transaction(
                doc, "Changing family category to:" + str(new_category_name)
            )
            change_cat = in_transaction(transaction, action)
            if change_cat.status:
                return_value.update_sep(
                    True,
                    "Successfully changed family category to: {}".format(
                        new_category_name
                    ),
                )
            else:
                return_value.update(change_cat)
        else:
            return_value.update_sep(
                False, "Invalid Category name supplied: {}".format(new_category_name)
            )
    else:
        return_value.update_sep(
            False, "Family is already of category: {}".format(new_category_name)
        )
    return return_value
