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