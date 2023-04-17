'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit ramps utility functions. 
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

from duHast.APISamples.Ramps.RevitRamps import get_all_ramp_types_by_category


def build_ramp_type_dictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    TODO: similar function exists in Walls module. Consider more generic function.
    :param collector: A filtered element collector containing ramp type elements of family symbols representing in place families
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: dictionary containing key: ramp type family name, value: list of ids
    :type dic: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def sort_ramp_types_by_family_name(doc):
    '''
    Returns a dictionary where key is the family name and values are ids of types belonging to that family.
    TODO: similar function exists in Walls module. Consider more generic function.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    # get all ramp types including in place ramp families
    wts_two = get_all_ramp_types_by_category(doc)
    usedWts = {}
    usedWts = build_ramp_type_dictionary(wts_two, usedWts)
    return usedWts