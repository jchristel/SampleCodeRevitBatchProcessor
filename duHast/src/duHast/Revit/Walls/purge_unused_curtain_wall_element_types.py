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
from duHast.Revit.Walls import curtain_wall_elements as rCurtainWallElem


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

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rCurtainWallElem.get_all_curtain_wall_element_type_ids_by_category, 1
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
    ids = rPurgeUtils.get_used_unused_type_ids(
        doc,
        rCurtainWallElem.get_all_curtain_wall_element_type_ids_by_category_excl_symbols,
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

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rCurtainWallElem.get_all_curtain_wall_non_shared_symbol_ids_by_category, 1
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

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rCurtainWallElem.get_all_curtain_wall_non_shared_symbol_ids_by_category, 0
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

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_curtain_wall_symbol_ids
    )
    return ids
