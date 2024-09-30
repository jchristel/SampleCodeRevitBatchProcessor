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


# required for .ToList() call
# import clr

# clr.AddReference("System.Core")
# from System import Linq

# clr.ImportExtensions(Linq)

from duHast.Revit.Common.purge_utils import get_used_unused_type_ids

from duHast.Revit.Walls.walls import (
    get_all_in_place_wall_type_ids,
    get_all_basic_wall_type_ids,
)
from duHast.Revit.Family.purge_unused_family_types import (
    get_unused_in_place_ids_for_purge,
)
from duHast.Revit.Walls.curtain_walls import get_all_curtain_wall_type_ids
from duHast.Revit.Walls.stacked_walls import get_all_stacked_wall_type_ids

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

    ids = get_used_unused_type_ids(doc, get_all_stacked_wall_type_ids, 1)
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

    ids = get_used_unused_type_ids(doc, get_all_in_place_wall_type_ids, 1)
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

    ids = get_used_unused_type_ids(doc, get_all_curtain_wall_type_ids, 1)
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

    ids = get_used_unused_type_ids(doc, get_all_basic_wall_type_ids, 1)
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

    ids = get_used_unused_type_ids(doc, get_all_basic_wall_type_ids, 0)
    # looks like a separate check is required whether any basic wall type is used in stacked wall type in model at this point
    # DOH! GetStackedWallMemberIds() is only available on wall element but not wallType. Why?
    available_type_count = len(get_all_basic_wall_type_ids(doc))
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

    ids = get_used_unused_type_ids(doc, get_all_curtain_wall_type_ids, 0)
    available_type_count = len(get_all_curtain_wall_type_ids(doc))
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

    ids = get_used_unused_type_ids(doc, get_all_in_place_wall_type_ids, 0)
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

    ids = get_unused_in_place_ids_for_purge(doc, get_unused_in_place_wall_type_ids)
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

    ids = get_used_unused_type_ids(doc, get_all_stacked_wall_type_ids, 0)
    available_type_count = len(get_all_stacked_wall_type_ids(doc))
    if len(ids) == available_type_count:
        ids.pop(0)
    return ids
