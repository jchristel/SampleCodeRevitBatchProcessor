"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging unused families which can be used in mep systems.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


# -------------------------------- purge loaded families which can be used in system types --------------------------------

from duHast.Revit.Family import purge_unused_family_types as rFamPurge
from duHast.Revit.Common import purge_utils as rPurgeUtils

from duHast.Revit.MEP_Systems.pipes import (
    get_symbol_ids_for_pipe_types_in_model,
    get_symbol_ids_used_in_pipe_types,
)
from duHast.Revit.MEP_Systems.conduits import (
    get_symbol_ids_for_conduit_types_in_model,
    get_symbol_ids_used_in_conduit_types,
)
from duHast.Revit.MEP_Systems.cable_trays import (
    get_symbol_ids_for_cable_tray_types_in_model,
    get_symbol_ids_used_in_cable_tray_types,
)
from duHast.Revit.MEP_Systems.ducts import (
    get_symbol_ids_for_duct_types_in_model,
    get_symbol_ids_used_in_duct_types,
)
from duHast.Revit.MEP_Systems.flex_ducts import get_symbol_ids_used_in_flex_duct_types
from duHast.Revit.MEP_Systems.Utility.MergeLists import merge_into_unique_list


def get_used_duct_and_flex_duct_symbol_ids(doc):
    """
    Gets all used duct and flex duct symbol ids of categories
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(
        doc, get_symbol_ids_for_duct_types_in_model, 1
    )
    ids_used_in_types = get_symbol_ids_used_in_duct_types(doc)
    ids_used_in_flex_types = get_symbol_ids_used_in_flex_duct_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    ids = merge_into_unique_list(ids, ids_used_in_flex_types)
    return ids


def get_unused_duct_and_flex_duct_symbol_ids(doc):
    """
    Gets all unused duct and flex duct symbol ids of categories
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used = get_used_duct_and_flex_duct_symbol_ids(doc)
    ids_available = get_symbol_ids_for_duct_types_in_model(doc)
    for id in ids_available:
        if id not in ids_used:
            ids.append(id)
    return ids


def get_unused_duct_and_flex_duct_symbol_ids_for_purge(doc):
    """
    Gets all unused duct and flex duct symbol ids of categories
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused duct symbols and families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_duct_and_flex_duct_symbol_ids
    )
    return ids


def get_used_cable_tray_symbol_ids(doc):
    """
    Gets all used cable tray symbol ids of categories
    - BuiltInCategory.OST_CableTrayFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(
        doc, get_symbol_ids_for_cable_tray_types_in_model, 1
    )
    ids_used_in_types = get_symbol_ids_used_in_cable_tray_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    return ids


def get_unused_cable_tray_symbol_ids(doc):
    """
    Gets all unused cable tray symbol ids of categories
    - BuiltInCategory.OST_CableTrayFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used = get_used_cable_tray_symbol_ids(doc)
    ids_available = get_symbol_ids_for_cable_tray_types_in_model(doc)
    for id in ids_available:
        if id not in ids_used:
            ids.append(id)
    return ids


def get_unused_cable_tray_symbol_ids_for_purge(doc):
    """
    Gets all unused cable tray symbol ids of categories
    - BuiltInCategory.OST_CableTrayFitting
    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused cable tray symbols and families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_cable_tray_symbol_ids
    )
    return ids


def get_used_conduit_symbol_ids(doc):
    """
    Gets all used conduit symbol ids of categories
    - BuiltInCategory.OST_ConduitFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(
        doc, get_symbol_ids_for_conduit_types_in_model, 1
    )
    ids_used_in_types = get_symbol_ids_used_in_conduit_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    return ids


def get_unused_conduit_symbol_ids(doc):
    """
    Gets all unused conduit symbol ids of categories
    - BuiltInCategory.OST_ConduitFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used = get_used_conduit_symbol_ids(doc)
    ids_available = get_symbol_ids_for_conduit_types_in_model(doc)
    for id in ids_available:
        if id not in ids_used:
            ids.append(id)
    return ids


def get_unused_conduit_symbol_ids_for_purge(doc):
    """
    Gets all unused conduit symbol ids of categories
    - BuiltInCategory.OST_ConduitFitting
    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused conduit symbols and families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_conduit_symbol_ids
    )
    return ids


def get_used_pipe_symbol_ids(doc):
    """
    Gets all used pipe symbol ids of categories
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(
        doc, get_symbol_ids_for_pipe_types_in_model, 1
    )
    ids_used_in_types = get_symbol_ids_used_in_pipe_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    return ids


def get_unused_pipe_symbol_ids(doc):
    """
    Gets all unused pipe symbol ids of categories
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used = get_used_pipe_symbol_ids(doc)
    ids_available = get_symbol_ids_for_pipe_types_in_model(doc)
    for id in ids_available:
        if id not in ids_used:
            ids.append(id)
    return ids


def get_unused_pipe_symbol_ids_for_purge(doc):
    """
    Gets all unused pipe symbol ids of categories
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused pipe symbols and families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_pipe_symbol_ids)
    return ids
