"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit detail items. 
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


from duHast.Revit.Family import purge_unused_family_types as rFamPurge
from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Revit.DetailItems import detail_items as rDetail
from duHast.Revit.DetailItems.Utility import (
    detail_items_type_sorting as rDetailTypeSort,
)

# -------------------------------- repeating detail types -------------------------------------------------------


def get_used_repeating_detail_type_ids(doc):
    """
    Gets all used repeating detail type ids in the model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rDetail.get_all_repeating_detail_type_ids_available, 1, 1
    )
    return ids


def get_unused_repeating_detail_type_ids(doc):
    """
    Gets all unused repeating detail type ids in the model.
    Unused: not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rDetail.get_all_repeating_detail_type_ids_available, 0, 1
    )
    return ids


def get_unused_repeating_detail_type_ids_for_purge(doc):
    """
    Gets type ids off all unused repeating detail types in model.
    This method can be used to safely delete unused repeating detail types. In the case that no basic\
        wall instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one repeating detail type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all repeating detail types not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rDetail.get_all_repeating_detail_type_ids_available, 0, 1
    )
    all_ids = rDetail.get_all_repeating_detail_type_ids_available(doc)
    # need to keep at least one
    if len(all_ids) == len(ids):
        ids.pop(0)
    return ids


# -------------------------------- Detail families -------------------------------------------------------


def get_all_used_detail_symbol_ids(doc):
    """
    Gets all used detail symbol type ids in model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of family symbol (type) ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = []
    dic = rDetailTypeSort.build_detail_type_ids_dictionary(
        rDetail.get_all_detail_types_by_category(doc)
    )
    if dic.has_key(rDetail.ELEMENT_TYPE):
        ids_unfiltered = dic[rDetail.FAMILY_SYMBOL]
        # check if used in repeating details
        ids_repeat_det = rDetail.get_all_repeating_detail_type_ids_available(doc)
        # print('ids used in repeating details ' + str(len(idsRepeatDet)))
        # get detail types used in repeating details only
        ids_of_details_used_repeat_details = (
            rDetail.get_detail_symbols_used_in_repeating_details(doc, ids_repeat_det)
        )
        # get detail types used in model
        ids_used_in_model = rPurgeUtils.get_used_unused_type_ids(
            doc, rDetail.get_all_detail_symbol_ids_available, 1
        )
        print("ids used in model: {} ".format(len(ids_used_in_model)))
        # built overall ids list
        for id in ids_of_details_used_repeat_details:
            if id not in ids:
                ids.append(id)
        for id in ids_used_in_model:
            if id not in ids:
                ids.append(id)
        return ids
    else:
        return []


def get_all_unused_detail_symbol_ids(doc):
    """
    Gets all unused detail symbol type ids in model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of family symbol (type) ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = []
    all_available_ids = rDetail.get_all_detail_symbol_ids_available(doc)
    all_used_ids = get_all_used_detail_symbol_ids(doc)
    for id in all_available_ids:
        if id not in all_used_ids:
            ids.append(id)
    return ids


def get_all_unused_detail_symbol_ids_for_purge(doc):
    """
    Gets type ids off all unused detail symbols (types) in model.
    This method can be used to safely delete all unused detail symbols (types) and families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all unused detail symbols and families not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_all_unused_detail_symbol_ids
    )
    return ids


def get_used_filled_region_type_ids(doc):
    """
    Gets all used filled region type ids in model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of filled region type ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = []
    ids_all = rDetail.get_all_filled_region_type_ids_available(doc)
    for id in ids_all:
        el = doc.GetElement(id)
        dic = rDetailTypeSort.build_dependent_elements_dictionary(
            doc, el.GetDependentElements(None)
        )
        if dic.has_key("Autodesk.Revit.DB.FilledRegion"):
            ids.append(id)
    return ids


def get_unused_filled_region_type_ids(doc):
    """'
    Gets all unused filled region type ids in model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of filled region type ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    ids = []
    ids_all = rDetail.get_all_filled_region_type_ids_available(doc)
    for id in ids_all:
        el = doc.GetElement(id)
        dic = rDetailTypeSort.build_dependent_elements_dictionary(
            doc, el.GetDependentElements(None)
        )
        if dic.has_key("Autodesk.Revit.DB.FilledRegion") == False:
            ids.append(id)
    return ids


def get_unused_filled_region_type_ids_for_purge(doc):
    """
    Gets ids off all unused filled region types in model.
    This method can be used to safely delete all unused filled region types in model. In the case that no filled\
        region instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one filled region type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all unused filled region types not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_unused_filled_region_type_ids(doc)
    ids_all = rDetail.get_all_filled_region_type_ids_available(doc)
    # need to keep at least one
    if len(ids_all) == len(ids):
        ids.pop(0)
    return ids
