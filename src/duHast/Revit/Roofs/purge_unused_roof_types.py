"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit roofs. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

from duHast.Revit.Family import purge_unused_family_types as rFamPurge
from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Revit.Roofs.roofs import (
    get_all_in_place_roof_type_ids,
    get_all_roof_type_ids_by_class,
    get_all_roof_type_ids_by_category,
)
from duHast.Revit.Roofs.Utility.RevitRoofsFamilyNames import (
    BUILTIN_ROOF_TYPE_FAMILY_NAMES,
)
from duHast.Revit.Roofs.Utility.RevitRoofsTypeSorting import (
    sort_roof_types_by_family_name,
)


def get_used_roof_type_ids(doc):
    """
    Gets all used in Roof type ids in the model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, get_all_roof_type_ids_by_category, 1
    )
    return ids


def family_no_types_in_use(famTypeIds, unUsedTypeIds):
    """
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    Returns False if any symbols (types) of a family (first lists) are in use in a model (second list).
    TODO: repetitive code...Consider generic function!
    :param famTypeIds: List of family symbols (types).
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: List of unused family symbols (types)
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId
    :return: True if all ids in first list are also in second list, otherwise False.
    :rtype: bool
    """

    match = True
    for famTypeId in famTypeIds:
        if famTypeId not in unUsedTypeIds:
            match = False
            break
    return match


def get_unused_non_in_place_roof_type_ids_to_purge(doc):
    """
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
    """

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_roof_type_ids_by_class, 0)
    # make sure there is at least on Roof type per system family left in model
    RoofTypes = sort_roof_types_by_family_name(doc)
    for key, value in RoofTypes.items():
        if key in BUILTIN_ROOF_TYPE_FAMILY_NAMES:
            if family_no_types_in_use(value, ids) == True:
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def get_used_in_place_roof_type_ids(doc):
    """
    Gets all used in place roof type ids in the model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_in_place_roof_type_ids, 1)
    return ids


def get_unused_in_place_roof_type_ids(doc):
    """
    Gets all unused in place roof type ids in the model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_in_place_roof_type_ids, 0)
    return ids


def get_unused_in_place_roof_type_ids_for_purge(doc):
    """
    Gets symbol(type) ids and family ids (when no type is in use of a family) of in place Roof families which can be purged.
    This method can be used to safely delete unused in place roof types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_in_place_roof_type_ids
    )
    return ids
