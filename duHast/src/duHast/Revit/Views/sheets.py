"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view sheets. 
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

import clr

import Autodesk.Revit.DB as rdb
from duHast.Utilities import utility as util

from duHast.Revit.Common import parameter_get_utils as rParaGet

# required in lambda expressions!
clr.AddReference("System.Core")
import System
clr.ImportExtensions(System.Linq)


def get_sheets_by_filters(doc, view_rules=None):
    """
    Gets sheets matching filters provided
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_rules: A set of rules. If sheet matches rule it will be returned. Defaults to None which will return all sheets.
    :type view_rules: array in format [parameter name, condition test method, value to test against], optional
    :return: Views matching filter
    :rtype: list of Autodesk.Revit.DB.View
    """

    collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    views = []
    for v in collector_views:
        # if no filter rules applied return al sheets
        if view_rules is not None:
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
                views.append(v)
        else:
            views.append(v)
    return views


def get_all_sheets(doc):
    """
    Gets all sheets in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of sheet views
    :rtype: list of Autodesk.Revit.DB.View
    """

    collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    return collector_views


def get_sheet_rev_by_sheet_number(doc, sheet_number):  # type # type: str

    """
    Returns the revision of a sheet identified by its number. Default value is '-'.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet_number # type: The number of the sheet of which the revision is to be returned.
    :type sheet_number # type: str
    :raise: Any exception will need to be managed by the function caller.
    :return:
        The sheets current revision value.
        If no matching sheet is found, '-' is returned.
    :rtype: str
    """

    rev_value = "-"
    collector = (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.ViewSheet)
        .Where(lambda e: e.SheetNumber == sheet_number)
    )  # type
    results = collector.ToList()
    if len(results) > 0:
        sheet = results[0]
        rev_p = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        rev_value = rev_p.AsString()
    return rev_value


def get_sheet_rev_by_sheet_name(doc, sheet_name):  # type # type: str

    """
    Returns the revision of a sheet identified by its name. Default value is '-'.
    Since multiple sheets can have the same name it will return the revision of the first sheet matching the name.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet_name # type: The name of the sheet of which the revision is to be returned.
    :type sheet_name # type: str
    :raise: Any exception will need to be managed by the function caller.
    :return:
        The sheets current revision value.
        If no matching sheet is found, '-' is returned.
    :rtype: str
    """

    rev_value = "-"
    collector = (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.ViewSheet)
        .Where(lambda e: e.Name == sheet_name)
    )  # type
    results = collector.ToList()
    if len(results) > 0:
        sheet = results[0]
        rev_p = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        rev_value = util.pad_single_digit_numeric_string(rev_p.AsString())
    return rev_value
