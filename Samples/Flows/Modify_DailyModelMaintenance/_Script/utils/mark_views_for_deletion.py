"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing view maintenance functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- mark any view which just ends on 'Copy x' as to be deleted (assume its a quick and dirty throw away view)

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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


# debug mode revit project file name
debugRevitFileName_ = r"C:\Users\jchristel\Documents\Temp\Debug.rvt"

import sys, os


debug = True
if debug:
    SCRIPT_DIRECTORY = r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\Flows\Modify_DailyModelMaintenance\_Script"
    sys.path += [SCRIPT_DIRECTORY]

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import Autodesk.Revit.DB as rdb


from duHast.Revit.Views import views as rViews
from duHast.Utilities.Objects import result as res
from duHast.Utilities import date_stamps as ds
from duHast.Revit.Common import transaction as rTran, parameter_get_utils as rParaGet

# the string to find in a view name indicating it needs to be marked for deletion
COPY_STRING = " copy "
#: prefix to be applied to a view marked for deletion
TO_BE_DELETED_MARKER = "DELETE_"
#: characters not allowed in a view name (standard user 3D view has them...)
ILLEGAL_CHARACTERS = [
    "{",
    "}",
]


def _view_filter(view):
    """
    generic view filter allowing all views to be selected

    :param view: not used!
    :type view: Autodesk.Revit.DB.View

    :return: returns always True
    :rtype: bool
    """
    return True


def _get_copy_index(view_name):
    """
    Returns th index of the word COPY_STRING in a view name

    :param view_name: The view name.
    :type view_name: str
    :return: index greater or equal to 0 if string is present in name, Otherwise -1
    :rtype: int
    """

    if COPY_STRING in view_name:
        return view_name.rfind(COPY_STRING)
    else:
        return -1


def _get_view_filters_for_file(doc):
    """
    Returns the view filters assigned to a given Revit project file name.

    Note: some files may be excluded from auto marking...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of view filters.
    :rtype: []
    """

    # get view filter rules for this file
    for fileName, viewRules in settings.VIEW_KEEP_RULES:
        if doc.Title.startswith(fileName):
            return viewRules
    return []


def _filter_view_rules(view, view_rules):
    """
    Applies view filter rules to a view.

    :param view: The view.
    :type view: Autodesk.Revit.DB.View
    :param view_rules: List of filter rules.
    :type view_rules: []

    :return: True if view can be included in renames, otherwise False
    :rtype: bool
    """

    paras = view.GetOrderedParameters()
    rule_match = True
    for para_name, paraCondition, conditionValue in view_rules:
        for p in paras:
            if p.Definition.Name == para_name:
                rule_match = rule_match and rParaGet.check_parameter_value(
                    p, paraCondition, conditionValue
                )
    if rule_match == True:
        return True
    else:
        return False


def _strip_illegal_char(view_name):
    for illegal_char in ILLEGAL_CHARACTERS:
        if illegal_char in view_name:
            view_name = view_name.replace(illegal_char, "_")
    return view_name


def get_views_with_copy_in_name(doc):
    """
    Gets the number of views in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of views in model. On exception it will return -1
    :rtype: int
    """

    designated_copy_views = []
    all_views = rViews.get_views_in_model(doc, _view_filter)
    view_filter_rules = _get_view_filters_for_file(doc)

    for v in all_views:
        v_name = rdb.Element.Name.GetValue(v)
        # check filter
        if _filter_view_rules(v, view_filter_rules):
            v_name = rdb.Element.Name.GetValue(v)
            v_name_lower = v_name.lower()
            # filter views containing copy
            copy_index = _get_copy_index(v_name_lower)
            if copy_index > 0:
                # check whether string after copy is a number and nothing else
                view_name_end = v_name[copy_index + len(COPY_STRING) :]
                try:
                    copy_int = int(view_name_end)
                    print("Added view: {}".format(v_name))
                    designated_copy_views.append(v)
                except:
                    print(
                        "Ignoring view: {} String sequence after copy is not a number: {}".format(
                            v_name, view_name_end
                        )
                    )
        else:
            print("Excluded by filter view: {} ".format(v_name))
    return designated_copy_views


def filter_marked_already(doc, views):
    """
    Checks whether views are already marked.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param views: List of views to be checked.
    :type views: [Autodesk.Revit.DB.View]

    :return: List of views which past filters.
    :rtype: [Autodesk.Revit.DB.View]
    """

    views_filtered = []
    for v in views:
        v_name = rdb.Element.Name.GetValue(v)
        if v_name.lower().startswith(TO_BE_DELETED_MARKER.lower()) == False:
            views_filtered.append(v)
        else:
            print("View {} already marked for deletion".format(v_name))
    return views_filtered


def _mark_views(doc, views):
    """
    Will prefix all views past in which end on 'Copy x' with the word 'DELETE_' and a time stamp

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param views: List of views
    :type views: [Autodesk.Revit.DB.View]

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result A list of views which got renamed.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for v in views:
        v_name = rdb.Element.Name.GetValue(v)
        time_stamp = ds.get_file_date_stamp(ds.FILE_DATE_STAMP_YYYY_MM_DD)

        def action():
            action_return_value = res.Result()
            try:
                # strip illegal characters from the name i.e. { or }
                new_v_name = (
                    TO_BE_DELETED_MARKER
                    + time_stamp
                    + " "
                    + _strip_illegal_char(v_name)
                )
                v.Name = new_v_name
                action_return_value.update_sep(
                    False, "Renamed view: {} to: {}".format(v_name, new_v_name)
                )
                action_return_value.result.append(v)
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to rename view: {} with exception: {}".format(v_name, e),
                )
            return action_return_value

        transaction = rdb.Transaction(doc, "Renaming view: {}".format(v_name))
        tran_result = rTran.in_transaction(transaction, action)
        # for reporting
        return_value.update(tran_result)
    return return_value


def mark_views_for_deletion(doc, revit_file_path, output):
    """
    Will prefix all views which end on 'Copy x' with the word 'DELETE_' and a time stamp

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified file path of the revit file. (not used)
    :type revit_file_path: str
    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result A list of views which got renamed.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Marking views for deletion...start")
    views_copy_in_name = get_views_with_copy_in_name(doc)
    if(len(views_copy_in_name) > 0):
        views_to_mark = filter_marked_already(doc, views_copy_in_name)
        if(len(views_to_mark) > 0):
            result_rename = _mark_views(doc, views_to_mark)
            return_value.update(result_rename)
        else:
            return_value.append_message("All views with 'copy' in name are already marked.")
    else:
        return_value.append_message("No views with 'copy' in name where found.")
    return return_value
