"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging annotation types. 
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
    BuiltInParameter,
    ElementId,
    FilteredElementCollector,
    ViewSchedule,
)

from duHast.Revit.Annotation.generic_annotation import (
    get_all_generic_annotation_type_ids_by_category,
)
from duHast.Revit.Family.purge_unused_family_types import (
    get_unused_in_place_ids_for_purge,
)
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Common.common import get_unused_type_ids_in_model
from duHast.Revit.Annotation.annotation import get_anno_symbol_arrow_head_ids
from duHast.Revit.Annotation.dimensions import (
    get_all_dimension_elements,
    get_dim_type_arrow_head_ids,
    get_dim_types,
    get_symbol_ids_from_dim_types,
)
from duHast.Revit.Annotation.multi_ref_annotation import (
    get_all_multi_ref_annotation_elements,
    get_all_similar_multi_reference_anno_types,
    get_all_multi_ref_annotation_types,
)
from duHast.Revit.Annotation.text import (
    get_all_text_annotation_elements,
    get_text_type_arrow_head_ids,
    get_all_text_types,
)
from duHast.Revit.Annotation.arrow_heads import get_arrow_type_ids_in_model
from duHast.Revit.Annotation.independent_tags import (
    get_independent_tag_type_arrow_head_ids,
)
from duHast.Revit.Annotation.spot_dimensions import (
    get_spot_type_arrow_head_ids,
    get_all_spot_elevation_symbol_ids_in_model,
    get_all_spot_dim_types,
    get_symbol_ids_from_spot_types,
)
from duHast.Revit.Annotation.stair_path import get_stairs_path_arrow_head_ids
from duHast.Revit.Common.purge_utils import get_used_unused_type_ids


# ------------------ used annotation types  ------------------


def get_used_text_type_ids_in_model(doc):
    """
    Gets all ids of text types used by elements in the model, includes types used in schedules (appearance)!
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    text_type_ids_used = []
    col = get_all_text_annotation_elements(doc)
    for t in col:
        if t.GetTypeId() not in text_type_ids_used:
            text_type_ids_used.append(t.GetTypeId())
    # get all schedules and check their appearance text properties!
    col = FilteredElementCollector(doc).OfClass(ViewSchedule)
    for c in col:
        if c.BodyTextTypeId not in text_type_ids_used:
            text_type_ids_used.append(c.BodyTextTypeId)
        if c.HeaderTextTypeId not in text_type_ids_used:
            text_type_ids_used.append(c.HeaderTextTypeId)
        if c.TitleTextTypeId not in text_type_ids_used:
            text_type_ids_used.append(c.TitleTextTypeId)
    return text_type_ids_used


def get_used_dim_type_ids_in_model(doc):
    """
    Gets all used dimension type Ids in the model.
    Used: at least one instance using this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing Dimension Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    dim_type_ids_used = []
    col = get_all_dimension_elements(doc)
    for v in col:
        if v.GetTypeId() not in dim_type_ids_used:
            dim_type_ids_used.append(v.GetTypeId())
    return dim_type_ids_used


def get_used_dim_styles_from_multi_ref(doc, multi_reference_anno_types):
    """
    Gets all dimension styles used in multi ref annotation types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param multi_reference_anno_types: list in format [[multi refType, [element ids of similar multi ref types, ...]]]
    :type multi_reference_anno_types: List [[Autodesk.Revit.DB.ElementType, [Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]]
    :return: List of element ids representing dimension style
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    dim_type_ids_used = []
    for m_type in multi_reference_anno_types:
        for t in m_type[1]:
            multi_ref_type = doc.GetElement(t)
            if multi_ref_type.DimensionStyleId not in dim_type_ids_used:
                dim_type_ids_used.append(multi_ref_type.DimensionStyleId)
    return dim_type_ids_used


def get_used_multi_ref_dim_type_ids_in_model(doc):
    """
    Gets all ids of multi reference types used by elements in the model.
    Used: at least one instance using this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi reference Annotation Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    dim_type_ids_used = []
    col = get_all_multi_ref_annotation_elements(doc)
    for v in col:
        if v.GetTypeId() not in dim_type_ids_used:
            dim_type_ids_used.append(v.GetTypeId())
    return dim_type_ids_used


def get_all_used_arrow_head_type_ids_in_model(doc):
    """
    Returns all used arrow types in the model.
    Used in types of dimension, text, independent tags, spot dims, annotation symbols (incl room and area tags), stairs path
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    used_ids = []
    used_ids = used_ids + get_dim_type_arrow_head_ids(doc)
    used_ids = used_ids + get_text_type_arrow_head_ids(doc)
    used_ids = used_ids + get_independent_tag_type_arrow_head_ids(doc)
    used_ids = used_ids + get_spot_type_arrow_head_ids(doc)
    used_ids = used_ids + get_anno_symbol_arrow_head_ids(doc)
    used_ids = used_ids + get_stairs_path_arrow_head_ids(doc)
    filtered_ids = []
    for u in used_ids:
        if u not in filtered_ids:
            filtered_ids.append(u)
    return filtered_ids


# ------------------ unused annotation types  ------------------


def get_all_unused_text_type_ids_in_model(doc):
    """
    Gets ID of all unused text types in the model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    filtered_unused_text_type_ids = get_unused_type_ids_in_model(
        doc, get_all_text_types, get_used_text_type_ids_in_model
    )
    return filtered_unused_text_type_ids


def get_all_unused_dim_type_ids_in_model(doc):
    """
    Gets ID of all unused dim types in the model.
    Includes checking multi ref dims for used dim types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # get unused dimension type ids
    filtered_unused_dim_type_ids = get_unused_type_ids_in_model(
        doc, get_dim_types, get_used_dim_type_ids_in_model
    )
    # get all multi ref dimension types in model
    multi_reference_anno_types = get_all_similar_multi_reference_anno_types(doc)
    # get all dim styles used in multi refs
    used_dim_styles_in_multi_refs = get_used_dim_styles_from_multi_ref(
        doc, multi_reference_anno_types
    )
    # cross reference filtered list vs multi ref list and only keep items which are just in the filtered list
    unused_dim_type_ids = []
    for f in filtered_unused_dim_type_ids:
        if f not in used_dim_styles_in_multi_refs:
            unused_dim_type_ids.append(f)
    return unused_dim_type_ids


def get_all_unused_multi_ref_dim_type_ids_in_model(doc):
    """
    Gets IDs of all unused multi ref dimension types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi ref dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    return get_unused_type_ids_in_model(
        doc,
        get_all_multi_ref_annotation_types,
        get_used_multi_ref_dim_type_ids_in_model,
    )


def get_all_unused_arrow_type_ids_in_model(doc):
    """
    Gets all unused arrow type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    unused_ids = []
    used_ids = get_all_used_arrow_head_type_ids_in_model(doc)
    available_ids = get_arrow_type_ids_in_model(doc)
    for a_id in available_ids:
        if a_id not in used_ids:
            unused_ids.append(a_id)
    return unused_ids


def get_unused_symbol_ids_from_spot_types(doc):
    """
    Gets all family symbol ids not used as symbol in any spot elevation or spot coordinate type definition.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols not used in spot elevation or spot coordinate type definition.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used = []
    ids_available = get_all_spot_elevation_symbol_ids_in_model(doc)
    dim_ts = get_all_spot_dim_types(doc)
    for t in dim_ts:
        id = get_built_in_parameter_value(t, BuiltInParameter.SPOT_ELEV_SYMBOL)
        if id not in ids_used and id != ElementId.InvalidElementId and id != None:
            ids_used.append(id)

    # get unused ids
    for id in ids_available:
        if id not in ids_used:
            ids.append(id)
    return ids


def get_unused_symbol_ids_from_spot_types_to_purge(doc):
    """
    Gets all unused family and family symbol ids of category BuiltInCategory.OST_SpotElevSymbols.
    This method can be used to safely delete unused families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family and family symbols not used in spot elevation or spot coordinate type definition.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_unused_in_place_ids_for_purge(doc, get_unused_symbol_ids_from_spot_types)
    return ids


def get_used_generic_annotation_type_ids(doc):
    """
    Returns all used generic annotation symbol ids ( used in model as well as dimension types)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    # get ids from symbols used in dim types
    ids_dim_types = get_symbol_ids_from_dim_types(doc)
    # get ids from symbols used in spots
    ids_spots = get_symbol_ids_from_spot_types(doc)
    # get detail types used in model
    ids_used_in_model = get_used_unused_type_ids(
        doc, get_all_generic_annotation_type_ids_by_category, 1
    )
    # build overall list
    for id in ids_used_in_model:
        ids.append(id)
    for id in ids_dim_types:
        if id not in ids:
            ids.append(id)
    for id in ids_spots:
        if id not in ids:
            ids.append(id)
    return ids


def get_unused_generic_annotation_type_ids(doc):
    """
    Returns all unused annotation symbol ids ( unused in model as well as dimension types)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    ids_used = get_used_generic_annotation_type_ids(doc)
    ids_all = get_all_generic_annotation_type_ids_by_category(doc)
    for id in ids_all:
        if id not in ids_used:
            ids.append(id)
    return ids


def get_unused_generic_annotation_ids_for_purge(doc):
    """
    returns symbol(type) ids and family ids (when no type is in use) of in generic anno families which can be purged
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_unused_in_place_ids_for_purge(doc, get_unused_generic_annotation_type_ids)
    return ids
