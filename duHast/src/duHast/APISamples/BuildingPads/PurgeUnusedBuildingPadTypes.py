'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit building pad types. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.BuildingPads.Utility import RevitBuildingPadTypeSorting as rBuildingPadSort
from duHast.APISamples.BuildingPads import RevitBuildingPads as rBuildingPads

#: Built in family name for pad
BASIC_BUILDING_PAD_FAMILY_NAME = 'Pad'

#: List of all Built in pad family names
BUILTIN_BUILDING_PAD_TYPE_FAMILY_NAMES = [
    BASIC_BUILDING_PAD_FAMILY_NAME
]

def GetUsedBuildingPadTypeIds(doc):
    '''
    Gets all used building pad type ids.
    Filters by category.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used building pad types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, rBuildingPads.GetAllBuildingPadTypeIdsInModelByCategory, 1)
    return ids


def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of ids. True if any id is not in unUsedTypeIds.
    TODO: check for more generic list comparison and remove this function.
    :param famTypeIds: List of family type ids to check.
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: Reference list of ids.
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId
    :return: True if any id from famTypeIds is not in unUsedTypeIds.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match


def GetUnusedNonInPlaceBuildingPadTypeIdsToPurge(doc):
    '''
    Gets all unused building pad type id's.
    - Basic BuildingPad
    This method can be used to safely delete unused building pad types:
    In the case that no building pad instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one building pad type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing not used building pad types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, rBuildingPads.GetAllBuildingPadTypeIdsInModelByClass, 0)
    # make sure there is at least on BuildingPad type per system family left in model
    BuildingPadTypes = rBuildingPadSort.SortBuildingPadTypesByFamilyName(doc)
    for key, value in BuildingPadTypes.items():
        if(key in BUILTIN_BUILDING_PAD_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids

