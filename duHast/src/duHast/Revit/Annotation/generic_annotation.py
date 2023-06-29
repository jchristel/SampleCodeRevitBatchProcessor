"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit generic annotation helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

from duHast.Revit.Common import parameter_get_utils as rParaGet

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------

# returns all  GenericAnnotation types in a model
# doc:   current model document
def get_all_generic_annotation_types_by_category(doc):
    """
    This will return a filtered element collector of all GenericAnnotation types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_GenericAnnotation)
        .WhereElementIsElementType()
    )
    return collector


# returns all  GenericAnnotation types in a model
# doc:   current model document
def get_all_generic_annotation_type_ids_by_category(doc):
    """
    This will return a list of all GenericAnnotation types (symbols) id's in the model excluding shared families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = get_all_generic_annotation_types_by_category(doc)
    for c in col:
        parameter_match = False
        # get the family object to check whether it is a shared family
        fam = c.Family
        id = rParaGet.get_built_in_parameter_value(
            fam, rdb.BuiltInParameter.FAMILY_SHARED
        )
        if id != None:
            parameter_match = True
            if id == "No" and c.Id not in ids:
                ids.append(c.Id)
        if parameter_match == False:
            # family cant be of type shared...
            ids.append(c.Id)
    return ids
