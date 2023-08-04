"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit curtain walls utility functions. 
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

import Autodesk.Revit.DB as rdb
from duHast.Revit.Walls.Utility import walls_type_sorting as rWallTypeSort

#: Built in wall family name for curtain wall
CURTAIN_WALL_FAMILY_NAME = "Curtain Wall"


def get_all_curtain_wall_type_ids(doc):
    """
    Gets type ids off all available curtain wall types in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    dic = rWallTypeSort.sort_wall_types_by_family_name(doc)
    if dic.has_key(CURTAIN_WALL_FAMILY_NAME):
        ids = dic[CURTAIN_WALL_FAMILY_NAME]
    return ids


def get_all_curtain_wall_instances(doc, available_ids):
    """
    Gets all curtain wall elements placed in model...ignores legend elements.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param available_ids: Filter: curtain wall type ids to check wall instances for.
    :type available_ids: list of Autodesk.Revit.DB.ElementId
    :return: List of wall instances
    :rtype: List of Autodesk.Revit.DB.Wall
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


def get_placed_curtain_wall_type_ids(doc, available_ids):
    """
    Gets all used curtain wall types in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param available_ids: Filter: curtain wall type ids to check wall types for.
    :type available_ids: list of Autodesk.Revit.DB.ElementId
    :return: List of wall instances
    :rtype: List of Autodesk.Revit.DB.Wall
    """

    instances = []
    col = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )
    for c in col:
        if c.GetTypeId() in available_ids:
            instances.append(c.GetTypeId())
    return instances
