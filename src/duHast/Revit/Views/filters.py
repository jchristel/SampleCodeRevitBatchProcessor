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
    Element,
    FilteredElementCollector,
    ParameterFilterElement,
    Transaction,
    View,
    ViewType,
)

from duHast.Revit.Views.templates import get_template_ids_which_can_have_filters
from duHast.Revit.Common import common as com
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction


VIEW_TYPE_WHICH_CAN_HAVE_FILTERS = [
    ViewType.FloorPlan,
    ViewType.CeilingPlan,
    ViewType.Elevation,
    ViewType.ThreeD,
    ViewType.EngineeringPlan,
    ViewType.AreaPlan,
    ViewType.Section,
    ViewType.Detail,
    ViewType.Walkthrough,
    ViewType.DraftingView,
    ViewType.Legend,
]


def get_all_filters(doc):
    """
    Gets all filters in document as a collector

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered Element collector containing Autodesk.Revit.DB.ParameterFilterElement
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """
    collector = FilteredElementCollector(doc).OfClass(ParameterFilterElement)
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


def get_filter_by_name(doc, filter_name):
    """
    Retrieves a filter by its name from the current Revit model document.

    Args:
        doc (Revit Document): The current Revit model document.
        filter_name (str): The name of the filter to be retrieved.

    Returns:
        Filter: The filter with the specified name, if found.
        None: If no filter with the specified name is found.
    """
    filters = get_all_filters(doc=doc)
    for filter in filters:
        if Element.Name.GetValue(filter) == filter_name:
            return filter
    return None


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


def is_filter_applied_to_view(view, filter):
    """
    Checks if a filter is already applied to a view in Autodesk Revit.

    Args:
        view (Autodesk.Revit.DB.View): The view object to check if the filter is applied.
        filter (Autodesk.Revit.DB.Filter): The filter object to check if it is applied to the view.

    Returns:
        bool: True if the filter is applied to the view, False otherwise.
    """
    filter_is_applied = False
    filters_applied_to_view_as_ids = view.GetFilters()
    if filter.Id in filters_applied_to_view_as_ids:
        filter_is_applied = True
    return filter_is_applied


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
    col = FilteredElementCollector(doc).OfClass(View)
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


def apply_filter_to_view(doc, view, filter):
    """
    Applies a filter to a view in Autodesk Revit.

    Args:
        doc (Autodesk.Revit.DB.Document): The document object representing the Revit model.
        view (Autodesk.Revit.DB.View): The view object to which the filter should be applied.
        filter (Autodesk.Revit.DB.Filter): The filter object that should be applied to the view.

    Returns:
        duHast.Utilities.Objects.result.Result: The result object containing the outcome of applying the filter to the view. The `result` attribute of the result object indicates whether the filter was applied successfully or not. The `messages` attribute of the result object contains any additional messages related to the application of the filter.
    """

    return_value = res.Result()

    if not is_filter_applied_to_view(view=view, filter=filter):
        # need to add filter
        return_value.append_message(
            "Filter: {} needs to be applied to view: {}".format(filter.Name, view.Name)
        )

        def action():
            action_return_value = res.Result()
            try:
                view.AddFilter(filter.Id)
                return_value.append_message(
                    "Filter: {} added to view: {} successfully.".format(
                        filter.Name, view.Name
                    )
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to apply filter: {} to view: {} with exception: {}".format(
                        filter.Name,
                        view.Name,
                        e,
                    ),
                )
            return action_return_value

        transaction = Transaction(
            doc,
            "Adding filter: {} to view: {}".format(
                filter.Name,
                view.Name,
            ),
        )
        add_filter_status = in_transaction(transaction, action)
        return_value.update(add_filter_status)
    else:
        return_value.append_message(
            "Filter: {} already applied to view: {}".format(filter.Name, view.Name)
        )

    return return_value
