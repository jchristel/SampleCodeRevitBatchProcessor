'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit views. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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
import clr
import System

# import common library modules
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res
from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in views report
REPORT_VIEWS_HEADER = ['HOSTFILE']
#: header used in sheets report
REPORT_SHEETS_HEADER = ['HOSTFILE','Id']

# --------------------------------------------- utility functions ------------------

# --------------------------------------------- View Types  ------------------

def GetViewTypes(doc):
    '''
    Returns all view family types in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A filtered element collector.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.ViewFamilyType)

def GetViewTypeIds(doc):
    '''
    Returns all view family type ids in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: ids of view family types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewFamilyType)
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetUsedViewTypeIdsInTheModel(doc):
    '''
    Returns all view family types in use in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: ids of view family types in use
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    viewTypeIdsUsed = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out browser organization and other views which cant be deleted
        if(v.IsTemplate == False and 
        v.ViewType != rdb.ViewType.SystemBrowser and 
        v.ViewType != rdb.ViewType.ProjectBrowser and 
        v.ViewType != rdb.ViewType.Undefined and 
        v.ViewType != rdb.ViewType.Internal and 
        v.ViewType != rdb.ViewType.DrawingSheet):
            if(v.GetTypeId() not in viewTypeIdsUsed):
                viewTypeIdsUsed.append(v.GetTypeId())
    return viewTypeIdsUsed

def GetUnusedViewTypeIdsInModel(doc):
    '''
    Returns all unused view family types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: ids of view family types not in use
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filteredUnusedViewTypeIds = com.GetUnusedTypeIdsInModel(doc, GetViewTypes, GetUsedViewTypeIdsInTheModel)
    return filteredUnusedViewTypeIds
 
# -------------------------------------------View Templates --------------------------------------------

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
    viewFamilyTemplates = com.GetSimilarTypeFamiliesByType(doc, GetViewTypes)
    for vt in viewFamilyTemplates:
        for id in vt[1]:
            # get the element
            vtFam = doc.GetElement(id)
            if(vtFam.DefaultTemplateId not in viewTemplateIdsUsed and 
            vtFam.DefaultTemplateId != rdb.ElementId.InvalidElementId):
                viewTemplateIdsUsed.append(vtFam.DefaultTemplateId)
    return viewTemplateIdsUsed

# doc   current model document
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

# -------------------------------------------View Filters --------------------------------------------

#: List of view types which can have filters applied
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
    rdb.ViewType.Legend
]

def GetAllAvailableFiltersInModel(doc):
    '''
    Gets all filters in document as a collector

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered Element collector containing Autodesk.Revit.DB.ParameterFilterElement
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ParameterFilterElement)
    return collector

def GetAllAvailableFilterIdsInModel(doc):
    '''
    Gets all view filter ids in document

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All view filter Id's which are in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = GetAllAvailableFiltersInModel(doc)
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetFilterIdsFromViewByFilter(view, uniqueList):
    '''
    Returns past in list of filter id's plus new unique filter id's from view (if not already in list past in)

    :param view: The view of which to get the filters from.
    :type view: Autodesk.Revit.DB.View
    :param uniqueList: List containing view filters
    :type uniqueList: list of Autodesk.Revit.DB.ElementId

    :return: List containing past in view filters and new view filters.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filters = view.GetFilters()
    if len(filters) != 0:
        for j in filters:
            if (j not in uniqueList): 
                uniqueList.append(j)
    return uniqueList

def GetFiltersFromTemplates(doc):
    '''
    Gets all filter id's used in view templates only.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List containing filter Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filtersInUse = []
    # get view filters used in templates only
    # include templates which do not enforce filters but still may have some set
    templateWithFilters = GetTemplateIdsWhichCanHaveFilters(doc, VIEW_TYPE_WHICH_CAN_HAVE_FILTERS)
    for temp in templateWithFilters:
        # get filters and check whether already in list
        filtersInUse = GetFilterIdsFromViewByFilter(temp, filtersInUse)
    return filtersInUse

def GetFilterIdsFromViewsWithoutTemplate(doc, filterByType):
    '''
    Gets all filter id's from views which dont have a template applied and match a given view type.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filterByType: list of view types of which the filters are to be returned.
    :type filterByType: list of Autodesk.Revit.DB.ViewType

    :return: List containing filter Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filtersInUse = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # cant filter out templates or templates which do not control filters to be more precise
        # views The parameter:
        # BuiltInParameter.VIS_GRAPHICS_FILTERS
        # which is attached to views is of storage type None...not much use...
        if(v.IsTemplate == False):
            for filter in filterByType:
                if (v.ViewType == filter):
                    GetFilterIdsFromViewByFilter(v, filtersInUse)
                    break
    return filtersInUse

def GetAllUnUsedViewFilters(doc):
    '''
    Gets id's of all unused view filters in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List containing filter Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    unUsedViewFilterIds = []
    allAvailableFilters = GetAllAvailableFiltersInModel(doc)
    allFilterIdsByTemplate = GetFiltersFromTemplates(doc)
    allFilterIdsByView = GetFilterIdsFromViewsWithoutTemplate(doc, VIEW_TYPE_WHICH_CAN_HAVE_FILTERS)
    # combine list of used filters into one
    allUsedViewFilters = allFilterIdsByTemplate + allFilterIdsByView
    # loop over all available filters and check for match in used filters
    for availableF in allAvailableFilters:
        if(availableF.Id not in allUsedViewFilters):
            unUsedViewFilterIds.append(availableF.Id)
    return unUsedViewFilterIds
# ----------------------------------------------------------------------------------------

def GetScheduleIdsOnSheets(doc):
    '''
    Gets view ids of all schedules with instances placed on a sheet

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List containing schedule Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids=[]
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ScheduleSheetInstance)
    for s in col:
        if s.ScheduleId not in ids:
            ids.append(s.ScheduleId)
    return ids
 
def GetViewsOfType(doc, viewType):
    '''
    Gets all views in a model of a given type. Excludes templates.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewType: Filter: the view type
    :type viewType: Autodesk.Revit.DB.ViewType

    :return: list of views
    :rtype: list of Autodesk.Revit.DB.View
    '''

    views=[]
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        if(v.ViewType == viewType and v.IsTemplate == False):
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

    return GetViewsOfType(doc, rdb.ViewType.DrawingSheet)

def GetViewportOnSheets(doc, sheets):
    '''
    Get all view ports on sheets provided.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: list of sheets of which to return the view ports from.
    :type sheets: list of Autodesk.Revit.DB.ViewSheet

    :return: list of view ports
    :rtype: list of Autodesk.Revit.DB.Viewport
    '''

    viewPorts = []
    for sheet in sheets:
        try:
            viewportIds = sheet.GetAllViewports()
            if(viewportIds != None):
                for viewportId in viewportIds:
                    viewport = doc.GetElement(viewportId)
                    viewPorts.append(viewport)
        except Exception as e:
            print(str(e))
    return viewPorts

def FilterRevisionSchedules(view):
    '''
    Checks whether a view is a revision schedule.

    :param view: The view to check.
    :type view: Autodesk.Revit.DB.View

    :return: True if the view name starts with '<', otherwise False
    :rtype: bool
    '''

    if(view.Name.startswith('<')):
        return False
    else:
        return True

def GetViewsInModel(doc, filter):
    '''
    Gets all views in a model which are matching a filter and are:

    - not template views
    - not system browser
    - not project browser
    - not undefined
    - not Internal
    - not sheets
   

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter: function checking view
    :type filter: func(view) returning a bool

    :return: list of views
    :rtype: list of Autodesk.Revit.DB.View
    '''

    views = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        #filter out browser organization and other views which cant be deleted
        if(v.IsTemplate == False and filter(v) == True and 
        v.ViewType != rdb.ViewType.SystemBrowser and 
        v.ViewType != rdb.ViewType.ProjectBrowser and 
        v.ViewType != rdb.ViewType.Undefined and 
        v.ViewType != rdb.ViewType.Internal and 
        v.ViewType != rdb.ViewType.DrawingSheet):
            views.append(v)
    return views

def GetSchedulesNotOnSheets(doc):
    '''
    Gets all schedules without an instance placed on a sheet.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: list of schedules without a sheet schedule instance.
    :rtype: list of Autodesk.Revit.DB.View
    '''

    schedulesNotOnSheets = []
    # get schedules on sheets
    idsOnSheets = GetScheduleIdsOnSheets(doc)
    # get all schedules in model
    schedulesInModel = GetViewsOfType(doc, rdb.ViewType.Schedule)
    # loop and filter out schedules not on sheets
    for schedule in schedulesInModel:
        if(schedule.Id not in idsOnSheets):
            schedulesNotOnSheets.append(schedule)
    return schedulesNotOnSheets

def GetViewsNotOnSheet(doc):
    '''
    Gets all views not placed on a sheet. (Excludes schedules)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of views which are currently not placed on a sheet.
    :rtype: list of Autodesk.Revit.DB.View
    '''

    viewsNotOnSheet = []
    # get all sheets
    sheetsInModel = GetSheetsInModel(doc)
    # get all viewPorts on sheets
    viewPortsOnSheets = GetViewportOnSheets(doc, sheetsInModel)
    # get all views in model
    viewsInModel = GetViewsInModel(doc, FilterRevisionSchedules)
    # check whether view has a viewport if not ... its not placed on a sheet
    for viewInModel in viewsInModel:
        match = False
        for viewPortsOnSheet in viewPortsOnSheets:
            if(viewPortsOnSheet.ViewId == viewInModel.Id):
                match = True
                break
        if(match == False):
            viewsNotOnSheet.append(viewInModel)
    return viewsNotOnSheet

# deletes views based on
# view rules: array in format [parameter name, condition test method, value to test against]
def DeleteViews(doc, viewRules, collectorViews):
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
    result = com.DeleteByElementIds(doc,ids, 'deleting views not matching filters','views')
    return result

def DeleteViewsNotOnSheets(doc, filter):
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
    viewsNotOnSheets = GetViewsNotOnSheet(doc)
    for viewNotOnSheet in viewsNotOnSheets:
        if(filter(viewNotOnSheet)):
            ids.append(viewNotOnSheet.Id)
    # check we are not trying to delete all views
    if(len(viewsNotOnSheets) == len(ids) and len(viewsNotOnSheets) > 0):
        # remove a random view from this list
        ids.pop(0)
    if(len(ids) > 0):
        returnValue = com.DeleteByElementIds(doc,ids, 'deleting '+ str(len(viewsNotOnSheets)) +' views not on sheets', 'views')
    else:
        returnValue.UpdateSep(True, 'No views not placed on sheets found.')
    return returnValue

def DeleteUnusedElevationViewMarkers(doc):
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
        returnValue = com.DeleteByElementIds(doc,ids, 'deleting unused view markers: ' + str(counter),'view marker')
    else:
        returnValue.UpdateSep(True, 'No unused elevation markers in model')
    return returnValue

def DeleteSheets(doc, viewRules, collectorViews):
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
    result = com.DeleteByElementIds(doc,ids, 'deleting sheets', 'sheets')
    return result

def DeleteAllSheetsInModel(doc):
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
        returnValue = com.DeleteByElementIds(doc,ids, 'deleting all sheets', 'sheets')
    else:
        returnValue.UpdateSep(True, 'No sheets in the model')
    return returnValue

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

# ------------------------------------------------------- sheet reporting --------------------------------------------------------------------

def WriteSheetData(doc, fileName, currentFileName):
    '''
    Writes to file all sheet properties.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param fileName: The fully qualified file path of the report file.
    :type fileName: str
    :param currentFileName: The current revit file name which will be appended to data in the report.
    :type currentFileName: str
    :return: 
        Result class instance.
        
        - .result = True if data was written successfully. Otherwise False.
        - .message will contain write status.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        data = GetSheetReportData(doc, currentFileName)
        headers = GetReportHeaders(doc)
        util.writeReportData(
            fileName, 
            headers, 
            data)
        returnValue.UpdateSep(True, 'Successfully wrote data file')
    except Exception as e:
        returnValue.UpdateSep(False, str(e))
    return returnValue

def WriteSheetDataByPropertyNames(doc, fileName, currentFileName, sheetProperties):
    '''
    Writes to file sheet properties as nominated in past in list.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param fileName: The fully qualified file path of the report file.
    :type fileName: str
    :param currentFileName: The current Revit file name which will be appended to data in the report.
    :type currentFileName: str
    :param sheetProperties: List of sheet properties to be extracted from sheets.
    :type sheetProperties: list of str

    :return: 
        Result class instance.
    
        - .result = True if data was written successfully. Otherwise False.
        - .message will contain write status.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        data = GetSheetReportData(doc, currentFileName)
        headers = GetReportHeaders(doc)
        data = FilterDataByProperties(data, headers, sheetProperties)
        # change headers to filtered + default
        headers = REPORT_SHEETS_HEADER[:]
        headers = headers + sheetProperties
        # write data out to file
        util.writeReportData(
            fileName, 
            headers, 
            data)
        returnValue.UpdateSep(True, 'Successfully wrote data file')
    except Exception as e:
        returnValue.UpdateSep(False, str(e))
    return returnValue

def FilterDataByProperties(data, headers, sheetProperties):
    '''
    Filters sheet data by supplied property names.

    Data gets filtered twice: property needs to exist in headers list as well as in sheet properties list.

    :param data: List of sheet properties to be kept.
    :type data: list of list of str
    :param headers: Filter: list of headers representing property names.
    :type headers: list of str
    :param sheetProperties: list of sheet properties to be extracted from data
    :type sheetProperties: list of str

    :return: List of sheet properties matching filters.
    :rtype: list of list of str
    '''

    # add default headers to properties to be filtered first
    dataIndexList= [iter for iter in range(len(REPORT_SHEETS_HEADER))]
    # build index pointer list of data to be kept
    for f in sheetProperties:
        if (f in headers):
            dataIndexList.append(headers.index(f))
    # filter data out
    newData = []
    for d in data:
        dataRow = []
        for i in dataIndexList:
            dataRow.append(d[i])
        newData.append(dataRow)
    return newData

def GetSheetReportData(doc, hostName):
    '''
    Gets sheet data to be written to report file.

    The data returned includes all sheet properties available in the file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param hostName: The file hostname, which is added to data returned
    :type hostName: str

    :return: list of list of sheet properties.
    :rtype: list of list of str
    '''

    collectorViews = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    views = []
    for v in collectorViews:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        data = [hostName, str(v.Id)]
        for para in paras:
            # get values as utf-8 encoded strings
            value = rParaGet.get_parameter_value_utf8_string (para)
            try:
                data.append (value)
            except:
                data.append('Failed to retrieve value')
        views.append(data)
    return views

def GetReportHeaders(doc):
    '''
    A list of headers used in report files

    Hardcoded header list is expanded by parameters added to sheet category in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of headers.
    :rtype: list str
    '''

    collectorViews = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    # copy headers list
    headers = REPORT_SHEETS_HEADER[:]
    for v in collectorViews:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        for para in paras:
            headers.append (para.Definition.Name)
        break
    return headers