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

from Autodesk.Revit.DB import (
    BuiltInCategory,
    FilteredElementCollector,
    WallKind,
)

from duHast.Revit.Walls.Utility.walls_type_sorting import sort_wall_types_by_family_name

#: Built in wall family name for curtain wall
CURTAIN_WALL_FAMILY_NAME = WallKind.Curtain


def get_all_curtain_wall_type_ids(doc):
    """
    Gets type ids off all available curtain wall types in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    dic = sort_wall_types_by_family_name(doc)
    if CURTAIN_WALL_FAMILY_NAME in dic:
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
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
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
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )
    for c in col:
        if c.GetTypeId() in available_ids:
            instances.append(c.GetTypeId())
    return instances
