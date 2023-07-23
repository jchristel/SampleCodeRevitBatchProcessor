"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Varies Element filter / check functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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


import Autodesk.Revit.DB as rdb


def is_element_of_built_in_category(doc, element_id, builtin_categories):
    """
    Checks whether an element is of the built in categories past in.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: The id of the element to be tested.
    :type element_id: Autodesk.Revit.DB.ElementId
    :param builtin_categories: The builtin category the element does needs to match.
    :type builtin_categories: Autodesk.Revit.DB.Definition
    :return: True if element's builtin category does equals the test category, otherwise False.
    :rtype: bool
    """

    match = False
    el = doc.GetElement(element_id)
    enum_category_id = el.Category.Id.IntegerValue.ToString()
    for bic in builtin_categories:
        if enum_category_id == bic.value__.ToString():
            match = True
            break
    return match


def is_element_not_of_built_in_category(doc, element_id, builtin_categories):
    """
    Checks whether an element is not of the built in categories past in.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: The id of the element to be tested.
    :type element_id: Autodesk.Revit.DB.ElementId
    :param builtin_categories: The builtin category the element does not needs to match.
    :type builtin_categories: Autodesk.Revit.DB.Definition
    :return: True if element's builtin category does not equals the test category, otherwise False.
    :rtype: bool
    """

    match = True
    el = doc.GetElement(element_id)
    enum_category_id = el.Category.Id.IntegerValue.ToString()
    for bic in builtin_categories:
        if enum_category_id == bic.value__.ToString():
            match = False
            break
    return match


def is_family_name_from_instance(
    doc,
    family_name,  # type: str
    element_id,
):

    """
    Checks whether the family name of a given family instance matches filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_name: The string the name of the family needs to match.
    :type family_name: str
    :param element_id: The id of the element to be tested.
    :type element_id: Autodesk.Revit.DB.ElementId
    :return: True if family equals the test string, otherwise False.
    :rtype: bool
    """

    el = doc.GetElement(element_id)
    flag = True
    try:
        if rdb.Element.Name.GetValue(el.Symbol.Family) != family_name:
            flag = False
    except Exception:
        flag = False
    return flag


def is_family_name_from_instance_contains(
    doc,
    contains_value,  # type: str
    element_id,
):
    # type: (...) -> bool
    """
    Checks whether the family name of a given family instance contains filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains_value: The string the name of the family instance is to be tested for.
    :type ccontains_value: str
    :param element_id: The id of the element to be tested.
    :type element_id:  Autodesk.Revit.DB.ElementId
    :return: True if family name does contain the test string, otherwise False.
    :rtype: bool
    """

    el = doc.GetElement(element_id)
    flag = True
    try:
        if contains_value not in rdb.Element.Name.GetValue(el.Symbol.Family):
            flag = False
    except Exception:
        flag = False
    return flag


def is_family_name_from_instance_does_not_contains(
    doc,
    contains_value,  # type: str
    element_id,
):
    # type: (...) -> bool
    """
    Checks whether the family name of a given family instance does not contains filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains_value: The string the name of the family instance is to be tested for.
    :type contains_value: str
    :param element_id: The id of the element to be tested.
    :type element_id: Autodesk.Revit.DB.ElementId
    :return: True if family name does not contain the test string, otherwise False.
    :rtype: bool
    """

    el = doc.GetElement(element_id)
    flag = True
    try:
        if contains_value in rdb.Element.Name.GetValue(el.Symbol.Family):
            flag = False
    except Exception:
        flag = False
    return flag


def is_symbol_name_from_instance_contains(
    doc,
    contains_value,  # type: str
    element_id,
):
    # type: (...) -> bool
    """
    Checks whether the family symbol name of a given family instance contains filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains_value: The string the name of the family instance is to be tested for.
    :type contains_value: str
    :param element_id: The id of the element to be tested.
    :type element_id: Autodesk.Revit.DB.ElementId
    :return: : True if family name does contain the test string, otherwise False.
    :rtype: bool
    """

    el = doc.GetElement(element_id)
    flag = True
    try:
        if contains_value not in rdb.Element.Name.GetValue(el.Symbol):
            flag = False
    except Exception:
        flag = False
    return flag


def is_symbol_name_from_instance_does_not_contains(
    doc,
    contains_value,  # type: str
    element_id,
):
    # type: (...) -> bool

    """
    Checks whether the family symbol name of a given family instance does not contains filter value.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param contains_value: The string the name of the family is to be tested for.
    :type contains_value: string
    :param element_id: The id of the element to be tested.
    :type element_id: Autodesk.Revit.DB.ElementId
    :return: True if symbol name does not contain the test string, otherwise False.
    :rtype: bool
    """

    el = doc.GetElement(element_id)
    flag = True
    try:
        if contains_value in rdb.Element.Name.GetValue(el.Symbol):
            flag = False
    except Exception:
        flag = False
    return flag
