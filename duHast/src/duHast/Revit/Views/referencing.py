"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view referencing. 
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

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)
import System
from System.Collections.Generic import List

from duHast.Revit.Common import common as com
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Family import family_utils as rFamUPurge
from duHast.Revit.Views import views as rView

# import Autodesk
import Autodesk.Revit.DB as rdb

# ------------------------ deprecated -----------------------
# the following element collectors dont seem to return any types ...

# doc:   current model document
def deprecated__get_all_call_out_types_by_category(doc):
    """this will return an EMPTY filtered element collector of all call out types in the model in Revit 2019"""
    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Callouts)
        .WhereElementIsElementType()
    )
    return collector


# doc:   current model document
def deprecated__get_all_reference_view_types_by_category(doc):
    """this will return an EMPTY filtered element collector of all reference view types in the model in Revit 2019"""
    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_ReferenceViewer)
        .WhereElementIsElementType()
    )
    return collector


# doc:   current model document
def deprecated__get_all_call_out_type_ids_by_category(doc):
    """this will return an EMPTY filtered element collector of all call out type ids in the model"""
    collector = deprecated__get_all_call_out_types_by_category(doc)
    ids = com.get_ids_from_element_collector(collector)
    return ids


# doc:   current model document
def deprecated__get_all_reference_view_type_ids_by_category(doc):
    """this will return an EMPTY filtered element collector of all reference view types in the model"""
    collector = deprecated__get_all_reference_view_types_by_category(doc)
    ids = com.get_ids_from_element_collector(collector)
    return ids


# ---------------------- utility -----------------------


def get_all_call_out_heads_by_category(doc):
    """
    Gets a filtered element collector of all callOut Head symbol (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing call out head symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_CalloutHeads)
        .WhereElementIsElementType()
    )
    return collector


def get_all_elevation_heads_by_category(doc):
    """
    Gets a filtered element collector of all elevation symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing elevation symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_ElevationMarks)
        .WhereElementIsElementType()
    )
    return collector


def get_all_section_heads_by_category(doc):
    """
    Gets a filtered element collector of all section symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing section symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_SectionHeads)
        .WhereElementIsElementType()
    )
    return collector


def get_all_view_continuation_markers_by_category(doc):
    """
    Gets a filtered element collector of all view continuation symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing Continuation Marker symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_ReferenceViewerSymbol
    )
    return collector


def get_all_reference_view_elements_by_category(doc):
    """
    Gets filtered element collector of all reference view elements in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing reference view elements.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_ReferenceViewer
    )
    return collector


# ---------------------- view ref types  -----------------------

#: contains the builtin parameter definitions for Call out type ids, section type ids, elevation type ids
VIEW_REFERENCE_PARAMETER_DEF_NAMES = [
    rdb.BuiltInParameter.ELEVATN_TAG,
    rdb.BuiltInParameter.CALLOUT_TAG,
    rdb.BuiltInParameter.SECTION_TAG,
]

#: contains the builtin parameter definitions for call out symbol tag ids, section symbol tag ids, elevation symbol tag ids
VIEW_TAG_SYMBOL_PARAMETER_DEF = [
    rdb.BuiltInParameter.CALLOUT_ATTR_HEAD_TAG,
    rdb.BuiltInParameter.ELEV_SYMBOL_ID,
    rdb.BuiltInParameter.SECTION_ATTR_HEAD_TAG,
    rdb.BuiltInParameter.SECTION_ATTR_TAIL_TAG,
    rdb.BuiltInParameter.REFERENCE_VIEWER_ATTR_TAG,
]

#: category filter for all view ref categories
VIEW_REF_CATEGORY_FILTER = List[rdb.BuiltInCategory](
    [
        rdb.BuiltInCategory.OST_CalloutHeads,
        rdb.BuiltInCategory.OST_ElevationMarks,
        rdb.BuiltInCategory.OST_SectionHeads,
        rdb.BuiltInCategory.OST_ReferenceViewerSymbol,
    ]
)


def get_reference_type_ids_from_view_type(view_type):
    """
    Gets all reference type ids used in view type.

    :param view_type: The view type.
    :type view_type: Autodesk.Revit.DB.ViewType

    :return: dictionary, key: BuiltinParameterDefinition, value: id of a tag
    :rtype: dic{Autodesk.Revit.DB.BuiltinParameterDefinition:[Autodesk.Revit.DB.ElementId]}
    """

    dic = {}
    for p_def in VIEW_REFERENCE_PARAMETER_DEF_NAMES:
        p_value = rParaGet.get_built_in_parameter_value(view_type, p_def)
        if p_value != None:
            # there should only ever be one value per key!
            if dic.has_key(p_def):
                dic[p_def].append(p_value)
            else:
                dic[p_def] = [p_value]
    return dic


def get_used_view_reference_type_id_data(doc):
    """
    Gets all view references types in use in the model in a dictionary.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: key is the reference tag type: call out, section or elevation, values are the type ids in use
    :rtype: dictionary {reference tag type: list Autodesk.Revit.DB.ElementIds}
    """

    dic = {}
    col = rView.get_view_types(doc)
    for c in col:
        # get reference types from view types
        reference_type_by_view_type = get_reference_type_ids_from_view_type(c)
        # check if already in dictionary , if not append
        for key, value in reference_type_by_view_type.items():
            if dic.has_key(key):
                for v in value:
                    if v not in dic[key]:
                        dic[key].append(v)
            else:
                dic[key] = value
    return dic


def get_all_view_reference_type_id_data(doc):
    """
    Gets all view references types available in the model in a dictionary.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: key is the reference type: call out, section or elevation, values are the type ids in use
    :rtype: dictionary {reference tag type: list Autodesk.Revit.DB.ElementIds}
    """

    dic = {}
    col = rView.get_view_types(doc)
    for c in col:
        # get reference types from view types
        reference_type_by_view_type = get_reference_type_ids_from_view_type(c)
        # get all similar types
        for key, value in reference_type_by_view_type.items():
            for v in reference_type_by_view_type[key]:
                type = doc.GetElement(v)
                if type != None:
                    all_sim_type_ids = type.GetSimilarTypes()
                    for sim_type_id in all_sim_type_ids:
                        if dic.has_key(key):
                            if sim_type_id not in dic[key]:
                                dic[key].append(sim_type_id)
                        else:
                            dic[key] = [sim_type_id]
    return dic


def get_all_view_reference_type_id_data_as_list(doc):
    """
    Gets all view references type ids available in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing view reference types
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    dic = get_all_view_reference_type_id_data(doc)
    ids = []
    for key, value in dic.items():
        if len(dic[key]) > 0:
            ids = ids + dic[key]
    return ids


def get_all_view_continuation_type_ids(doc):
    """
    Gets all view continuation type ids available in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of view continuation type ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = []
    syms = get_all_reference_view_elements_by_category(doc)
    for sym in syms:
        sim_type_ids = sym.GetValidTypes()
        for sim_type in sim_type_ids:
            if sim_type not in ids:
                ids.append(sim_type)
    return ids


def get_used_view_continuation_type_ids(doc):
    """returns all view continuation types available in the model"""

    ids = []
    syms = get_all_reference_view_elements_by_category(doc)
    for sym in syms:
        if sym.GetTypeId() not in ids:
            ids.append(sym.GetTypeId())
    return ids


def get_all_view_reference_symbol_ids(doc):
    """
    Gets the ids of all view reference family symbols(types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of view reference family symbols(types) ids.
    :rtype:  list Autodesk.Revit.DB.ElementIds
    """

    ids = []
    multi_cat_filter = rdb.ElementMulticategoryFilter(VIEW_REF_CATEGORY_FILTER)
    collector = (
        rdb.FilteredElementCollector(doc)
        .WherePasses(multi_cat_filter)
        .WhereElementIsElementType()
    )
    ids = com.get_ids_from_element_collector(collector)
    return ids


# ---------------------- view refs and continuation symbols -----------------------


def get_symbol_ids_from_type_ids(doc, view_ref_types_ids):
    """
    'Gets the ids of all view family symbols(types) from given view ref types or continuation types the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_ref_types_ids: list of ids representing view reference types or continuation types
    :type view_ref_types_ids: list Autodesk.Revit.DB.ElementId

    :return: List of ids of all view family symbols(types).
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    for vrt_id in view_ref_types_ids:
        el = doc.GetElement(vrt_id)
        for p_def in VIEW_TAG_SYMBOL_PARAMETER_DEF:
            p_value = rParaGet.get_built_in_parameter_value(el, p_def)
            if p_value != None and p_value not in ids:
                ids.append(p_value)
    return ids


def get_used_view_reference_and_continuation_marker_symbol_ids(doc):
    """
    Get the ids of all view reference symbols(types) and view continuations symbols (types) used by
    view reference types and view continuation types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids of all view family symbols(types).
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    view_cont_types = get_all_view_continuation_type_ids(doc)
    view_ref_types = get_all_view_reference_type_id_data(doc)
    # get ids of symbols used in view ref types
    ids_cont = get_symbol_ids_from_type_ids(doc, view_cont_types)
    ids_view_refs = []
    for key, value in view_ref_types.items():
        ids_view_refs = ids_view_refs + get_symbol_ids_from_type_ids(
            doc, view_ref_types[key]
        )
    # build unique dictionary
    for id_c in ids_cont:
        ids.append(id_c)
    for id_v in ids_view_refs:
        if id_v not in ids:
            ids.append(id_v)
    return ids


def get_nested_family_marker_names(doc, used_ids):
    """
    Gets nested family names from provided symbols.

    - Retrieves a families from the symbols provided.
    - Opens the family document and extracts the names off all nested families within.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param used_ids: List of symbol ids.
    :type used_ids: list of Autodesk.Revit.DB.ElementId

    :return: List of all unique nested family names.
    :rtype: list str
    """

    names = []
    for used_symbol_id in used_ids:
        if used_symbol_id != rdb.ElementId.InvalidElementId:
            # get the family
            el_symbol = doc.GetElement(used_symbol_id)
            fam = el_symbol.Family
            # open family
            try:
                fam_doc = doc.EditFamily(fam)
                nested_fam_col = rFamUPurge.get_all_loadable_families(fam_doc)
                for n_fam in nested_fam_col:
                    if n_fam.Name not in names and n_fam.Name != "":
                        names.append(n_fam.Name)
                fam_doc.Close(False)
            except Exception as e:
                print(e)
    # print (names)
    return names
