'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view sheets. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
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

import Autodesk.Revit.DB as rdb
from duHast.Utilities import Utility as util

from duHast.APISamples.Views.Utility.ViewTypes import _get_view_types
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet


def get_sheets_by_filters(doc, view_rules = None):
    '''
    Gets sheets matching filters provided
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_rules: A set of rules. If sheet matches rule it will be returned. Defaults to None which will return all sheets.
    :type view_rules: array in format [parameter name, condition test method, value to test against], optional
    :return: Views matching filter
    :rtype: list of Autodesk.Revit.DB.View
    '''

    collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    views = []
    for v in collector_views:
        # if no filter rules applied return al sheets
        if(view_rules is not None):
            paras = v.GetOrderedParameters()
            rule_match = True
            for para_name, paraCondition, conditionValue in view_rules:
                for p in paras:
                    if(p.Definition.Name == para_name):
                        rule_match = rule_match and rParaGet.check_parameter_value(p, paraCondition, conditionValue)
            if (rule_match == True):
                # delete view
                views.append(v)
        else:
            views.append(v)
    return views


def get_all_sheets(doc):
    '''
    Gets all sheets in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of sheet views
    :rtype: list of Autodesk.Revit.DB.View
    '''

    return _get_view_types(doc, rdb.ViewType.DrawingSheet)

def get_sheet_rev_by_sheet_number(
    doc,
    sheet_number # type # type: str
    ):

    '''
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
    '''

    rev_value = '-'
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet).Where(lambda e: e.SheetNumber == sheet_number) # type
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        rev_p = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        rev_value = rev_p.AsString()
    return rev_value


def get_sheet_rev_by_sheet_name(
    doc,
    sheet_name # type # type: str
    ):

    '''
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
    '''

    rev_value = '-'
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet).Where(lambda e: e.Name == sheet_name) # type
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        rev_p = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        rev_value = util.pad_single_digit_numeric_string(rev_p.AsString())
    return rev_value