"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit railings. 
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

from duHast.Revit.Family import purge_unused_family_types as rFamPurge
from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Revit.Railings.balusters import (
    get_all_baluster_symbols_ids,
    get_baluster_types_from_railings,
)
from duHast.Revit.Railings.railings import (
    get_in_place_railing_type_ids_in_model,
    get_all_railing_type_ids_by_class_and_category,
)
from duHast.Revit.Railings.Utility.railing_family_names import (
    BUILTIN_RAILING_TYPE_FAMILY_NAMES,
)
from duHast.Revit.Railings.Utility.merge_lists import merge_into_unique_list
from duHast.Revit.Railings.Utility.railings_type_sorting import (
    sort_railing_types_by_family_name,
)


def get_used_railing_type_ids(doc):
    """
    Gets all used Railing element types available in model excluding in place types.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, get_all_railing_type_ids_by_class_and_category, 1
    )
    return ids


def family_no_types_in_use(fam_type_ids, un_used_type_ids):
    """
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    Returns False if any symbols (types) of a family (first list) are in use in a model (second list).
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


def get_unused_non_in_place_railing_type_ids_to_purge(doc):
    """
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
    """

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, get_all_railing_type_ids_by_class_and_category, 0
    )
    # make sure there is at least on Railing type per system family left in model
    railing_types = sort_railing_types_by_family_name(doc)
    for key, value in railing_types.items():
        if key in BUILTIN_RAILING_TYPE_FAMILY_NAMES:
            if family_no_types_in_use(value, ids) == True:
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def get_used_in_place_railing_type_ids(doc):
    """
    Gets all used in place railing type ids.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, get_in_place_railing_type_ids_in_model, 1
    )
    return ids


def get_unused_in_place_railing_type_ids(doc):
    """
    Gets all unused in place railing type ids.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, get_in_place_railing_type_ids_in_model, 0
    )
    return ids


def get_unused_in_place_railing_ids_for_purge(doc):
    """
    Gets symbol(type) ids and family ids (when no type is in use) of in place Railing families which can be purged.
    This method can be used to safely delete unused in place railing types and families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_in_place_railing_type_ids
    )
    return ids


def get_used_baluster_type_ids(doc):
    """
    Gets all used baluster type ids in the model.
    Used: at least one instance of this family symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used_in_model = rPurgeUtils.get_used_unused_type_ids(
        doc, get_all_baluster_symbols_ids, 1
    )
    ids_used_in_railings = get_baluster_types_from_railings(doc)
    ids = merge_into_unique_list(ids, ids_used_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_railings)
    return ids


def get_unused_baluster_type_ids(doc):
    """
    Gets all unused baluster type ids in the model.
    Unused: Not one instance of this family symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used = get_used_baluster_type_ids(doc)
    ids_available = get_all_baluster_symbols_ids(doc)
    for id in ids_available:
        if id not in ids_used:
            ids.append(id)
    return ids


def get_unused_baluster_type_ids_for_purge(doc):
    """
    Gets all unused baluster type ids in the model.
    Unused: at least one instance of this family symbol (type) is placed in the model.
    This method can be used to safely delete unused baluster families and symbols.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_baluster_type_ids)
    return ids
