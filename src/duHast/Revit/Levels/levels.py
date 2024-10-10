"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit levels helper functions.
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

import clr
import System


clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import common library modules
from duHast.Revit.Common.common import get_ids_from_element_collector

from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInCategory,
    ElementCategoryFilter,
    FamilySymbol,
    FilteredElementCollector,
    Level,
)


def get_levels_in_model(doc):
    """
    Get all levels in model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector with all levels in model.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = FilteredElementCollector(doc).OfClass(Level)
    return collector


def get_levels_in_view(doc, view):
    """
    Get all levels in a view

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view to get grids from.
    :type view: Autodesk.Revit.DB.View
    :return: A collector with all grids in view.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = FilteredElementCollector(doc, view.Id).OfClass(Level)
    return collector


# --------------------------------------------- utility functions ------------------


def get_levels_list_ascending(doc):
    """
    Gets a filtered element collector of all levels in the model ascending by project elevation.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of levels
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Levels)
        .WhereElementIsNotElementType()
        .ToList()
        .OrderBy(lambda l: l.ProjectElevation)
    )
    return collector


def get_levels_list_descending(doc):
    """
    Gets a filtered element collector of all levels in the model descending by project elevation.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of levels
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    levels_ascending = get_levels_list_ascending(doc)
    # using .Reverse() since this is a c# list, to get descending order rather than .reverse() which is a python list method
    levels_descending = levels_ascending.Reverse()
    return levels_descending


def get_level_elevation_by_name(doc, level_name):
    level_elevation = None
    levels = get_levels_in_model(doc=doc)
    for level in levels:
        if level.Name == level_name:
            return level.Elevation
    return level_elevation


# ------------------------------------------------- filters --------------------------------------------------------------------


def get_all_level_heads_by_category(doc):
    """
    Gets a filtered element collector of all level head types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level heads
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_LevelHeads)
        .WhereElementIsElementType()
    )
    return collector


def get_all_level_types_by_category(doc):
    """
    Gets a filtered element collector of all level types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Levels)
        .WhereElementIsElementType()
    )
    return collector


def get_all_level_type_ids_by_category(doc):
    """
    Gets a list of all level type ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Levels)
        .WhereElementIsElementType()
    )
    ids = get_ids_from_element_collector(collector)
    return ids


# -------------------------------------------------  purge --------------------------------------------------------------------


def get_all_level_head_family_type_ids(doc):
    """
    Gets ids of all level head family symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    filter = ElementCategoryFilter(BuiltInCategory.OST_LevelHeads)
    col = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    ids = get_ids_from_element_collector(col)
    return ids


def get_nearest_level_absolute(z, levels, ignore_level_names):
    """
    Returns the nearest level matching the Z value and the offset adjustment from the level (in metric!!) in a tuple.

    Note:
    Will return None if the placement level could not be determined.
    Nearest level is the level with the shortest absolute distance to the Z value and which is not in the ignore_level_names list.
    If the Z value is below the lowest level elevation in the model the lowest level will be returned.
    If the Z value is above the highest level elevation in the model the highest level will be returned.

    :param z: The Z coordinate (metric!)
    :type z: float
    :param levels: List of levels in the model. (sorted ascending)
    :type levels: list
    :return: Returns the level and the offset adjustment (in metric) from the source family instance level.
    :rtype: tuple
    """

    # distance placeholder
    absolute_distance_to_level = None
    nearest_level = None
    for level in levels:
        # check if level is to be ignored
        if level.Name in ignore_level_names:
            continue
        # get the absolute distance
        distance_to_level = abs(z - convert_imperial_feet_to_metric_mm(level.Elevation))
        # store the first level as the nearest level
        if absolute_distance_to_level is None:
            absolute_distance_to_level = distance_to_level
            nearest_level = level
        # check if the distance is shorter than the current shortest distance
        if distance_to_level < absolute_distance_to_level:
            absolute_distance_to_level = distance_to_level
            nearest_level = level

    if nearest_level == None:
        return None, None
    else:
        offset_from_level = z - convert_imperial_feet_to_metric_mm(
            nearest_level.Elevation
        )
        return nearest_level, offset_from_level


def get_nearest_lowest_level(z, levels, ignore_level_names):
    """
    Returns the nearest lowest level below the Z value and the offset adjustment from the level (in metric) in a tuple.

    Note:
    Will return None if the placement level could not be determined.
    Nearest level is the level below or at the Z value and which is not in the ignore_level_names list.

    :param z: The Z coordinate (metric!)
    :type z: float
    :param levels: List of levels in the model. (needs to be sorted ascending)
    :type levels: list
    :return: Returns the level and the offset adjustment (in metric) from the source family instance level.
    :rtype: tuple
    """

    # get level by Z coordinate of family
    nearest_level = None
    for level in levels:
        # check if level is to be ignored
        if level.Name in ignore_level_names:
            continue
        # store the lowest level for later
        if nearest_level == None:
            nearest_level = level
        # get the level by height
        if round(convert_imperial_feet_to_metric_mm(level.Elevation), 2) <= round(z, 2):
            nearest_level = level
        else:
            break

    # check if matching level was found and calc any offset
    if nearest_level != None:
        offset_from_level_adjustment = z - convert_imperial_feet_to_metric_mm(
            nearest_level.Elevation
        )
        return nearest_level, offset_from_level_adjustment
    else:
        return None, None
