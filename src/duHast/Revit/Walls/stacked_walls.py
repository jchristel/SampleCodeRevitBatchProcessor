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

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInCategory,
    FilteredElementCollector,
    WallKind,
)

from duHast.Revit.Common.common import get_ids_from_element_collector

#: Built in wall family name for stacked wall
STACKED_WALL_FAMILY_NAME = WallKind.Stacked

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
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StackedWalls)
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
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StackedWalls)
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
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StackedWalls)
        .WhereElementIsElementType()
    )
    ids = get_ids_from_element_collector(col)
    return ids
