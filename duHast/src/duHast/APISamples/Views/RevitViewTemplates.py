'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view templates. 
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

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Views.Utility.ViewTypes import _get_view_types


def GetViewsTemplatesInInModel(doc):
    '''
    Get all view templates in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates in the model
    :rtype: list of Autodesk.Revit.DB.View
    '''

    viewTemplates = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out templates
        if(v.IsTemplate):
            viewTemplates.append(v)
    return viewTemplates


def GetViewsTemplateIdsInInModel(doc):
    '''
    Get all view template ids in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's in the model
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out templates
        if(v.IsTemplate):
            ids.append(v.Id)
    return ids


def GetUsedViewTemplateIdsInTheModel(doc):
    '''
    Gets ids of view templates used in views in the model only
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All used view templates Id's in the model
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    viewTemplateIdsUsed = []
    # get all view templates assigned to views
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out browser organization and other views which cant be deleted
        if(v.IsTemplate == False and
        v.ViewType != rdb.ViewType.SystemBrowser and
        v.ViewType != rdb.ViewType.ProjectBrowser and
        v.ViewType != rdb.ViewType.Undefined and
        v.ViewType != rdb.ViewType.Internal and
        v.ViewType != rdb.ViewType.DrawingSheet):
            if(v.ViewTemplateId not in viewTemplateIdsUsed and v.ViewTemplateId != rdb.ElementId.InvalidElementId):
                viewTemplateIdsUsed.append(v.ViewTemplateId)
    return viewTemplateIdsUsed


def GetDefaultViewTypeTemplateIds(doc):
    '''
    Gets view template Id's used as default by view types
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's which are used as default in view types in the model
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    viewTemplateIdsUsed = []
    # get all templates assigned to view family types:
    viewFamilyTemplates = com.GetSimilarTypeFamiliesByType(doc, _get_view_types)
    for vt in viewFamilyTemplates:
        for id in vt[1]:
            # get the element
            vtFam = doc.GetElement(id)
            if(vtFam.DefaultTemplateId not in viewTemplateIdsUsed and
            vtFam.DefaultTemplateId != rdb.ElementId.InvalidElementId):
                viewTemplateIdsUsed.append(vtFam.DefaultTemplateId)
    return viewTemplateIdsUsed


def GetAllViewTemplateIdsUsedInModel(doc):
    '''
    Get all used view template Id's.
    Templates can either be:
    - used as default by view types
    - used by a view 
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's which are used in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    vtv = GetUsedViewTemplateIdsInTheModel(doc)
    viewFamilyTemplates = GetDefaultViewTypeTemplateIds(doc)
    for id in viewFamilyTemplates:
        if(id not in vtv):
            vtv.append(id)
    return vtv


def GetTemplateIdsWhichCanHaveFilters(doc, filterByType):
    '''
    Get all templates in a model of given type
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filterByType: List of view types of which to return view templates from
    :type filterByType: list of Autodesk.Revit.DB.ViewType
    :return: All view templates in the model
    :rtype: list of Autodesk.Revit.DB.View
    '''

    viewTemplates = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out templates
        if(v.IsTemplate):
            for filter in filterByType:
                if (v.ViewType == filter):
                    viewTemplates.append(v)
                    break
    return viewTemplates


def GetAllUnusedViewTemplateIdsInModel(doc):
    '''
    Gets all view template Id's not used by view types or by views
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's which are not used in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''
    usedVts = GetAllViewTemplateIdsUsedInModel(doc)
    vtInModel = GetViewsTemplatesInInModel(doc)
    unusedVts = []
    for vt in vtInModel:
        if(vt.Id not in usedVts):
            unusedVts.append(vt.Id)
    return unusedVts