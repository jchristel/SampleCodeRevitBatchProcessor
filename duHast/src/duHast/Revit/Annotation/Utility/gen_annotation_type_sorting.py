'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit generic annotation utility functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
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
#

from duHast.Revit.Annotation.generic_annotation import get_all_generic_annotation_types_by_category


def build_generic_annotation_types_dictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    :param collector: Filtered element collector containing GenericAnnotation type elements of family symbols.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: Dictionary, the key is the family name and the value a list of element ids representing annotation types.
    :type dic: dic: key str, values list of Autodesk.Revit.DB.ElementId
    :return: Past in expanded by values from collector. Dictionary the key is the Family name and the value a list of element ids.
    :rtype: dic: key str, values list of Autodesk.Revit.DB.ElementId
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def sort_generic_annotation_types_by_family_name(doc):
    '''
    Returns the dictionary keys is autodesk.revit.db element type as string and values are elements of that type.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param collector: A filtered element collector containing elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all elements belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.Element]}
    '''

    wts_two = get_all_generic_annotation_types_by_category(doc)
    usedWts = {}
    usedWts = build_generic_annotation_types_dictionary(wts_two, usedWts)
    return usedWts