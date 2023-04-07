'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging unused mep system types.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.MEP_Systems.RevitCableTrays import GetAllCableTrayTypeIdsInModelByCategory, GetAllCableTrayTypesByCategory
from duHast.APISamples.MEP_Systems.RevitConduits import GetAllConduitTypeIdsInModelByCategory, GetAllConduitTypesByCategory
from duHast.APISamples.MEP_Systems.RevitDucts import GetAllDuctTypeIdsInModelByCategory, GetAllDuctTypesByCategory
from duHast.APISamples.MEP_Systems.RevitFlexDucts import GetAllFlexDuctTypeIdsInModelByCategory, GetAllFlexDuctTypesByCategory
from duHast.APISamples.MEP_Systems.RevitPipes import GetAllPipeTypeIdsInModelByCategory, GetAllPipeTypesByCategory
from duHast.APISamples.MEP_Systems.Utility.RevitMEPSystemNames import BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES, BUILTIN_CONDUIT_TYPE_FAMILY_NAMES, BUILTIN_DUCT_TYPE_FAMILY_NAMES, BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES, BUILTIN_PIPE_TYPE_FAMILY_NAMES
from duHast.APISamples.MEP_Systems.Utility.RevitMEPTypeSorting import SortTypesByFamilyName


def GetUsedDuctTypeIds(doc):
    '''
    Gets all used duct type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllDuctTypeIdsInModelByCategory, 1)
    return ids


def GetUsedFlexDuctTypeIds(doc):
    '''
    Gets all used flex duct type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllFlexDuctTypeIdsInModelByCategory, 1)
    return ids


def GetUsedConduitTypeIds(doc):
    '''
    Gets all used conduit type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllConduitTypeIdsInModelByCategory, 1)
    return ids


def GetUsedCableTrayTypeIds(doc):
    '''
    Gets all used cable tray type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCableTrayTypeIdsInModelByCategory, 1)
    return ids


def GetUsedPipeTypeIds(doc):
    '''
    Gets all used pipe type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllPipeTypeIdsInModelByCategory, 1)
    return ids


def GetUnUsedDuctTypeIds(doc):
    '''
    Gets all unused duct type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllDuctTypeIdsInModelByCategory, 0)
    return ids


def GetUnUsedFlexDuctTypeIds(doc):
    '''
    Gets all unused flex duct type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllFlexDuctTypeIdsInModelByCategory, 0)
    return ids


def GetUnUsedConduitTypeIds(doc):
    '''
    Gets all unused conduit type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllConduitTypeIdsInModelByCategory, 0)
    return ids


def GetUnUsedCableTrayTypeIds(doc):
    '''
    Gets all unused cable tray type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCableTrayTypeIdsInModelByCategory, 0)
    return ids


def GetUnUsedPipeTypeIds(doc):
    '''
    Gets all unused pipe type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllPipeTypeIdsInModelByCategory, 0)
    return ids


def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    Returns False if any symbols (types) of a family (first list) are in use in a model (second list).
    TODO: repetitive code...Consider generic function!
    :param famTypeIds: List of family symbols (types).
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: List of unused family symbols (types)
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId
    :return: True if all ids in first list are also in second list, otherwise False.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match


def GetUnUsedMEPSystemTypeIdsToPurge(doc, allTypeIDGetter, allTypesGetter, builtInFamilyTypeNames):
    '''
    Gets the ids of unused MEP system types. 
    In the case that no mep system instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one mep system type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param allTypeIDGetter: Function getting all available system type ids as a list.
    :type allTypeIDGetter: func(doc) -> List Autodesk.Revit.ED.ElementId
    :param allTypesGetter: Function getting all available system types as a collector.
    :type allTypesGetter: func(doc) -> Autodesk.Revit.DB.FilteredElementCollector
    :param builtInFamilyTypeNames: List containing all available major type names.
    :type builtInFamilyTypeNames: List str
    :return: A list of ids representing mep system types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, allTypeIDGetter, 0)
    # make sure there is at least on Stair type per system family left in model
    types = SortTypesByFamilyName(doc, allTypesGetter)
    for key, value in types.items():
        if(key in builtInFamilyTypeNames ):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def GetUnUsedDuctTypeIdsToPurge(doc):
    '''
    Gets all unused duct type ids. 
    This method can be used to safely delete unused duct types:
    In the case that no duct instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one duct type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc,GetAllDuctTypeIdsInModelByCategory, GetAllDuctTypesByCategory, BUILTIN_DUCT_TYPE_FAMILY_NAMES)
    return ids


def GetUnUsedFlexDuctTypeIdsToPurge(doc):
    '''
    Gets all unused flex duct type ids. 
    This method can be used to safely delete unused flex duct types:
    In the case that no flex duct instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one flex duct type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc,GetAllFlexDuctTypeIdsInModelByCategory, GetAllFlexDuctTypesByCategory, BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES)
    return ids


def GetUnUsedConduitTypeIdsToPurge(doc):
    '''
    Gets all unused conduit type ids. 
    This method can be used to safely delete unused conduit types:
    In the case that no conduit instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one conduit type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllConduitTypeIdsInModelByCategory, GetAllConduitTypesByCategory, BUILTIN_CONDUIT_TYPE_FAMILY_NAMES)
    return ids


def GetUnUsedCableTrayTypeIdsToPurge(doc):
    '''
    Gets all unused cable tray type ids. 
    This method can be used to safely delete unused cable tray types:
    In the case that no cable tray instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one cable tray type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllCableTrayTypeIdsInModelByCategory, GetAllCableTrayTypesByCategory, BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES)
    return ids


def GetUnUsedPipeTypeIdsToPurge(doc):
    '''
    Gets all unused pipe type ids. 
    This method can be used to safely delete unused pipe types:
    In the case that no pipe instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one pipe type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllPipeTypeIdsInModelByCategory, GetAllPipeTypesByCategory, BUILTIN_PIPE_TYPE_FAMILY_NAMES)
    return ids