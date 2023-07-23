"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit stacked walls. 
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

# import Autodesk
import Autodesk.Revit.DB as rdb
from duHast.Revit.Common import common as com

#: Built in wall family name for stacked wall
STACKED_WALL_FAMILY_NAME = "Stacked Wall"

# -------------------------------- stacked wall types -------------------------------------------------------


def get_all_stacked_wall_instances(doc):
    """
    Gets all stacked wall elements placed in model...ignores legend elements.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing wall instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_StackedWalls)
        .WhereElementIsNotElementType()
    )


def get_all_stacked_wall_types(doc):
    """
    Gets all stacked wall element types used by instances placed in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing stacked wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_StackedWalls)
        .WhereElementIsElementType()
    )


def get_all_stacked_wall_type_ids(doc):
    """
    Gets all stacked wall element types available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing stacked wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_StackedWalls)
        .WhereElementIsElementType()
    )
    ids = com.get_ids_from_element_collector(col)
    return ids
