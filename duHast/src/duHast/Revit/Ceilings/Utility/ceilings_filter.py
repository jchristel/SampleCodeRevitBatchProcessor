# import Autodesk
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit ceilings utility functions. 
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


def _get_all_ceiling_types_by_category(doc):
    """
    Gets a filtered element collector of all ceiling types in the model:

    - Compound Ceiling
    - In place families or loaded families
    - Basic Ceiling

    Filters by category.
    It will therefore not return any roof soffit types ..

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Ceilings)
        .WhereElementIsElementType()
    )
    return collector


def _get_ceiling_types_by_class(doc):
    """
    Gets a filtered element collector of all ceiling types in the model:

    - Roof Soffit
    - Compound Ceiling
    - Basic Ceiling

    Filters by class.
    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdb.CeilingType)
