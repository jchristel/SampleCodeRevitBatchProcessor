"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to deleting Revit views. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import delete as rDel, parameter_get_utils as rParaGet
from duHast.Utilities.Objects import result as res
from duHast.Utilities import utility as util
from duHast.Revit.Views.views import get_views_not_on_sheet


def delete_views(doc, view_rules, collector_views):
    """
    Deletes views based on view rules supplied.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_rules: Rules used to check whether a view should be deleted. Rules are based on parameters attached to view and their values.
    :type view_rules: array in format [[parameter name, condition test method, value to test against]]
    :param collector_views: A filtered element collector containing views.
    :type collector_views: Autodesk.Revit.DB.FilteredElementCollector
    :return:
        Result class instance.
        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    """

    ids = []
    view_counter = 0
    for v in collector_views:
        # filter out revision schedules '<', sheets and other view types which can not be deleted
        if (
            util.encode_ascii(v.Name)[0] != "<"
            and v.ViewType != rdb.ViewType.Internal
            and v.ViewType != rdb.ViewType.Undefined
            and v.ViewType != rdb.ViewType.ProjectBrowser
            and v.ViewType != rdb.ViewType.DrawingSheet
            and v.ViewType != rdb.ViewType.SystemBrowser
        ):
            view_counter = +1
            paras = v.GetOrderedParameters()
            rule_match = True
            for para_name, paraCondition, conditionValue in view_rules:
                for p in paras:
                    if p.Definition.Name == para_name:
                        rule_match = rule_match and rParaGet.check_parameter_value(
                            p, paraCondition, conditionValue
                        )
            if rule_match == True:
                # delete view
                ids.append(v.Id)
    # make sure we are not trying to delete all views (this allowed when a model is opened into memory only, but that model will crash when trying to open into UI)
    if len(ids) == view_counter and len(ids) > 0:
        ids.pop()
    # delete all views at once
    result = rDel.delete_by_element_ids(
        doc, ids, "deleting views not matching filters", "views"
    )
    return result


def delete_views_not_on_sheets(doc, filter):
    """
    Deletes all views not placed on sheets includes schedules and legends matching filter.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter: Function checking whether view should be deleted.
    :type filter: func(view) returns a bool
    :return:
        Result class instance.
        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    """

    ids = []
    return_value = res.Result()
    views_not_on_sheets = get_views_not_on_sheet(doc)
    for view_not_on_sheet in views_not_on_sheets:
        if filter(view_not_on_sheet):
            ids.append(view_not_on_sheet.Id)
    # check we are not trying to delete all views
    if len(views_not_on_sheets) == len(ids) and len(views_not_on_sheets) > 0:
        # remove a random view from this list
        ids.pop(0)
    if len(ids) > 0:
        return_value = rDel.delete_by_element_ids(
            doc,
            ids,
            "deleting " + str(len(views_not_on_sheets)) + " views not on sheets",
            "views",
        )
    else:
        return_value.update_sep(True, "No views not placed on sheets found.")
    return return_value


def delete_unused_elevation_view_markers(doc):
    """
    Deletes all unused elevation markers. (no Elevation is created by the marker)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return:
        Result class instance.
        - .result = True if all unused elevation markers where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    ele = rdb.FilteredElementCollector(doc).OfClass(rdb.ElevationMarker)
    # items to be deleted
    ids = []
    # set up view counter (how many views will be deleted)
    counter = 0
    # loop over markers
    for e in ele:
        # check if view count is 0 (unused marker)
        if e.CurrentViewCount == 0:
            # add to list of views to be deleted
            ids.append(e.Id)
            counter += 1
    if len(ids) > 0:
        return_value = rDel.delete_by_element_ids(
            doc, ids, "deleting unused view markers: " + str(counter), "view marker"
        )
    else:
        return_value.update_sep(True, "No unused elevation markers in model")
    return return_value


def delete_sheets(doc, view_rules, collector_views):
    """
    Deletes sheets based on rules.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_rules: A set of rules. If view matches rule it will be deleted.
    :type view_rules: array in format [parameter name, condition test method, value to test against
    :param collector_views: A filtered element collector containing view instances.
    :type collector_views: Autodesk.Revit.DB.FilteredElementCollector
    :return:
        Result class instance.
        - .result = True if all sheets matching filter where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    """

    ids = []
    for v in collector_views:
        if v.ViewType == rdb.ViewType.DrawingSheet:
            paras = v.GetOrderedParameters()
            rule_match = True
            for para_name, paraCondition, conditionValue in view_rules:
                for p in paras:
                    if p.Definition.Name == para_name:
                        rule_match = rule_match and rParaGet.check_parameter_value(
                            p, paraCondition, conditionValue
                        )
            if rule_match == True:
                # delete view
                ids.append(v.Id)
    result = rDel.delete_by_element_ids(doc, ids, "deleting sheets", "sheets")
    return result


def delete_all_sheets(doc):
    """
    Deletes all sheets in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return:
        Result class instance.
        - .result = True if all sheets where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    ids = []
    collector_sheets = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in collector_sheets:
        if v.ViewType == rdb.ViewType.DrawingSheet:
            ids.append(v.Id)
    if len(ids) > 0:
        return_value = rDel.delete_by_element_ids(
            doc, ids, "deleting all sheets", "sheets"
        )
    else:
        return_value.update_sep(True, "No sheets in the model")
    return return_value
