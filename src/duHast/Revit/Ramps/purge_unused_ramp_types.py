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
# BSD License
# Copyright 2023, Jan Christel
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
