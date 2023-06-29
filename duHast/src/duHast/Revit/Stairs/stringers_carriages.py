"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit stair stringers and carriage elements. 
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

from duHast.Revit.Common import common as com

#: list of built in parameters for stair support types
STAIR_SUPPORT_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_LEFT_SIDE_SUPPORT_TYPE,
    rdb.BuiltInParameter.STAIRSTYPE_INTERMEDIATE_SUPPORT_TYPE,
    rdb.BuiltInParameter.STAIRSTYPE_RIGHT_SIDE_SUPPORT_TYPE,
]


def get_all_stair_stringers_carriage_by_category(doc):
    """
    Gets a filtered element collector of all stair stringers and carriage types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing stair stringers and carriage types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_StairsStringerCarriage)
        .WhereElementIsElementType()
    )
    return collector


def get_all_stair_stringers_carriage_type_ids_by_category(doc):
    """
    Get all Stair stringers and carriage element type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing stair stringer and carriage types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_cat = get_all_stair_stringers_carriage_by_category(doc)
    ids = com.get_ids_from_element_collector(col_cat)
    return ids
