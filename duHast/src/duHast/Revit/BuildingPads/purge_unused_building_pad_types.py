"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit building pad types. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Revit.BuildingPads.Utility import (
    RevitBuildingPadTypeSorting as rBuildingPadSort,
)
from duHast.Revit.BuildingPads import building_pads as rBuildingPads

#: Built in family name for pad
BASIC_BUILDING_PAD_FAMILY_NAME = "Pad"

#: List of all Built in pad family names
BUILTIN_BUILDING_PAD_TYPE_FAMILY_NAMES = [BASIC_BUILDING_PAD_FAMILY_NAME]


def get_used_building_pad_type_ids(doc):
    """
    Gets all used building pad type ids.
    Filters by category.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used building pad types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rBuildingPads.get_all_building_pad_type_ids_in_model_by_category, 1
    )
    return ids


def family_no_types_in_use(fam_type_ids, un_used_type_ids):
    """
    Compares two lists of ids. True if any id is not in unUsedTypeIds.
    TODO: check for more generic list comparison and remove this function.
    :param fam_type_ids: List of family type ids to check.
    :type fam_type_ids: List of Autodesk.Revit.DB.ElementId
    :param un_used_type_ids: Reference list of ids.
    :type un_used_type_ids: List of Autodesk.Revit.DB.ElementId
    :return: True if any id from famTypeIds is not in unUsedTypeIds.
    :rtype: bool
    """

    match = True
    for fam_type_id in fam_type_ids:
        if fam_type_id not in un_used_type_ids:
            match = False
            break
    return match


def get_unused_non_in_place_building_pad_type_ids_to_purge(doc):
    """
    Gets all unused building pad type id's.
    - Basic BuildingPad
    This method can be used to safely delete unused building pad types:
    In the case that no building pad instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one building pad type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing not used building pad types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rBuildingPads.get_all_building_pad_type_ids_in_model_by_class, 0
    )
    # make sure there is at least on BuildingPad type per system family left in model
    building_pad_types = rBuildingPadSort.sort_building_pad_types_by_family_name(doc)
    for key, value in building_pad_types.items():
        if key in BUILTIN_BUILDING_PAD_TYPE_FAMILY_NAMES:
            if family_no_types_in_use(value, ids) == True:
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
