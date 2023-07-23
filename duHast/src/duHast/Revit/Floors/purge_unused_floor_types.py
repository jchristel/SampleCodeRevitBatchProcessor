"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit floors. 
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
from duHast.Revit.Floors import floors as rFloor
from duHast.Revit.Floors.Utility import floors_type_sorting as rFloorTypeSort


def get_used_floor_type_ids(doc):
    """
    Returns all used in Floor type ids.
    Filters by builtin category.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing not used floor types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rFloor.get_all_floor_type_ids_in_model_by_category, 1
    )
    return ids


def family_no_types_in_use(fam_type_ids, un_used_type_ids):
    """
    Compares two lists of ids. True if any id is not in un_used_type_ids.
    TODO: check for more generic list comparison and remove this function.

    :param fam_type_ids: List of family type ids to check.
    :type fam_type_ids: List of Autodesk.Revit.DB.ElementId
    :param un_used_type_ids: Reference list of ids.
    :type un_used_type_ids: List of Autodesk.Revit.DB.ElementId
    :return: True if any id from fam_type_ids is not in un_used_type_ids.
    :rtype: bool
    """

    match = True
    for fam_type_id in fam_type_ids:
        if fam_type_id not in un_used_type_ids:
            match = False
            break
    return match


def get_unused_non_in_place_floor_type_ids_to_purge(doc):
    """
    Gets all unused floor type id's.
    This method can be used to safely delete unused wall types:
    In the case that no wall instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one wall type definition to be in the model.
    Filters by class:
    - Floor
    - foundation slab
    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing not used floor types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rFloor.get_all_floor_type_ids_in_model_by_class, 0
    )
    # make sure there is at least on Floor type per system family left in model
    floor_types = rFloorTypeSort.sort_floor_types_by_family_name(doc)
    for key, value in floor_types.items():
        if key in rFloor.BUILTIN_FLOOR_TYPE_FAMILY_NAMES:
            if family_no_types_in_use(value, ids) == True:
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def get_used_in_place_floor_type_ids(doc):
    """
    Gets all used in place family symbol (type) ids.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing in place floor symbols (types).
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rFloor.get_all_in_place_floor_type_ids_in_model, 1
    )
    return ids


def get_unused_in_place_floor_type_ids(doc):
    """
    Gets all used in place family symbol (type) ids.
    Unused: Not one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing in place floor symbols (types).
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rFloor.get_all_in_place_floor_type_ids_in_model, 0
    )
    return ids


def get_unused_in_place_floor_ids_for_purge(doc):
    """
    Gets symbol(type) ids and family ids (when no type is in use) of in place floor families which can be safely deleted from the model.
    This method can be used to safely delete unused in place floor types. There is no requirement by Revit to have at least one\
        in place wall definition in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in place floor types and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_in_place_floor_type_ids
    )
    return ids
