"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category helper functions for project files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
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
from System import Enum
from collections import namedtuple

from Autodesk.Revit.DB import BuiltInCategory, Category


# tuples containing categories data
category_data = namedtuple("category_data", "category_name sub_category_name id")


def get_categories_in_model(doc):
    """
    Returns all categories and subcategories in a model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of named tuples of type category_data
    :rtype: [category_data]
    """

    cats = doc.Settings.Categories
    categories = []
    for main_category in cats:
        categories.append(
            category_data(
                category_name=main_category.Name,
                sub_category_name=main_category.Name,
                id=main_category.Id,
            )
        )
        for sub_cat in main_category.SubCategories:
            categories.append(
                category_data(
                    category_name=main_category.Name,
                    sub_category_name=sub_cat.Name,
                    id=sub_cat.Id,
                )
            )

    return categories


def get_category_from_builtInCategory(doc, built_in_category):
    """
    Returns a category based on the build in category enum value.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_category: The built in category
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory
    :return: A category
    :rtype: Autodesk.Revit.DB.Category
    """

    return Category.GetCategory(doc, built_in_category)


def get_builtInCategory_from_category(doc, category):
    """
    Returns a built in category enum value based on the category object.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param category: The category object
    :type category: Autodesk.Revit.DB.Category
    :return: The built in category enum value
    :rtype: Autodesk.Revit.DB.BuiltInCategory
    """

    values = Enum.GetValues(BuiltInCategory)
    names = Enum.GetNames(BuiltInCategory)
    for value, name in zip(values, names):
        try:
            cat = Category.GetCategory(doc, value)
            if cat == None:
                continue
            if cat.Name == category.Name:
                return value
        except:
            continue
    return None


def get_category_by_names(doc, main_category_name, sub_category_name):
    """
    Retrieves a category object from a document based on the given main category name and optional sub category name.

    Args:
        doc (document object): The document object from which to retrieve the category.
        main_category_name (str): The name of the main category to search for.
        sub_category_name (str): The name of the sub category to search for within the main category.

    Returns:
        category object: The retrieved category object if a match is found.
        None: If no match is found.
    """
    return_value = None
    cats = doc.Settings.Categories
    for main_category in cats:
        if main_category.Name == main_category_name:
            if sub_category_name == main_category_name:
                return main_category
            else:
                for sub_cat in main_category.SubCategories:
                    if sub_cat.Name == sub_category_name:
                        return sub_cat
    return return_value


def get_builtin_category_by_name(category_name):
    """
    Returns the built in category enum value based on the category name.(i.e. OST_Walls)

    :param category_name: The category name
    :type category_name: str
    :return: The built in category enum value
    :rtype: Autodesk.Revit.DB.BuiltInCategory
    """

    values = Enum.GetValues(BuiltInCategory)
    names = Enum.GetNames(BuiltInCategory)
    for value, name in zip(values, names):
        if name == category_name:
            return value
    return None
