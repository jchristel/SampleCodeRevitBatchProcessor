"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit stair landing elements. 
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
import Autodesk.Revit.DB.Architecture as rdbA

from duHast.Revit.Common import common as com

#: list of built in parameters attached to stair sub types
STAIR_LANDING_TYPE_PARAS = [rdb.BuiltInParameter.STAIRSTYPE_LANDING_TYPE]


def get_stair_landing_types_by_class(doc):
    """
    Gets a filtered element collector of all Stair landing types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing stair landing types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsLandingType)


def get_stair_landing_types_ids_by_class(doc):
    """
    Gets all Stair landing element type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing stair landing types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_class = get_stair_landing_types_by_class(doc)
    ids = com.get_ids_from_element_collector(col_class)
    return ids
