"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit ramps. 
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

from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Revit.Ramps.Utility.RevitRampsFamilyNames import (
    BUILTIN_RAMP_TYPE_FAMILY_NAMES,
)
from duHast.Revit.Ramps.Utility.RevitRampsTypeSorting import (
    sort_ramp_types_by_family_name,
)
from duHast.Revit.Ramps.ramps import get_all_ramp_types_ids_by_category


def get_used_ramp_type_ids(doc):
    """
    Gets all used ramp element type ids available in model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of ramp types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, get_all_ramp_types_ids_by_category, 1, 4
    )
    return ids


def family_no_types_in_use(fam_type_ids, un_used_type_ids):
    """
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    Returns False if any symbols (types) of a family (first lists) are in use in a model (second list).
    TODO: repetitive code...Consider generic function!
    :param fam_type_ids: List of family symbols (types).
    :type fam_type_ids: List of Autodesk.Revit.DB.ElementId
    :param un_used_type_ids: List of unused family symbols (types)
    :type un_used_type_ids: List of Autodesk.Revit.DB.ElementId
    :return: True if all ids in first list are also in second list, otherwise False.
    :rtype: bool
    """

    match = True
    for fam_type_id in fam_type_ids:
        if fam_type_id not in un_used_type_ids:
            match = False
            break
    return match


def get_unused_non_in_place_ramp_type_ids_to_purge(doc):
    """
    Gets all unused ramp type ids in the model.
    This method can be used to safely delete unused ramp types. In the case that no ramp\
        instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one ramp type definition to be in the model.
    Unused: Not one instance of this type is placed in the model.
    - Ramp
    It will therefore not return any in place family types. (No such thing in Revit?)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, get_all_ramp_types_ids_by_category, 0, 4
    )
    # make sure there is at least on Ramp type per system family left in model
    ramp_types = sort_ramp_types_by_family_name(doc)
    for key, value in ramp_types.items():
        if key in BUILTIN_RAMP_TYPE_FAMILY_NAMES:
            if family_no_types_in_use(value, ids) == True:
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
