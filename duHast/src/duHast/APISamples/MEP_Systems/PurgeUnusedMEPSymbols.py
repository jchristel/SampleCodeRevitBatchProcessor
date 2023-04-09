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

from duHast.APISamples.Family import RevitFamilyUtils as rFam
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils

from duHast.APISamples.MEP_Systems.RevitPipes import GetSymbolIdsForPipeTypesInModel, GetSymbolIdsUsedInPipeTypes
from duHast.APISamples.MEP_Systems.RevitConduits import GetSymbolIdsForConduitTypesInModel, GetSymbolIdsUsedInConduitTypes
from duHast.APISamples.MEP_Systems.RevitCableTrays import GetSymbolIdsForCableTrayTypesInModel, GetSymbolIdsUsedInCableTrayTypes
from duHast.APISamples.MEP_Systems.RevitDucts import GetSymbolIdsForDuctTypesInModel, GetSymbolIdsUsedInDuctTypes
from duHast.APISamples.MEP_Systems.RevitFlexDucts import GetSymbolIdsUsedInFlexDuctTypes
from duHast.APISamples.MEP_Systems.Utility.MergeLists import MergeIntoUniqueList


def GetUsedDuctAndFlexDuctSymbolIds(doc):
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
    idsInModel = rPurgeUtils.GetUsedUnusedTypeIds(doc, GetSymbolIdsForDuctTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInDuctTypes(doc)
    idsUsedInFlexTypes = GetSymbolIdsUsedInFlexDuctTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    ids = MergeIntoUniqueList(ids, idsUsedInFlexTypes)
    return ids


def GetUnUsedDuctAndFlexDuctSymbolIds(doc):
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
    idsUsed = GetUsedDuctAndFlexDuctSymbolIds(doc)
    idsAvailable = GetSymbolIdsForDuctTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids


def GetUnUsedDuctAndFlexDuctSymbolIdsForPurge(doc):
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

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedDuctAndFlexDuctSymbolIds)
    return ids


def GetUsedCableTraySymbolIds(doc):
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
    idsInModel = rPurgeUtils.GetUsedUnusedTypeIds(doc, GetSymbolIdsForCableTrayTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInCableTrayTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    return ids


def GetUnUsedCableTraySymbolIds(doc):
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
    idsUsed = GetUsedCableTraySymbolIds(doc)
    idsAvailable = GetSymbolIdsForCableTrayTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids


def GetUnUsedCableTraySymbolIdsForPurge(doc):
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

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedCableTraySymbolIds)
    return ids


def GetUsedConduitSymbolIds(doc):
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
    idsInModel = rPurgeUtils.GetUsedUnusedTypeIds(doc, GetSymbolIdsForConduitTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInConduitTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    return ids


def GetUnUsedConduitSymbolIds(doc):
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
    idsUsed = GetUsedConduitSymbolIds(doc)
    idsAvailable = GetSymbolIdsForConduitTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids


def GetUnUsedConduitSymbolIdsForPurge(doc):
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

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedConduitSymbolIds)
    return ids


def GetUsedPipeSymbolIds(doc):
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
    idsInModel = rPurgeUtils.GetUsedUnusedTypeIds(doc, GetSymbolIdsForPipeTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInPipeTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    return ids


def GetUnUsedPipeSymbolIds(doc):
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
    idsUsed = GetUsedPipeSymbolIds(doc)
    idsAvailable = GetSymbolIdsForPipeTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids


def GetUnUsedPipeSymbolIdsForPurge(doc):
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

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedPipeSymbolIds)
    return ids