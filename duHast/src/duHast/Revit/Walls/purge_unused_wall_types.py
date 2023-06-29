"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit walls. 
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


# required for .ToList() call
import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Revit.Walls import walls as rWall
from duHast.Revit.Family import purge_unused_family_types as rFamPurge
from duHast.Revit.Walls import curtain_walls as rCurtainWall
from duHast.Revit.Walls import stacked_walls as rStackWall

# -------------------- used types --------------------------


def get_used_stacked_wall_type_ids(doc):
    """
    Returns all used stack wall type ids.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used stacked wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rStackWall.get_all_stacked_wall_type_ids, 1
    )
    return ids


def get_used_in_place_wall_type_ids(doc):
    """
    Gets all used in place type ids in the model.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used in place wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rWall.get_all_in_place_wall_type_ids, 1
    )
    return ids


def get_used_curtain_wall_type_ids(doc):
    """
    Gets type ids off all used curtain wall types.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used in curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rCurtainWall.get_all_curtain_wall_type_ids, 1
    )
    return ids


def get_used_basic_wall_type_ids(doc):
    """
    Gets type ids off all used basic wall types.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all basic wall types in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rWall.get_all_basic_wall_type_ids, 1
    )
    return ids


# -------------------- purge unused types --------------------------


def get_unused_basic_wall_type_ids_to_purge(doc):
    """
    Gets type ids off all unused basic wall types in model.
    This method can be used to safely delete unused basic wall types. In the case that no basic\
        wall instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one basic wall type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all basic wall types not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rWall.get_all_basic_wall_type_ids, 0
    )
    # looks like a separate check is required whether any basic wall type is used in stacked wall type in model at this point
    # DOH! GetStackedWallMemberIds() is only available on wall element but not wallType. Why?
    available_type_count = len(rWall.get_all_basic_wall_type_ids(doc).ToList())
    if len(ids) == available_type_count:
        ids.pop(0)
    return ids


def get_unused_curtain_wall_type_ids_to_purge(doc):
    """
    Gets type ids off all unused curtain wall types.
    This method can be used to safely delete unused curtain wall types. In the case that no curtain\
        wall instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one curtain wall type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rCurtainWall.get_all_curtain_wall_type_ids, 0
    )
    available_type_count = len(rCurtainWall.get_all_curtain_wall_type_ids(doc).ToList())
    if len(ids) == available_type_count:
        ids.pop(0)
    return ids


def get_unused_in_place_wall_type_ids(doc):
    """
    Gets all unused in place type ids in the model.
    Unused: Not one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in place wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rWall.get_all_in_place_wall_type_ids, 0
    )
    return ids


def get_unused_in_place_wall_ids_for_purge(doc):
    """
    Gets symbol(type) ids and family ids (when no type is in use) of in place wall families which can be safely deleted from the model.
    This method can be used to safely delete unused in place wall types. There is no requirement by Revit to have at least one\
        in place wall definition in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in place wall types and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_in_place_wall_type_ids
    )
    return ids


def get_unused_stacked_wall_type_ids_to_purge(doc):
    """
    Gets all unused stacked wall type id's.
    This method can be used to safely delete unused wall types:
    In the case that no wall instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one wall type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing not used stacked wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rStackWall.get_all_stacked_wall_type_ids, 0
    )
    available_type_count = len(rStackWall.get_all_stacked_wall_type_ids(doc).ToList())
    if len(ids) == available_type_count:
        ids.pop(0)
    return ids
