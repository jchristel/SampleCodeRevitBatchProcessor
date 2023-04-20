'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging unused families which can be used in mep systems.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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


# -------------------------------- purge loaded families which can be used in system types --------------------------------

from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils

from duHast.APISamples.MEP_Systems.RevitPipes import get_symbol_ids_for_pipe_types_in_model, get_symbol_ids_used_in_pipe_types
from duHast.APISamples.MEP_Systems.RevitConduits import get_symbol_ids_for_conduit_types_in_model, get_symbol_ids_used_in_conduit_types
from duHast.APISamples.MEP_Systems.RevitCableTrays import get_symbol_ids_for_cable_tray_types_in_model, get_symbol_ids_used_in_cable_tray_types
from duHast.APISamples.MEP_Systems.RevitDucts import get_symbol_ids_for_duct_types_in_model, get_symbol_ids_used_in_duct_types
from duHast.APISamples.MEP_Systems.RevitFlexDucts import get_symbol_ids_used_in_flex_duct_types
from duHast.APISamples.MEP_Systems.Utility.MergeLists import merge_into_unique_list


def get_used_duct_and_flex_duct_symbol_ids(doc):
    '''
    Gets all used duct and flex duct symbol ids of categories
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(doc, get_symbol_ids_for_duct_types_in_model, 1)
    ids_used_in_types = get_symbol_ids_used_in_duct_types(doc)
    ids_used_in_flex_types = get_symbol_ids_used_in_flex_duct_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    ids = merge_into_unique_list(ids, ids_used_in_flex_types)
    return ids


def get_unused_duct_and_flex_duct_symbol_ids(doc):
    '''
    Gets all unused duct and flex duct symbol ids of categories
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_used = get_used_duct_and_flex_duct_symbol_ids(doc)
    ids_available = get_symbol_ids_for_duct_types_in_model(doc)
    for id in ids_available:
        if (id not in ids_used):
            ids.append(id)
    return ids


def get_unused_duct_and_flex_duct_symbol_ids_for_purge(doc):
    '''
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
    '''

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_duct_and_flex_duct_symbol_ids)
    return ids


def get_used_cable_tray_symbol_ids(doc):
    '''
    Gets all used cable tray symbol ids of categories
    - BuiltInCategory.OST_CableTrayFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(doc, get_symbol_ids_for_cable_tray_types_in_model, 1)
    ids_used_in_types = get_symbol_ids_used_in_cable_tray_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    return ids


def get_unused_cable_tray_symbol_ids(doc):
    '''
    Gets all unused cable tray symbol ids of categories
    - BuiltInCategory.OST_CableTrayFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_used = get_used_cable_tray_symbol_ids(doc)
    ids_available = get_symbol_ids_for_cable_tray_types_in_model(doc)
    for id in ids_available:
        if (id not in ids_used):
            ids.append(id)
    return ids


def get_unused_cable_tray_symbol_ids_for_purge(doc):
    '''
    Gets all unused cable tray symbol ids of categories
    - BuiltInCategory.OST_CableTrayFitting
    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused cable tray symbols and families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_cable_tray_symbol_ids)
    return ids


def get_used_conduit_symbol_ids(doc):
    '''
    Gets all used conduit symbol ids of categories
    - BuiltInCategory.OST_ConduitFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(doc, get_symbol_ids_for_conduit_types_in_model, 1)
    ids_used_in_types = get_symbol_ids_used_in_conduit_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    return ids


def get_unused_conduit_symbol_ids(doc):
    '''
    Gets all unused conduit symbol ids of categories
    - BuiltInCategory.OST_ConduitFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_used = get_used_conduit_symbol_ids(doc)
    ids_available = get_symbol_ids_for_conduit_types_in_model(doc)
    for id in ids_available:
        if (id not in ids_used):
            ids.append(id)
    return ids


def get_unused_conduit_symbol_ids_for_purge(doc):
    '''
    Gets all unused conduit symbol ids of categories
    - BuiltInCategory.OST_ConduitFitting
    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused conduit symbols and families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_conduit_symbol_ids)
    return ids


def get_used_pipe_symbol_ids(doc):
    '''
    Gets all used pipe symbol ids of categories
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
    Used: at least instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_in_model = rPurgeUtils.get_used_unused_type_ids(doc, get_symbol_ids_for_pipe_types_in_model, 1)
    ids_used_in_types = get_symbol_ids_used_in_pipe_types(doc)
    ids = merge_into_unique_list(ids, ids_in_model)
    ids = merge_into_unique_list(ids, ids_used_in_types)
    return ids


def get_unused_pipe_symbol_ids(doc):
    '''
    Gets all unused pipe symbol ids of categories
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    ids_used = get_used_pipe_symbol_ids(doc)
    ids_available = get_symbol_ids_for_pipe_types_in_model(doc)
    for id in ids_available:
        if (id not in ids_used):
            ids.append(id)
    return ids


def get_unused_pipe_symbol_ids_for_purge(doc):
    '''
    Gets all unused pipe symbol ids of categories
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused pipe symbols and families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_pipe_symbol_ids)
    return ids