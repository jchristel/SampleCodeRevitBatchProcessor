'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Varies Element filter / check functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import Autodesk.Revit.DB as rdb


def IsElementOfBuiltInCategory(doc, elId, builtinCategories):
    '''
    Checks whether an element is of the built in categories past in.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elId: The id of the element to be tested.
    :type elId: Autodesk.Revit.DB.ElementId
    :param builtinCategories: The builtin category the element does needs to match.
    :type builtinCategories: Autodesk.Revit.DB.Definition
    :return: True if element's builtin category does equals the test category, otherwise False.
    :rtype: bool
    '''

    match = False
    el = doc.GetElement(elId)
    enumCategoryId = el.Category.Id.IntegerValue.ToString()
    for bic in builtinCategories:
        if (enumCategoryId == bic.value__.ToString()):
            match = True
            break
    return match


def IsElementNotOfBuiltInCategory(doc, elId, builtinCategories):
    '''
    Checks whether an element is not of the built in categories past in.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elId: The id of the element to be tested.
    :type elId: Autodesk.Revit.DB.ElementId
    :param builtinCategories: The builtin category the element does not needs to match.
    :type builtinCategories: Autodesk.Revit.DB.Definition
    :return: True if element's builtin category does not equals the test category, otherwise False.
    :rtype: bool
    '''

    match = True
    el = doc.GetElement(elId)
    enumCategoryId = el.Category.Id.IntegerValue.ToString()
    for bic in builtinCategories:
        if (enumCategoryId == bic.value__.ToString()):
            match = False
            break
    return match


def IsFamilyNameFromInstance(
    doc,
    familyName, # type: str
    elementId
    ):

    '''
    Checks whether the family name of a given family instance matches filter value.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param familyName: The string the name of the family needs to match.
    :type familyName: str
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    :return: True if family equals the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(rdb.Element.Name.GetValue(el.Symbol.Family) != familyName):
            flag = False
    except Exception:
        flag = False
    return flag


def IsFamilyNameFromInstanceContains(
    doc,
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool
    '''
    Checks whether the family name of a given family instance contains filter value.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family instance is to be tested for.
    :type containsValue: str
    :param elementId: The id of the element to be tested.
    :type elementId:  Autodesk.Revit.DB.ElementId
    :return: True if family name does contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue not in rdb.Element.Name.GetValue(el.Symbol.Family)):
            flag = False
    except Exception:
        flag = False
    return flag


def IsFamilyNameFromInstanceDoesNotContains(
    doc,
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool
    '''
    Checks whether the family name of a given family instance does not contains filter value.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family instance is to be tested for.
    :type containsValue: str
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    :return: True if family name does not contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue in rdb.Element.Name.GetValue(el.Symbol.Family)):
            flag = False
    except Exception:
        flag = False
    return flag


def IsSymbolNameFromInstanceContains(
    doc,
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool
    '''
    Checks whether the family symbol name of a given family instance contains filter value.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family instance is to be tested for.
    :type containsValue: str
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    :return: : True if family name does contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue not in rdb.Element.Name.GetValue(el.Symbol)):
            flag = False
    except Exception:
        flag = False
    return flag


def IsSymbolNameFromInstanceDoesNotContains(
    doc,
    containsValue, # type: str
    elementId
    ):
    # type: (...) -> bool

    '''
    Checks whether the family symbol name of a given family instance does not contains filter value.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param containsValue: The string the name of the family is to be tested for.
    :type containsValue: string
    :param elementId: The id of the element to be tested.
    :type elementId: Autodesk.Revit.DB.ElementId
    :return: True if symbol name does not contain the test string, otherwise False.
    :rtype: bool
    '''

    el = doc.GetElement(elementId)
    flag = True
    try:
        if(containsValue in rdb.Element.Name.GetValue(el.Symbol)):
            flag = False
    except Exception:
        flag = False
    return flag