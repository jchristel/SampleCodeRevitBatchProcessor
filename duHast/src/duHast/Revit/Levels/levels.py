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
import System


clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import common library modules
from duHast.Revit.Common import common as com

# import Autodesk
import Autodesk.Revit.DB as rdb


def get_levels_in_model(doc):
    """
    Get all levels in model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector with all levels in model.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.Level)
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
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Levels)
        .WhereElementIsNotElementType()
        .ToList()
        .OrderBy(lambda l: l.ProjectElevation)
    )
    return collector


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
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_LevelHeads)
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
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Levels)
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
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Levels)
        .WhereElementIsElementType()
    )
    ids = com.get_ids_from_element_collector(collector)
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
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_LevelHeads)
    col = (
        rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    )
    ids = com.get_ids_from_element_collector(col)
    return ids
