"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit detail items.
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

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import common library modules
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.DetailItems.Utility import (
    detail_items_type_sorting as rDetailItemTypeSort,
)

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    ElementId,
    FilledRegion,
    FilteredElementCollector,
)

#: class name Autodesk.Revit.DB.ElementType
ELEMENT_TYPE = "Autodesk.Revit.DB.ElementType"
#: class name Autodesk.Revit.DB.FilledRegionType
FILLED_REGION_TYPE = "Autodesk.Revit.DB.FilledRegionType"
#: class name Autodesk.Revit.DB.FamilySymbol
FAMILY_SYMBOL = "Autodesk.Revit.DB.FamilySymbol"

#: List of class names which can be detailed components
DETAIL_COMPONENT_TYPES = [ELEMENT_TYPE, FILLED_REGION_TYPE, FAMILY_SYMBOL]

# --------------------------------------------- filled region ------------------


def get_filled_regions_in_model(doc):
    """
    Gets all filled region instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list containing floor instances.
    :rtype: list Autodesk.Revit.DB.FilledRegion
    """

    return FilteredElementCollector(doc).OfClass(FilledRegion).ToList()


def get_all_filled_region_type_ids_available(doc):
    """
    Gets all filled region types ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing filled region types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    dic = rDetailItemTypeSort.build_detail_type_ids_dictionary(
        get_all_detail_types_by_category(doc)
    )
    if FILLED_REGION_TYPE in dic:
        return dic[FILLED_REGION_TYPE]
    else:
        return []


"""
TODO: check for actual class...
"""

# -------------------------------- detail components -------------------------------------------------------


def get_all_detail_types_by_category(doc):
    """
    Gets all detail component types in the model.

    Filters by built in category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing detail component types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_DetailComponents)
        .WhereElementIsElementType()
    )
    return collector


# -------------------------------- repeating detail types -------------------------------------------------------


def get_all_repeating_detail_type_ids_available(doc):
    """
    Get all repeating detail type id's in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    dic = rDetailItemTypeSort.build_detail_type_ids_dictionary(
        get_all_detail_types_by_category(doc)
    )
    if ELEMENT_TYPE in dic:
        return dic[ELEMENT_TYPE]
    else:
        return []


# -------------------------------- Detail families -------------------------------------------------------


def get_all_detail_symbol_ids_available(doc):
    """
    Gets all detail symbol (types) ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing detail symbols.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    dic = rDetailItemTypeSort.build_detail_type_ids_dictionary(
        get_all_detail_types_by_category(doc)
    )
    if FAMILY_SYMBOL in dic:
        return dic[FAMILY_SYMBOL]
    else:
        return []


def get_detail_symbols_used_in_repeating_details(doc, ids_repeat_det):
    """
    Gets the ids of all symbols used in repeating details.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param idsRepeatDet: List of repeating detail type ids.
    :type idsRepeatDet: list Autodesk.Revit.DB.ElementIds

    :return: List of family symbol (type) ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = []
    for id_r in ids_repeat_det:
        repeat_detail = doc.GetElement(id_r)
        id = rParaGet.get_built_in_parameter_value(
            repeat_detail, BuiltInParameter.REPEATING_DETAIL_ELEMENT
        )
        if id not in ids and id != ElementId.InvalidElementId and id != None:
            ids.append(id)
    return ids
