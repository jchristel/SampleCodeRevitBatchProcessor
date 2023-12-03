"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a base helper functions relating to Revit view types. 
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
from System import Enum


# --------------------------------------------- View Types  ------------------


def _get_view_types(doc):
    """
    Returns all view family types in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewFamilyType)
    return collector


def get_view_type_enum_to_name_dict():
    """
    Get a dictionary of the ViewType enum to verbose name e.g. FloorPlan to Floor Plan
    :return: A dictionary in format of Autodesk.Revit.DB.ViewType.FloorPlan: "Floor Plan"
    :rtype: dict
    """
    enum_and_name_dict = {}
    view_type_enum_vals = Enum.GetValues(rdb.ViewType)

    for enum_val in view_type_enum_vals:
        str_val = str(enum_val)
        val_with_spaces = "".join(map(lambda x: x if x.islower() else " " + x, str_val))
        enum_and_name_dict[enum_val] = val_with_spaces.strip()

    return enum_and_name_dict
