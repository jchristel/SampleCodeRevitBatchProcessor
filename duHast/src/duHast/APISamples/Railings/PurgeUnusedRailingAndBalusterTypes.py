'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit railings. 
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

from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
from duHast.APISamples.Railings.RevitBalusters import get_all_baluster_symbols_ids, get_baluster_types_from_railings
from duHast.APISamples.Railings.RevitRailings import get_in_place_railing_type_ids_in_model, get_all_railing_type_ids_by_class_and_category
from duHast.APISamples.Railings.Utility.RevitRailingFamilyNames import BUILTIN_RAILING_TYPE_FAMILY_NAMES
from duHast.APISamples.Railings.Utility.MergeLists import merge_into_unique_list
from duHast.APISamples.Railings.Utility.RevitRailingsTypeSorting import sort_railing_types_by_family_name


def get_used_railing_type_ids(doc):
    '''
    Gets all used Railing element types available in model excluding in place types.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_railing_type_ids_by_class_and_category, 1)
    return ids


def family_no_types_in_use(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    Returns False if any symbols (types) of a family (first list) are in use in a model (second list).
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


def get_unused_non_in_place_railing_type_ids_to_purge(doc):
    '''
    Gets all unused Railing type ids for:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - loaded families
    Excludes any in place family types.
    This method can be used to safely delete unused railing types:
    In the case that no railing instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one railing type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_railing_type_ids_by_class_and_category, 0)
    # make sure there is at least on Railing type per system family left in model
    RailingTypes = sort_railing_types_by_family_name(doc)
    for key, value in RailingTypes.items():
        if(key in BUILTIN_RAILING_TYPE_FAMILY_NAMES):
            if(family_no_types_in_use(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def get_used_in_place_railing_type_ids(doc):
    '''
    Gets all used in place railing type ids.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_in_place_railing_type_ids_in_model, 1)
    return ids


def get_unused_in_place_railing_type_ids(doc):
    '''
    Gets all unused in place railing type ids.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_in_place_railing_type_ids_in_model, 0)
    return ids


def get_unused_in_place_railing_ids_for_purge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of in place Railing families which can be purged.
    This method can be used to safely delete unused in place railing types and families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_in_place_railing_type_ids)
    return ids


def get_used_baluster_type_ids(doc):
    '''
    Gets all used baluster type ids in the model.
    Used: at least one instance of this family symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsedInModel = rPurgeUtils.get_used_unused_type_ids(doc, get_all_baluster_symbols_ids, 1)
    idsUsedInRailings = get_baluster_types_from_railings(doc)
    ids = merge_into_unique_list(ids, idsUsedInModel)
    ids = merge_into_unique_list(ids, idsUsedInRailings)
    return ids


def get_unused_baluster_type_ids(doc):
    '''
    Gets all unused baluster type ids in the model.
    Unused: Not one instance of this family symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = get_used_baluster_type_ids(doc)
    idsAvailable = get_all_baluster_symbols_ids(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids


def get_unused_baluster_type_ids_for_purge(doc):
    '''
    Gets all unused baluster type ids in the model.
    Unused: at least one instance of this family symbol (type) is placed in the model.
    This method can be used to safely delete unused baluster families and symbols.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_baluster_type_ids)
    return ids