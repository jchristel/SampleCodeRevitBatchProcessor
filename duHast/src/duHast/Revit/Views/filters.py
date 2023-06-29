"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view filters. 
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

from duHast.Revit.Views.templates import get_template_ids_which_can_have_filters
from duHast.Revit.Common import common as com


VIEW_TYPE_WHICH_CAN_HAVE_FILTERS = [
    rdb.ViewType.FloorPlan,
    rdb.ViewType.CeilingPlan,
    rdb.ViewType.Elevation,
    rdb.ViewType.ThreeD,
    rdb.ViewType.EngineeringPlan,
    rdb.ViewType.AreaPlan,
    rdb.ViewType.Section,
    rdb.ViewType.Detail,
    rdb.ViewType.Walkthrough,
    rdb.ViewType.DraftingView,
    rdb.ViewType.Legend,
]


def get_all_filters(doc):
    """
    Gets all filters in document as a collector

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered Element collector containing Autodesk.Revit.DB.ParameterFilterElement
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ParameterFilterElement)
    return collector


def get_all_filter_ids(doc):
    """
    Gets all view filter ids in document

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view filter Id's which are in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = get_all_filters(doc)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_filter_ids_from_view_by_filter(view, unique_list):
    """
    Returns past in list of filter id's plus new unique filter id's from view (if not already in list past in)

    :param view: The view of which to get the filters from.
    :type view: Autodesk.Revit.DB.View
    :param unique_list: List containing view filters
    :type unique_list: list of Autodesk.Revit.DB.ElementId
    :return: List containing past in view filters and new view filters.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    filters = view.GetFilters()
    if len(filters) != 0:
        for j in filters:
            if j not in unique_list:
                unique_list.append(j)
    return unique_list


def get_filters_from_templates(doc):
    """
    Gets all filter id's used in view templates only.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List containing filter Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    filters_in_use = []
    # get view filters used in templates only
    # include templates which do not enforce filters but still may have some set
    template_with_filters = get_template_ids_which_can_have_filters(
        doc, VIEW_TYPE_WHICH_CAN_HAVE_FILTERS
    )
    for temp in template_with_filters:
        # get filters and check whether already in list
        filters_in_use = get_filter_ids_from_view_by_filter(temp, filters_in_use)
    return filters_in_use


def get_filter_ids_from_views_without_template(doc, filter_by_type):
    """
    Gets all filter id's from views which dont have a template applied and match a given view type.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter_by_type: list of view types of which the filters are to be returned.
    :type filter_by_type: list of Autodesk.Revit.DB.ViewType
    :return: List containing filter Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    filters_in_use = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # cant filter out templates or templates which do not control filters to be more precise
        # views The parameter:
        # BuiltInParameter.VIS_GRAPHICS_FILTERS
        # which is attached to views is of storage type None...not much use...
        if v.IsTemplate == False:
            for filter in filter_by_type:
                if v.ViewType == filter:
                    get_filter_ids_from_view_by_filter(v, filters_in_use)
                    break
    return filters_in_use


def get_all_unused_view_filters(doc):
    """
    Gets id's of all unused view filters in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List containing filter Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    un_used_view_filter_ids = []
    all_available_filters = get_all_filters(doc)
    all_filter_ids_by_template = get_filters_from_templates(doc)
    all_filter_ids_by_view = get_filter_ids_from_views_without_template(
        doc, VIEW_TYPE_WHICH_CAN_HAVE_FILTERS
    )
    # combine list of used filters into one
    all_used_view_filters = all_filter_ids_by_template + all_filter_ids_by_view
    # loop over all available filters and check for match in used filters
    for available_f in all_available_filters:
        if available_f.Id not in all_used_view_filters:
            un_used_view_filter_ids.append(available_f.Id)
    return un_used_view_filter_ids
