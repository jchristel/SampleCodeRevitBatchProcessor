"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit walls. 
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

# import clr

# clr.AddReference("System.Core")
# from System import Linq

# clr.ImportExtensions(Linq)
# import System

# import common library modules
from duHast.Revit.Common.common import get_ids_from_element_collector

from duHast.Revit.Walls.Utility.walls_type_sorting import sort_wall_types_by_family_name
from duHast.Revit.Walls.curtain_walls import CURTAIN_WALL_FAMILY_NAME
from duHast.Revit.Walls.stacked_walls import STACKED_WALL_FAMILY_NAME
from duHast.Revit.Walls.Utility.walls_filter import (
    _get_all_wall_types_by_category,
    _get_all_wall_types_by_class,
)
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Common.parameter_set_utils import set_built_in_parameter_value
from duHast.Utilities.Objects import result as res

# import Autodesk

from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    ElementCategoryFilter,
    FamilyInstance,
    FamilySymbol,
    FilteredElementCollector,
    WallKind,
)

# -------------------------------------------- common variables --------------------

#: Built in wall family name for basic wall
BASIC_WALL_FAMILY_NAME = WallKind.Basic

#: List of all Built in wall family names
BUILTIN_WALL_TYPE_FAMILY_NAMES = [
    STACKED_WALL_FAMILY_NAME,
    CURTAIN_WALL_FAMILY_NAME,
    BASIC_WALL_FAMILY_NAME,
]


def get_all_wall_types_by_category(doc):
    """
    Gets all wall types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = _get_all_wall_types_by_category(doc)
    return collector


def get_all_wall_types_by_class(doc):
    """
    This will return a filtered element collector of all wall types by class in the model

    It will therefore not return any in place wall types since revit treats those as families...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = _get_all_wall_types_by_class(doc)
    return collector


# -------------------------------- in place wall types -------------------------------------------------------


def get_in_place_wall_family_instances(doc):
    """
    Returns all instances in place families of category wall in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing  in place wall instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    filter = ElementCategoryFilter(BuiltInCategory.OST_Walls)
    return FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)


def get_all_in_place_wall_type_ids(doc):
    """
    Gets all type ids off all available in place families of category wall.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    filter = ElementCategoryFilter(BuiltInCategory.OST_Walls)
    col = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    ids = get_ids_from_element_collector(col)
    return ids


# -------------------------------- basic wall types -------------------------------------------------------


def get_all_basic_wall_type_ids(doc):
    """
    Gets type ids off all available basic wall types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing all basic wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    dic = sort_wall_types_by_family_name(doc)
    if BASIC_WALL_FAMILY_NAME in dic:
        ids = dic[BASIC_WALL_FAMILY_NAME]
    return ids


def get_all_basic_wall_instances(doc, available_ids):
    """
    Gets all basic wall elements placed in model...ignores legend elements.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param available_ids:  Filter: curtain wall type ids to check wall instances for.
    :type available_ids: list of Autodesk.Revit.DB.ElementId

    :return: List of element ids representing all basic wall instances.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    instances = []
    col = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )
    for c in col:
        if c.GetTypeId() in available_ids:
            instances.append(c)
    return instances


def get_used_basic_wall_type_ids(doc, available_ids):
    """
    Gets all basic wall types used in model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param available_ids:  Filter: basic wall type ids to check wall instances for.
    :type available_ids: list of Autodesk.Revit.DB.ElementId

    :return: List of element ids representing all basic wall types in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )
    for c in col:
        if c.GetTypeId() in available_ids:
            ids.append(c.GetTypeId())
    return ids


def get_location_reference_type_name(wall_instance):
    """
    Gets the location line reference type name of a wall instance.

    # 0- Wall Centerline;
    # 1- Core Centerline;
    # 2- Finish Face: Exterior;
    # 3- Finish Face: Interior;
    # 4- Core Face: Exterior and
    # 5- Core Face: Interior.

    :param wall_instance: Wall instance to get the location line reference type name for.
    :type wall_instance: Autodesk.Revit.DB.Element
    :return: Name of the reference type.
    :rtype: str
    """

    location_line_reference_type_name = get_built_in_parameter_value(
        wall_instance, BuiltInParameter.WALL_KEY_REF_PARAM
    )
    return location_line_reference_type_name


def set_location_reference_type_name(doc, wall_instance, reference_type_name):
    """
    Sets the location line reference type name of a wall instance.

    Possible values are:

        - Wall Centerline
        - Core Centerline
        - Finish Face: Exterior
        - Finish Face: Interior
        - Core Face: Exterior
        - Core Face: Interior

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param wall_instance: Wall instance to change the location line reference type name for.
    :type wall_instance: Autodesk.Revit.DB.Element
    :param reference_type_name: Name of the reference type to set.
    :type reference_type_name: str
    :return: Result object with success status and message.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    reference_types_by_name = {
        "Wall Centerline": 0,
        "Core Centerline": 1,
        "Finish Face: Exterior": 2,
        "Finish Face: Interior": 3,
        "Core Face: Exterior": 4,
        "Core Face: Interior": 5,
    }

    return_value = res.Result()

    if reference_type_name not in reference_types_by_name:
        return_value.update_sep(
            False,
            "Invalid reference type name. Expect:\n{}".format(
                "\n".join(reference_types_by_name.keys())
            ),
        )
        return return_value

    result_change_loc_line = set_built_in_parameter_value(
        doc,
        wall_instance,
        BuiltInParameter.WALL_KEY_REF_PARAM,
        str(reference_types_by_name[reference_type_name]),
    )
    return result_change_loc_line
