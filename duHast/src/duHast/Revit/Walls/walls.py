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

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)
import System

# import common library modules
from duHast.Revit.Common import common as com

from duHast.Revit.Walls.Utility import walls_type_sorting as rWallTypeSort
from duHast.Revit.Walls import curtain_walls as rCurtainWall
from duHast.Revit.Walls import stacked_walls as rStackedWall
from duHast.Revit.Walls.Utility import walls_filter as rWallFilter

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------

#: Built in wall family name for basic wall
BASIC_WALL_FAMILY_NAME = "Basic Wall"

#: List of all Built in wall family names
BUILTIN_WALL_TYPE_FAMILY_NAMES = [
    rStackedWall.STACKED_WALL_FAMILY_NAME,
    rCurtainWall.CURTAIN_WALL_FAMILY_NAME,
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

    collector = rWallFilter._get_all_wall_types_by_category(doc)
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

    collector = rWallFilter._get_all_wall_types_by_class(doc)
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

    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Walls)
    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.FamilyInstance)
        .WherePasses(filter)
    )


def get_all_in_place_wall_type_ids(doc):
    """
    Gets all type ids off all available in place families of category wall.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Walls)
    col = (
        rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    )
    ids = com.get_ids_from_element_collector(col)
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
    dic = rWallTypeSort.sort_wall_types_by_family_name(doc)
    if dic.has_key(BASIC_WALL_FAMILY_NAME):
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
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Walls)
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
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )
    for c in col:
        if c.GetTypeId() in available_ids:
            ids.append(c.GetTypeId())
    return ids
