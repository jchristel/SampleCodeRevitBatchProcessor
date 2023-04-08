'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit roofs. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

from duHast.APISamples.Family import RevitFamilyUtils as rFam
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Roofs.RevitRoofs import GetAllInPlaceRoofTypeIdsInModel, GetAllRoofTypeIdsInModelByClass, GetAllRoofTypeIdsInModelByCategory
from duHast.APISamples.Roofs.Utility.RevitRoofsFamilyNames import BUILTIN_ROOF_TYPE_FAMILY_NAMES
from duHast.APISamples.Roofs.Utility.RevitRoofsTypeSorting import SortRoofTypesByFamilyName


def GetUsedRoofTypeIds(doc):
    '''
    Gets all used in Roof type ids in the model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllRoofTypeIdsInModelByCategory, 1)
    return ids


def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    Returns False if any symbols (types) of a family (first lists) are in use in a model (second list).
    TODO: repetitive code...Consider generic function!
    :param famTypeIds: List of family symbols (types).
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: List of unused family symbols (types)
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId
    :return: True if all ids in first list are also in second list, otherwise False.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match


def GetUnusedNonInPlaceRoofTypeIdsToPurge(doc):
    '''
    Gets all unused Roof type ids in the model.
    This method can be used to safely delete unused roof types. In the case that no roof\
        instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one roof type definition to be in the model.
    Unused: Not one instance of this type is placed in the model.
    - Roof Soffit
    - Compound Roof
    - Basic Roof
    It will therefore not return any in place family types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRoofTypeIdsInModelByClass, 0)
    # make sure there is at least on Roof type per system family left in model
    RoofTypes = SortRoofTypesByFamilyName(doc)
    for key, value in RoofTypes.items():
        if(key in BUILTIN_ROOF_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def GetUsedInPlaceRoofTypeIds(doc):
    '''
    Gets all used in place roof type ids in the model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRoofTypeIdsInModel, 1)
    return ids


def GetUnusedInPlaceRoofTypeIds(doc):
    '''
    Gets all unused in place roof type ids in the model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRoofTypeIdsInModel, 0)
    return ids


def GetUnusedInPlaceRoofIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use of a family) of in place Roof families which can be purged.
    This method can be used to safely delete unused in place roof types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceRoofTypeIds)
    return ids