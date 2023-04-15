'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit purge utility functions.
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

from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet


def build_category_dictionary(doc, elementIds):
    '''
    Builds a dictionary from elementId s past in.
    Dictionary key is the element category and values are all the elements of that category.
    If no category can be found the key 'invalid category' will be used.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elementIds: List of element id of which to build the dictionary from.
    :type elementIds: list of AutoDesk.Revit.DB.ElementId
    :return: Dictionary key is the element category and values are all the elements of that category.
    :rtype: dictionary, key is string, value is list of AutoDesk.Revit.DB.Element
    '''

    dic = {}
    for elId in elementIds:
        try:
            el = doc.GetElement(elId)
            try:
                if(dic.has_key(el.Category.Name)):
                    dic[el.Category.Name].append(el)
                else:
                    dic[el.Category.Name] = [el]
            except:
                if(dic.has_key('invalid category')):
                    dic['invalid category'].append(el)
                else:
                    dic['invalid category'] = [el]
        except:
            if(dic.has_key('invalid element')):
                dic['invalid element'].append(el)
            else:
                dic['invalid element'] = [el]
    return dic


def check_whether_dependent_elements_are_multiple_orphaned_legend_components (doc, elementIds):
    '''
    Check if element are orphaned legend components

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param elementIds: List of elements to check
    :type elementIds: list of AutoDesk.Revit.DB.ElementId
    :return: True if all but one element are orphaned legend components.
    :rtype: bool
    '''

    flag = True
    categoryName = 'Legend Components'
    # build dependent type dictionary
    # check whether dictionary is made of
    #   1 entry for type
    #   multiple entries for legend components
    #   no other entry
    # if so: check whether any of the legend component entry has a valid view id
    #   if none has return true, otherwise return false
    dic = build_category_dictionary(doc,  elementIds)
    # check if dictionary has legend component key first up
    if(dic.has_key(categoryName) == True):
        # if so check number of keys and length of elements per key
        if(len(dic.keys()) == 2  and len(dic[categoryName]) == len(elementIds)-1):
            # this should be the only code path returning true...
            for value in dic[categoryName]:
                if value.OwnerViewId != rdb.ElementId.InvalidElementId:
                    flag = False
                    break
        else:
            flag = False
    else:
        flag = False
    return flag


def filter_out_warnings(doc, dependentElements):
    '''
    Attempts to filter out any warnings from ids supplied by checking the workset name
    of each element for 'Reviewable Warnings'

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param dependentElements: List of elements to check.
    :type dependentElements: list of AutoDesk.Revit.DB.Element
    :return: A list of elements id where the workset name of the element is not 'Reviewable Warnings'
    :rtype: list of AutoDesk.Revit.DB.Element
    '''

    ids = []
    for id in dependentElements:
        el = doc.GetElement(id)
        pValue = rParaGet.get_built_in_parameter_value(el, rdb.BuiltInParameter.ELEM_PARTITION_PARAM, rParaGet.get_parameter_value)
        if(pValue != 'Reviewable Warnings'):
            ids.append(id)
    return ids


def has_dependent_elements(
    doc,
    el,
    filter = None,
    threshold = 2 # type: int
    ):
    '''
    Checks whether an element has dependent elements.
    The dependent elements are collected via Element.GetDependentElements(filter).
    This also includes a check as to whether elements returned as dependent are orphaned. (for lack of better words)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param el: The element to be checked for dependent elements.
    :type el: AutoDesk.Revit.DB.Element
    :param filter: What type of dependent elements to filter, defaults to None which will return all dependent elements
    :type filter: Autodesk.Revit.DB.ElementFilter , optional
    :param threshold: The number of how many dependant elements an element can have but still be considered not used, defaults to 2
    :type threshold: int, optional
    :return: returns 0 for no dependent elements, 1, for other elements depend on it, -1 if an exception occurred
    :rtype: int
    '''

    value = 0 # 0: no dependent Elements, 1: has dependent elements, -1 an exception occurred
    try:
        dependentElements = el.GetDependentElements(filter)
        # remove any warnings from dependent elements
        dependentElements = filter_out_warnings(doc, dependentElements)
        # check if dependent elements pass threshold value
        if(len(dependentElements)) > threshold :
            # there appear to be situations where dependent elements are multiple (orphaned?) legend components only
            # or warnings belonging to a type (same type mark ...)
            # these are legend components with an invalid OwnerViewId, check whether this is the case...
            if (check_whether_dependent_elements_are_multiple_orphaned_legend_components(doc, dependentElements) == False):
                value = 1
    except Exception as e:
        value = -1
    return value


def get_used_unused_type_ids(
    doc,
    typeIdGetter,
    useType = 0, # type: int
    threshold = 2 # type: int
    ):
    '''
    Gets either the used or not used type Ids provided by typeIdGetter.
    Whether the used or unused type ids depends on the useType value.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIdGetter: Function returning type ids
    :type typeIdGetter: list of Autodesk.Revit.DB.ElementId
    :param useType: 0, no dependent elements; 1: has dependent elements, defaults to 0
    :type useType: int, optional
    :param threshold: The number of how many dependant elements an element can have but still be considered not used, defaults to 2
    :type threshold: int, optional
    :return: A list of either all used or unused element ids. Depends on useType. 
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get all types elements available
    allTypeIds = typeIdGetter(doc)
    ids = []
    for typeId in allTypeIds:
        type = doc.GetElement(typeId)
        hasDependents = has_dependent_elements(doc, type, None, threshold)
        if(hasDependents == useType):
            ids.append(typeId)
    return ids