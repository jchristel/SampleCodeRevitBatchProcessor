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


def GetSheetsByFilters(doc, viewRules = None):
    '''
    Gets sheets matching filters provided
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewRules: A set of rules. If sheet matches rule it will be returned. Defaults to None which will return all sheets.
    :type viewRules: array in format [parameter name, condition test method, value to test against], optional
    :return: Views matching filter
    :rtype: list of Autodesk.Revit.DB.View
    '''

    collectorViews = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    views = []
    for v in collectorViews:
        # if no filter rules applied return al sheets
        if(viewRules is not None):
            paras = v.GetOrderedParameters()
            ruleMatch = True
            for paraName, paraCondition, conditionValue in viewRules:
                for p in paras:
                    if(p.Definition.Name == paraName):
                        ruleMatch = ruleMatch and rParaGet.check_parameter_value(p, paraCondition, conditionValue)
            if (ruleMatch == True):
                # delete view
                views.append(v)
        else:
            views.append(v)
    return views


def GetSheetsInModel(doc):
    '''
    Gets all sheets in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of sheet views
    :rtype: list of Autodesk.Revit.DB.View
    '''

    return _get_view_types(doc, rdb.ViewType.DrawingSheet)

def GetSheetRevByNumber(
    doc,
    sheetNumber # type: str
    ):

    '''
    Returns the revision of a sheet identified by its number. Default value is '-'.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheetNumber: The number of the sheet of which the revision is to be returned.
    :type sheetNumber: str
    :raise: Any exception will need to be managed by the function caller.
    :return:
        The sheets current revision value.  
        If no matching sheet is found, '-' is returned.
    :rtype: str
    '''

    revValue = '-'
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet).Where(lambda e: e.SheetNumber == sheetNumber)
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        revP = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        revValue = revP.AsString()
    return revValue


def GetSheetRevByName(
    doc,
    sheetName # type: str
    ):

    '''
    Returns the revision of a sheet identified by its name. Default value is '-'.
    Since multiple sheets can have the same name it will return the revision of the first sheet matching the name.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document 
    :param sheetName: The name of the sheet of which the revision is to be returned.
    :type sheetName: str
    :raise: Any exception will need to be managed by the function caller.
    :return:
        The sheets current revision value.  
        If no matching sheet is found, '-' is returned.
    :rtype: str
    '''

    revValue = '-'
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet).Where(lambda e: e.Name == sheetName)
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        revP = sheet.get_Parameter(rdb.BuiltInParameter.SHEET_CURRENT_REVISION)
        revValue = util.PadSingleDigitNumericString(revP.AsString())
    return revValue