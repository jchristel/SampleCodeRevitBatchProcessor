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

from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
from duHast.APISamples.MEP_Systems.RevitCableTrays import get_all_cable_tray_type_ids_in_model_by_category, get_all_cable_tray_types_by_category
from duHast.APISamples.MEP_Systems.RevitConduits import get_all_conduit_type_ids_in_model_by_category, get_all_conduit_types_by_category
from duHast.APISamples.MEP_Systems.RevitDucts import get_all_duct_type_ids_in_model_by_category, get_all_duct_types_by_category
from duHast.APISamples.MEP_Systems.RevitFlexDucts import get_all_flex_duct_type_ids_in_model_by_category, get_all_flex_duct_types_by_category
from duHast.APISamples.MEP_Systems.RevitPipes import get_all_pipe_type_ids_in_model_by_category, get_all_pipe_types_by_category
from duHast.APISamples.MEP_Systems.Utility.RevitMEPSystemNames import BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES, BUILTIN_CONDUIT_TYPE_FAMILY_NAMES, BUILTIN_DUCT_TYPE_FAMILY_NAMES, BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES, BUILTIN_PIPE_TYPE_FAMILY_NAMES
from duHast.APISamples.MEP_Systems.Utility.RevitMEPTypeSorting import sort_types_by_family_name


def get_used_duct_type_ids(doc):
    '''
    Gets all used duct type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_duct_type_ids_in_model_by_category, 1)
    return ids


def get_used_flex_duct_type_ids(doc):
    '''
    Gets all used flex duct type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_flex_duct_type_ids_in_model_by_category, 1)
    return ids


def get_used_conduit_type_ids(doc):
    '''
    Gets all used conduit type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_conduit_type_ids_in_model_by_category, 1)
    return ids


def get_used_cable_tray_type_ids(doc):
    '''
    Gets all used cable tray type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_cable_tray_type_ids_in_model_by_category, 1)
    return ids


def get_used_pipe_type_ids(doc):
    '''
    Gets all used pipe type ids available in model.
    Unused: at least instance of each of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_pipe_type_ids_in_model_by_category, 1)
    return ids


def get_unused_duct_type_ids(doc):
    '''
    Gets all unused duct type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_duct_type_ids_in_model_by_category, 0)
    return ids


def get_unused_flex_duct_type_ids(doc):
    '''
    Gets all unused flex duct type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_flex_duct_type_ids_in_model_by_category, 0)
    return ids


def get_unused_conduit_type_ids(doc):
    '''
    Gets all unused conduit type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_conduit_type_ids_in_model_by_category, 0)
    return ids


def get_unused_cable_tray_type_ids(doc):
    '''
    Gets all unused cable tray type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_cable_tray_type_ids_in_model_by_category, 0)
    return ids


def get_unused_pipe_type_ids(doc):
    '''
    Gets all unused pipe type ids available in model.
    Unused: not one instance of these types is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, get_all_pipe_type_ids_in_model_by_category, 0)
    return ids


def family_no_types_in_use(famTypeIds,unUsedTypeIds):
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


def get_unused_mep_system_type_ids_to_purge(doc, allTypeIDGetter, allTypesGetter, builtInFamilyTypeNames):
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

    ids = rPurgeUtils.get_used_unused_type_ids(doc, allTypeIDGetter, 0)
    # make sure there is at least on Stair type per system family left in model
    types = sort_types_by_family_name(doc, allTypesGetter)
    for key, value in types.items():
        if(key in builtInFamilyTypeNames ):
            if(family_no_types_in_use(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def get_unused_duct_type_ids_to_purge(doc):
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

    ids = get_unused_mep_system_type_ids_to_purge(doc,get_all_duct_type_ids_in_model_by_category, get_all_duct_types_by_category, BUILTIN_DUCT_TYPE_FAMILY_NAMES)
    return ids


def get_unused_flex_duct_type_ids_to_purge(doc):
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

    ids = get_unused_mep_system_type_ids_to_purge(doc,get_all_flex_duct_type_ids_in_model_by_category, get_all_flex_duct_types_by_category, BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES)
    return ids


def get_unused_conduit_type_ids_to_purge(doc):
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

    ids = get_unused_mep_system_type_ids_to_purge(doc, get_all_conduit_type_ids_in_model_by_category, get_all_conduit_types_by_category, BUILTIN_CONDUIT_TYPE_FAMILY_NAMES)
    return ids


def get_unused_cable_tray_type_ids_to_purge(doc):
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

    ids = get_unused_mep_system_type_ids_to_purge(doc, get_all_cable_tray_type_ids_in_model_by_category, get_all_cable_tray_types_by_category, BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES)
    return ids


def get_unused_pipe_type_ids_to_purge(doc):
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

    ids = get_unused_mep_system_type_ids_to_purge(doc, get_all_pipe_type_ids_in_model_by_category, get_all_pipe_types_by_category, BUILTIN_PIPE_TYPE_FAMILY_NAMES)
    return ids