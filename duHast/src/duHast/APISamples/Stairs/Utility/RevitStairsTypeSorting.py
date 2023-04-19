'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to sorting Revit stairs by types. 
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


from duHast.APISamples.Stairs.Utility import RevitStairsFilter as rStairFilter

def build_stair_type_dictionary(collector, dic):
    '''
    Amends dictionary past in with keys and or values added retrieved from collector past in.

    Key values are as per BUILTIN_STAIR_TYPE_FAMILY_NAMES.

    :param collector: A filtered element collector containing Stair type elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: stair type family name, value: list of ids.
    :type dic: dic { str: [Autodesk.Revit.DB.ElementId]}

    :return: A dictionary containing key: stair type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def sort_stair_types_by_family_name(doc):
    '''
    Returns a dictionary containing all stair types in the model.

    Key values are as per BUILTIN_STAIR_TYPE_FAMILY_NAMES.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: stair type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    '''

    # get all Stair Type Elements
    wts = rStairFilter._get_stair_types_by_class(doc)
    # get all stair types including in place stair families
    wts_two = rStairFilter._get_all_stair_types_by_category(doc)
    used_wts = {}
    used_wts = build_stair_type_dictionary(wts, used_wts)
    used_wts = build_stair_type_dictionary(wts_two, used_wts)
    return used_wts