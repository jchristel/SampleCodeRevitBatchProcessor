"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit curtain wall elements. 
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

from duHast.Revit.Family.purge_unused_family_types import (
    get_unused_in_place_ids_for_purge,
)
from duHast.Revit.Common.purge_utils import get_used_unused_type_ids
from duHast.Revit.Walls.curtain_wall_elements import (
    get_all_curtain_wall_element_type_ids_by_category,
    get_all_curtain_wall_element_type_ids_by_category_excl_symbols,
    get_all_curtain_wall_non_shared_symbol_ids_by_category,
    get_all_curtain_wall_non_shared_symbol_ids_by_category,
)


def get_used_curtain_wall_element_type_ids(doc):
    """
    Gets all used Curtain Wall Element element type ids available in model.
    Used: at least one instance of this type is placed in the model.
    Includes:
    - curtain wall panels
    - curtain wall mullions
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_used_unused_type_ids(
        doc, get_all_curtain_wall_element_type_ids_by_category, 1
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


def get_unused_non_symbol_curtain_wall_element_type_ids_to_purge(doc):
    """
    Gets all unused Curtain Wall Element element type ids which can be safely deleted from the model.
    This method can be used to safely delete unused in curtain wall element types. There is no requirement by Revit to have at least one\
        curtain wall element definition in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # get unused type ids
    ids = get_used_unused_type_ids(
        doc,
        get_all_curtain_wall_element_type_ids_by_category_excl_symbols,
        0,
    )
    # unlike other element types, here I do NOT make sure there is at least on curtain wall element type per system family left in model!!
    return ids


def get_used_curtain_wall_symbol_ids(doc):
    """
    Gets a list of all used loadable, non shared, family symbols (types) in the model of categories:
    - curtain wall panels
    - curtain wall mullions
    Used: at least one family instance of this symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_used_unused_type_ids(
        doc, get_all_curtain_wall_non_shared_symbol_ids_by_category, 1
    )
    return ids


def get_unused_curtain_wall_symbol_ids(doc):
    """
    Gets a list of all used loadable, non shared, family symbols (types) in the model of categories:
    - curtain wall panels
    - curtain wall mullions
    Unused: Not one family instance of this symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_used_unused_type_ids(
        doc, get_all_curtain_wall_non_shared_symbol_ids_by_category, 0
    )
    return ids


def get_unused_curtain_wall_symbol_ids_for_purge(doc):
    """
    Gets symbol(type) ids and family ids (when no type is in use) of curtain wall element families which can be safely deleted from the model.
    This method can be used to safely delete unused curtain wall element types. There is no requirement by Revit to have at least one\
        in place wall definition in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused curtain wall element symbols (types) and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_unused_in_place_ids_for_purge(doc, get_unused_curtain_wall_symbol_ids)
    return ids
