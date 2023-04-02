'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to sorting Revit building pads by types. 
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

from duHast.APISamples.BuildingPads.Utility import RevitBuildingPadsFilter as rBuildingPadFilter

def BuildBuildingPadTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    Keys are built in building pad family type names.
    TODO: Use more generic code.
    :param collector: A filtered element collector containing building pad types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key:  building pad type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    :return: A dictionary containing key: built in building pad type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def SortBuildingPadTypesByFamilyName(doc):
    '''
    Returns a dictionary of all building pad types in the model where key is the build in wall family name, values are ids of associated wall types.
    TODO: Use more generic code.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary containing key: built in building pad type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    # get all building pad Type Elements
    wts = rBuildingPadFilter._get_building_pad_types_by_class(doc)
    # get all pad types including in place pad families
    wts_two = rBuildingPadFilter._get_all_building_pad_types_by_category(doc)
    usedWts = {}
    usedWts = BuildBuildingPadTypeDictionary(wts, usedWts)
    usedWts = BuildBuildingPadTypeDictionary(wts_two, usedWts)
    return usedWts