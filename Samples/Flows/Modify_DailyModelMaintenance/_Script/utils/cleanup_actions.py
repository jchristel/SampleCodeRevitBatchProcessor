#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#


from collections import namedtuple
from System.Collections.Generic import List
import Autodesk.Revit.DB as rdb

import settings as settings  # sets up all commonly used variables and path locations!

# import script_util
import script_util

from duHast.Revit.Warnings import solver_duplicate_mark as rwsDplMark
from duHast.Revit.Common import custom_element_filter as rCusFilter
from duHast.Revit.Common import element_filtering as elFilter
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Family import family_utils as rFamU

from duHast.Revit.Levels.levels import get_levels_in_model
from duHast.Revit.Grids.grids import get_grids_in_model
from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Revit.Walls.walls import get_all_basic_wall_instances
from duHast.Revit.Ceilings.ceilings import (
    get_all_ceiling_instances_in_model_by_category,
)
from duHast.Revit.Floors.floors import get_all_floor_instances_in_model_by_category
from duHast.Utilities.console_out import output


# set up custom duplicate mark filter and its filter values
CUSTOM_DUPLICATE_MARK_SOLVER = rwsDplMark.RevitWarningsSolverDuplicateMark(
    elFilter.is_element_not_of_built_in_category,  # check if element does not belongs to a given list of categories
    [  # category list (items can not be of this category)
        rdb.BuiltInCategory.OST_Windows,
        rdb.BuiltInCategory.OST_Doors,
    ],
)


def action_out(message):
    """
    Output function for filter actions

    :param message: the message to be printed out
    :type message: str
    """
    output(
        message,
        script_util.Output,
    )


# ----------------------------------------------- element workset settings ----------------------------------------

# ------------- common: always true  used when no element collector does not require further filtering --------------


# doc       current model
# elementId the elements id
def action_always_true(doc, elementId):
    """set up a function which returns always true"""
    return True


# class instance of custom filter filtering out riser place holder family instances
FILTER_ALWAYS_TRUE = rCusFilter.RevitCustomElementFilter([action_always_true])

# ------------- risers and placeholders --------------


def action_family_name_hyd_stack_placeholder(doc, element_id):
    """
    Set up a function checking for a specific family name of coordination families

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId
    :return: True if element family name does equal "Riser_Placeholder", otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_contains_any_of_values(
        ["Riser_Placeholder"], elCustomFilterTest.value_is_family_name, action_out
    )
    flag = test(doc, element_id)
    return flag


def action_family_name_riser_placeholder(doc, element_id):
    """
    Set up a function checking for a specific family name of coordination families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element family name does equal "placeholder one" or "placeholder two", otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_contains_any_of_values(
        ["placeholder one", "placeholder two"],
        elCustomFilterTest.value_is_family_name,
        action_out,
    )
    flag = test(doc, element_id)
    return flag


# class instance of custom filter filtering out hydraulic stack place holder family instances
FILTER_HYD_STACK_PLACEHOLDERS = rCusFilter.RevitCustomElementFilter(
    [action_family_name_hyd_stack_placeholder]
)

# class instance of custom filter filtering out riser place holder family instances
FILTER_RISER_PLACEHOLDERS = rCusFilter.RevitCustomElementFilter(
    [action_family_name_riser_placeholder]
)


# doc       current model document
def get_riser_placeholders(doc):
    """returns all instances of category plumbing fixtures"""
    col = rFamU.get_family_instances_of_built_in_category(
        doc, rdb.BuiltInCategory.OST_PlumbingFixtures
    )
    return col


# doc       current model document
def get_arch_column_instances(doc):
    """returns all instances of category arch columns"""
    col = rFamU.get_family_instances_of_built_in_category(
        doc, rdb.BuiltInCategory.OST_Columns
    )
    return col


# ------------- scope boxes--------------


# doc       current model document
def get_scope_boxes(doc):
    """returns all scope boxes"""
    col = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_VolumeOfInterest
    )
    return col


# ------------- room separation lines -------------


# doc       current model document
def get_room_separation_lines(doc):
    """returns all room separation lines"""
    col = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_RoomSeparationLines
    )
    return col


# ------------- doors -------------


def action_family_name_does_not_contain_protection(doc, element_id):
    """
    Set up a function checking for a door protection family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element family name does not contain "_Protection_", otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_does_not_contains_any_of_values(
        ["_Protection_"], elCustomFilterTest.value_in_family_name, action_out
    )
    flag = test(doc, element_id)
    return flag


# class instance of custom filter filtering out riser place holder family instances
FILTER_DOORS_DOOR_PROTECTION = rCusFilter.RevitCustomElementFilter(
    [action_family_name_does_not_contain_protection]
)


# doc       current model document
def get_doors(doc):
    """returns all doors"""
    col = rFamU.get_family_instances_of_built_in_category(
        doc, rdb.BuiltInCategory.OST_Doors
    )
    return col


# ------------- walls -------------


def action_symbol_name_does_not_contain_facade_or_cc(doc, element_id):
    """
    set up a function checking whether wall types does not contain FACADE or CC-

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element name does not contain "FACADE", "CC-", otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_does_not_contains_any_of_values(
        ["FACADE", "CC-"], elCustomFilterTest.value_in_name, action_out
    )
    flag = test(doc, element_id)
    return flag


def action_symbol_name_contain_cc(doc, element_id):
    """
    set up a function checking whether wall types contain CC-

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element name contain "CC-", otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_contains_any_of_values(
        ["CC-"], elCustomFilterTest.value_in_name, action_out
    )
    flag = test(doc, element_id)
    return flag


def action_symbol_name_contain_facade(doc, element_id):
    """
    Set up a function checking whether wall types contain FACADE

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element name contain "FACADE", otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_contains_any_of_values(
        ["FACADE"], elCustomFilterTest.value_in_name, action_out
    )
    flag = test(doc, element_id)
    return flag


# class instance of custom filter filtering out internal wall instances
FILTER_WALL_TYPES_INTERNAL = rCusFilter.RevitCustomElementFilter(
    [action_symbol_name_does_not_contain_facade_or_cc]
)
# class instance of custom filter filtering out structural wall instances
FILTER_WALL_TYPES_STRUCTURAL = rCusFilter.RevitCustomElementFilter(
    [action_symbol_name_contain_cc]
)
# class instance of custom filter filtering out FACADE wall instances
FILTER_WALL_TYPES_FACADE = rCusFilter.RevitCustomElementFilter(
    [action_symbol_name_contain_facade]
)

# ------------- Floors -------------


def action_symbol_name_contains_structure(doc, element_id):
    """
    Set up a function checking whether floor types contains 'Sample 1', 'Sample 2', 'Sample 3'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element name contain 'CONCRETE', 'Concrete', 'HOB', otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_contains_any_of_values(
        ["Sample 1", "Sample 2", "Sample 3"],
        elCustomFilterTest.value_in_name,
        action_out,
    )
    flag = test(doc, element_id)
    return flag


# class instance of custom filter filtering out internal wall instances
FILTER_FLOOR_TYPES_STRUCTURAL = rCusFilter.RevitCustomElementFilter(
    [action_symbol_name_contains_structure]
)

# ------------- Structural columns -------------


# doc       current model document
def get_structural_columns(doc):
    """returns all doors"""
    col = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_StructuralColumns
    )
    return col


# ------------- FFE -------------


def action_symbol_name_does_not_contain_ffe_names(doc, element_id):
    """
    Set up a function checking whether family does not contain any of the test values

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_id: id of element to be checked against condition
    :type element_id: Autodesk.Revit.DB.ElementId

    :return: True if element family name does equal sample values provided , otherwise False
    :rtype: bool
    """

    test = elCustomFilterAction.action_element_property_does_not_contains_any_of_values(
        [
            "Sample 1",
            "Sample 2",
            "Sample 3",
            "Sample 4",
        ],
        elCustomFilterTest.value_is_family_name,
        action_out,
    )
    flag = test(doc, element_id)
    return flag


# class instance of custom filter filtering out FFE instances
FILTER_FFE = rCusFilter.RevitCustomElementFilter(
    [
        action_symbol_name_does_not_contain_ffe_names,
    ]
)


# doc       current model document
def get_ffe(doc):
    """returns all instances of ffe"""
    cats = List[rdb.BuiltInCategory](
        [
            rdb.BuiltInCategory.OST_Casework,
            rdb.BuiltInCategory.OST_CommunicationDevices,
            rdb.BuiltInCategory.OST_DataDevices,
            rdb.BuiltInCategory.OST_ElectricalEquipment,
            rdb.BuiltInCategory.OST_ElectricalFixtures,
            rdb.BuiltInCategory.OST_FireAlarmDevices,
            rdb.BuiltInCategory.OST_Furniture,
            rdb.BuiltInCategory.OST_FurnitureSystems,
            rdb.BuiltInCategory.OST_GenericModel,
            rdb.BuiltInCategory.OST_LightingFixtures,
            rdb.BuiltInCategory.OST_LightingDevices,
            rdb.BuiltInCategory.OST_MechanicalEquipment,
            rdb.BuiltInCategory.OST_NurseCallDevices,
            rdb.BuiltInCategory.OST_PlumbingFixtures,
            rdb.BuiltInCategory.OST_SecurityDevices,
            rdb.BuiltInCategory.OST_SpecialityEquipment,
            rdb.BuiltInCategory.OST_TelephoneDevices,
        ]
    )
    col = rFamU.get_family_instances_by_built_in_categories(doc, cats)
    return col


# set up a named tuple to store workset action data in it
# getElements = returns a list of elements of which the workset may require changing
# filter        RevitCustomFilter class object
# targetWorksetName     which workset to move the element to
workset_action = namedtuple(
    "workset_action", "get_elements filter target_workset_name action_name"
)

# list of all workset actions
WORKSET_ACTIONS_BY_FILE = {
    "Revit": [  # actions for all models
        workset_action(
            get_room_separation_lines,
            FILTER_ALWAYS_TRUE,
            "INTERIOR",
            "Move room separation lines",
        ),
        workset_action(get_all_rooms, FILTER_ALWAYS_TRUE, "30_INTERIOR", "Move rooms"),
        workset_action(
            get_scope_boxes,
            FILTER_ALWAYS_TRUE,
            "Shared Levels and Grids",
            "Move scope boxes",
        ),
        workset_action(
            get_grids_in_model,
            FILTER_ALWAYS_TRUE,
            "Shared Levels and Grids",
            "Move grids",
        ),
        workset_action(
            get_levels_in_model,
            FILTER_ALWAYS_TRUE,
            "Shared Levels and Grids",
            "Move levels",
        ),
        workset_action(
            get_all_basic_wall_instances,
            FILTER_WALL_TYPES_STRUCTURAL,
            "STRUCTURE",
            "Move walls",
        ),
        workset_action(
            get_structural_columns,
            FILTER_ALWAYS_TRUE,
            "STRUCTURE",
            "Move structural columns",
        ),
        workset_action(
            get_all_floor_instances_in_model_by_category,
            FILTER_FLOOR_TYPES_STRUCTURAL,
            "STRUCTURE",
            "Move structual floors",
        ),
        workset_action(
            get_all_basic_wall_instances,
            FILTER_WALL_TYPES_FACADE,
            "FACADE",
            "Move walls facade",
        ),
    ],
    "Revit": [  # actions for all base build models
        workset_action(
            get_doors, FILTER_DOORS_DOOR_PROTECTION, "INTERIOR", "Move doors"
        ),
        workset_action(
            get_all_basic_wall_instances,
            FILTER_WALL_TYPES_INTERNAL,
            "INTERIOR",
            "Move interior walls",
        ),
        workset_action(
            get_all_ceiling_instances_in_model_by_category,
            FILTER_ALWAYS_TRUE,
            "INTERIOR",
            "Move interior ceilings",
        ),
        workset_action(get_ffe, FILTER_FFE, "FF&E", "Move ff and e"),
    ],
}
