'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to deleting Revit views. 
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

from duHast.APISamples.Common import RevitDeleteElements as rDel, RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res, Utility as util
from duHast.APISamples.Views.RevitViews import get_views_not_on_sheet

def delete_views(doc, viewRules, collectorViews):
    '''
    Deletes views based on view rules supplied.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewRules: Rules used to check whether a view should be deleted. Rules are based on parameters attached to view and their values.
    :type viewRules: array in format [[parameter name, condition test method, value to test against]]
    :param collectorViews: A filtered element collector containing views.
    :type collectorViews: Autodesk.Revit.DB.FilteredElementCollector
    :return: 
        Result class instance.
        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    '''

    ids = []
    viewCounter = 0
    for v in collectorViews:
        # filter out revision schedules '<', sheets and other view types which can not be deleted
        if(util.EncodeAscii(v.Name)[0] != '<' and
        v.ViewType != rdb.ViewType.Internal and
        v.ViewType != rdb.ViewType.Undefined and
        v.ViewType != rdb.ViewType.ProjectBrowser and
        v.ViewType != rdb.ViewType.DrawingSheet and
        v.ViewType != rdb.ViewType.SystemBrowser):
            viewCounter =+ 1
            paras = v.GetOrderedParameters()
            ruleMatch = True
            for paraName, paraCondition, conditionValue in viewRules:
                for p in paras:
                    if(p.Definition.Name == paraName):
                        ruleMatch = ruleMatch and rParaGet.check_parameter_value(p, paraCondition, conditionValue)
            if (ruleMatch == True):
                # delete view
                ids.append(v.Id)
    # make sure we are not trying to delete all views (this allowed when a model is opened into memory only, but that model will crash when trying to open into UI)
    if(len(ids) == viewCounter and len(ids) > 0):
        ids.pop()
    # delete all views at once
    result = rDel.delete_by_element_ids(doc,ids, 'deleting views not matching filters','views')
    return result


def delete_views_not_on_sheets(doc, filter):
    '''
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
    '''

    ids = []
    returnValue = res.Result()
    viewsNotOnSheets = get_views_not_on_sheet(doc)
    for viewNotOnSheet in viewsNotOnSheets:
        if(filter(viewNotOnSheet)):
            ids.append(viewNotOnSheet.Id)
    # check we are not trying to delete all views
    if(len(viewsNotOnSheets) == len(ids) and len(viewsNotOnSheets) > 0):
        # remove a random view from this list
        ids.pop(0)
    if(len(ids) > 0):
        returnValue = rDel.delete_by_element_ids(doc,ids, 'deleting '+ str(len(viewsNotOnSheets)) +' views not on sheets', 'views')
    else:
        returnValue.UpdateSep(True, 'No views not placed on sheets found.')
    return returnValue


def delete_unused_elevation_view_markers(doc):
    '''
    Deletes all unused elevation markers. (no Elevation is created by the marker)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: 
        Result class instance.
        - .result = True if all unused elevation markers where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    ele = rdb.FilteredElementCollector(doc).OfClass(rdb.ElevationMarker)
    # items to be deleted
    ids = []
    # set up view counter (how many views will be deleted)
    counter = 0
    # loop over markers
    for e in ele:
        # check if view count is 0 (unused marker)
        if(e.CurrentViewCount == 0):
            # add to list of views to be deleted
            ids.append(e.Id)
            counter += 1
    if(len(ids) > 0):
        returnValue = rDel.delete_by_element_ids(doc,ids, 'deleting unused view markers: ' + str(counter),'view marker')
    else:
        returnValue.UpdateSep(True, 'No unused elevation markers in model')
    return returnValue


def delete_sheets(doc, viewRules, collectorViews):
    '''
    Deletes sheets based on rules.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewRules: A set of rules. If view matches rule it will be deleted.
    :type viewRules: array in format [parameter name, condition test method, value to test against
    :param collectorViews: A filtered element collector containing view instances.
    :type collectorViews: Autodesk.Revit.DB.FilteredElementCollector
    :return: 
        Result class instance.
        - .result = True if all sheets matching filter where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    '''

    ids = []
    for v in collectorViews:
        if(v.ViewType == rdb.ViewType.DrawingSheet):
            paras = v.GetOrderedParameters()
            ruleMatch = True
            for paraName, paraCondition, conditionValue in viewRules:
                for p in paras:
                    if(p.Definition.Name == paraName):
                        ruleMatch = ruleMatch and rParaGet.check_parameter_value(p, paraCondition, conditionValue)
            if (ruleMatch == True):
                # delete view
                ids.append(v.Id)
    result = rDel.delete_by_element_ids(doc,ids, 'deleting sheets', 'sheets')
    return result


def delete_all_sheets(doc):
    '''
    Deletes all sheets in a model
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: 
        Result class instance.
        - .result = True if all sheets where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    ids = []
    collectorSheets = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in collectorSheets:
        if(v.ViewType == rdb.ViewType.DrawingSheet):
           ids.append(v.Id)
    if (len(ids)>0):
        returnValue = rDel.delete_by_element_ids(doc,ids, 'deleting all sheets', 'sheets')
    else:
        returnValue.UpdateSep(True, 'No sheets in the model')
    return returnValue