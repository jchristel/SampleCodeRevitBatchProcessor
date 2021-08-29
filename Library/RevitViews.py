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
import RevitCommonAPI as com
import Result as res
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_VIEWS_HEADER = ['HOSTFILE']
REPORT_SHEETS_HEADER = ['HOSTFILE','Id']

# --------------------------------------------- utility functions ------------------

# --------------------------------------------- View Types  ------------------

# doc: current model
def GetViewTypes(doc):
    """returns all view family types in a model"""
    return FilteredElementCollector(doc).OfClass(ViewFamilyType)

# doc   current model document
def GetUsedViewTypeIdsInTheModel(doc):
    """returns all view family types in the model"""
    viewTypeIdsUsed = []
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        # filter out browser organisation and other views which cant be deleted
        if(v.IsTemplate == False and 
        v.ViewType != ViewType.SystemBrowser and 
        v.ViewType != ViewType.ProjectBrowser and 
        v.ViewType != ViewType.Undefined and 
        v.ViewType != ViewType.Internal and 
        v.ViewType != ViewType.DrawingSheet):
            if(v.GetTypeId() not in viewTypeIdsUsed):
                viewTypeIdsUsed.append(v.GetTypeId())
    return viewTypeIdsUsed

# doc   current model document
def GetUnusedViewTypeIdsInModel(doc):
    """returns ID of unused view family types in the model"""
    filteredUnusedViewTypeIds = com.GetUnusedTypeIdsInModel(doc, GetViewTypes, GetUsedViewTypeIdsInTheModel)
    return filteredUnusedViewTypeIds
 
# -------------------------------------------View Templates --------------------------------------------

# doc   current model document
def GetViewsTemplatesInInModel(doc):
    """get all templates in a model"""
    viewTemplates = []
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        # filter out templates
        if(v.IsTemplate):
            viewTemplates.append(v)
    return viewTemplates

# doc   current model document
def GetUsedViewTemplateIdsInTheModel(doc):
    """returns view templates used in views in the model only"""
    viewTemplateIdsUsed = []
    # get all view templates assigned to views
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        # filter out browser organisation and other views which cant be deleted
        if(v.IsTemplate == False and 
        v.ViewType != ViewType.SystemBrowser and 
        v.ViewType != ViewType.ProjectBrowser and 
        v.ViewType != ViewType.Undefined and 
        v.ViewType != ViewType.Internal and 
        v.ViewType != ViewType.DrawingSheet):
            if(v.ViewTemplateId not in viewTemplateIdsUsed and v.ViewTemplateId != ElementId.InvalidElementId):
                viewTemplateIdsUsed.append(v.ViewTemplateId)
    return viewTemplateIdsUsed

# doc   current model document
def GetDefaultViewTypeTemplateIds(doc):
    """returns view template Id's used as default by view types"""
    viewTemplateIdsUsed = []
    # get all templates assigned to view family types:
    vfts = com.GetSimilarTypeFamiliesByType(doc, GetViewTypes)
    for vt in vfts:
        for id in vt[1]:
            # get the element
            vtFam = doc.GetElement(id)
            if(vtFam.DefaultTemplateId not in viewTemplateIdsUsed and 
            vtFam.DefaultTemplateId != ElementId.InvalidElementId):
                viewTemplateIdsUsed.append(vtFam.DefaultTemplateId)
    return viewTemplateIdsUsed

# doc   current model document
def GetAllViewTemplateIdsUsedInModel(doc):
    """returns view template Id's used as default by view types and by views"""
    vtv = GetUsedViewTemplateIdsInTheModel(doc)
    vfts = GetDefaultViewTypeTemplateIds(doc)
    for id in vfts:
        if(id not in vtv):
            vtv.append(id)
    return vtv

# doc   current model document
# filterByType:   list of view types of which to return view templates from
def GetTemplateIdsWhichCanHaveFilters(doc, filterByType):
    """get all templates in a model of given type"""
    viewTemplates = []
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        # filter out templates
        if(v.IsTemplate):
            for filter in filterByType:
                if (v.ViewType == filter):
                    viewTemplates.append(v)
                    break
    return viewTemplates

# doc   current model document
def GetAllUnusedViewTemplateIdsInModel(doc):
    """returns all view template Id's not used by view types and by views"""
    usedVts = GetAllViewTemplateIdsUsedInModel(doc)
    vtInModel = GetViewsTemplatesInInModel(doc)
    unusedVts = []
    for vt in vtInModel:
        if(vt.Id not in usedVts):
            unusedVts.append(vt.Id)
    return unusedVts

# -------------------------------------------View Filters --------------------------------------------

# all view types which can have filters applied
VIEW_TYPE_WHICH_CAN_HAVE_FILTERS = [ViewType.FloorPlan, ViewType.CeilingPlan, ViewType.Elevation, ViewType.ThreeD, ViewType.EngineeringPlan, ViewType.AreaPlan, ViewType.Section, ViewType.Detail, ViewType.Walkthrough, ViewType.DraftingView, ViewType.Legend]

# doc   current model document
def GetAllAvailableFiltersInModel(doc):
    """returns all filters in document as a collector"""
    collector = FilteredElementCollector(doc).OfClass(ParameterFilterElement)
    return collector

# view   view from which to get the filters from
# uniqueList    list of filters of which to add new filters to (not already in list)
def GetFilterIdsFromViewByFilter(view, uniqueList):
    """returns passed in list of filter id's plus new filter id's from view (not already in list passt in)"""
    filters = view.GetFilters()
    if len(filters) != 0:
        for j in filters:
            if (j not in uniqueList): 
                uniqueList.append(j)
    return uniqueList

# doc   current model document
def GetFiltersFromTemplates(doc):
    """returns all filters used in templates only"""
    filtersInUse = []
    # get view filters used in templates only
    # include templates which do not enforce filters but still may have some set
    templateWithFilters = GetTemplateIdsWhichCanHaveFilters(doc, VIEW_TYPE_WHICH_CAN_HAVE_FILTERS)
    for temp in templateWithFilters:
        # get filters and check whether already in list
        filtersInUse = GetFilterIdsFromViewByFilter(temp, filtersInUse)
    return filtersInUse

# doc   current model document
# filterByType:   list of view types of which to return view templates from
def GetFilterIdsFromViewsWithoutTemplate(doc, filterByType):
    """get all filters from views which dont have a template applied"""
    filtersInUse = []
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        # cant filter out templates or templates which do not control filters to be more precise
        # views The parameter:
        # BuiltInParameter.VIS_GRAPHICS_FILTERS
        # which is attached to views is of strorage type None...not much use...
        if(v.IsTemplate == False):
            for filter in filterByType:
                if (v.ViewType == filter):
                    GetFilterIdsFromViewByFilter(v, filtersInUse)
                    break
    return filtersInUse

# doc   current model document
def GetAllUnUsedViewFilters(doc):
    """gets id's of all unused view filters in a model"""
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
    """returns view ids of all schedules on a sheet"""
    ids=[]
    col = FilteredElementCollector(doc).OfClass(ScheduleSheetInstance)
    for s in col:
        if s.ScheduleId not in ids:
            ids.append(s.ScheduleId)
    return ids
 
# excludes templates!
def GetViewsofType(doc, viewtype):
    """returns all views in a model of a given type"""
    views=[]
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        if(v.ViewType == viewtype and v.IsTemplate == False):
            views.append(v)
    return views

def GetSheetsInModel(doc):
    """ returns all sheets in a model"""
    return GetViewsofType(doc, ViewType.DrawingSheet)

# doc:      current document
# sheets:   all sheets to retrieve view ports from
def GetViewportOnSheets(doc, sheets):
    """returns all view ports in the model"""
    viewports = []
    for sheet in sheets:
        try:
            viewportIds = sheet.GetAllViewports()
            if(viewportIds != None):
                for viewportId in viewportIds:
                    viewport = doc.GetElement(viewportId)
                    viewports.append(viewport)
        except Exception as e:
            print(str(e))
    return viewports

def FilterRevisionSchedules(view):
    """returns true if the view name starts with '<', otherwise false"""
    if(view.Name.startswith('<')):
        return False
    else:
        return True

def GetViewsInModel(doc, filter):
    """eturns all views in a model which are
    not template views
    not system browser
    not project broser
    not undefined
    not Internal
    not sheets
    match a filter"""
    views = []
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        #filter out browser organisation and other views which cant be deleted
        if(v.IsTemplate == False and filter(v) == True and 
        v.ViewType != ViewType.SystemBrowser and 
        v.ViewType != ViewType.ProjectBrowser and 
        v.ViewType != ViewType.Undefined and 
        v.ViewType != ViewType.Internal and 
        v.ViewType != ViewType.DrawingSheet):
            views.append(v)
    return views

def GetScheduleIdsNotOnSheets(doc):
    """returns all schedules not on a sheet"""
    schedulesNotOnSheets = []
    # get schedules on sheets
    idsOnSheets = GetScheduleIdsOnSheets(doc)
    # get all schedules in model
    schedulesInModel = GetViewsofType(doc, ViewType.Schedule)
    # loop and filter out schedules not on sheets
    for schedule in schedulesInModel:
        if(schedule.Id not in idsOnSheets):
            schedulesNotOnSheets.append(schedule)
    return schedulesNotOnSheets

# excludes schedules
def GetViewsNotOnSheet(doc):
    """returns all views not on a sheet"""
    viewsNotOnSheet = []
    # get all sheets
    sheetsInModel = GetSheetsInModel(doc)
    # get all viewports on sheets
    viewportsOnSheets = GetViewportOnSheets(doc, sheetsInModel)
    # get all views in model
    viewsInModel = GetViewsInModel(doc, FilterRevisionSchedules)
    # check whether view has a viewport if not ... its not placed on a sheet
    for viewInModel in viewsInModel:
        match = False
        for viewportsOnSheet in viewportsOnSheets:
            if(viewportsOnSheet.ViewId == viewInModel.Id):
                match = True
                break
        if(match == False):
            viewsNotOnSheet.append(viewInModel)
    return viewsNotOnSheet

# deletes views based on
# view rules: array in format [parameter name, condition test method, value to test against]
def DeleteViews(doc, viewRules, collectorViews):
    ids = []
    viewCounter = 0
    for v in collectorViews:
        # filter out revision schedules '<', sheets and other view types which can not be deleted
        if(util.EncodeAscii(v.Name)[0] != '<' and 
        v.ViewType != ViewType.Internal and 
        v.ViewType != ViewType.Undefined and 
        v.ViewType != ViewType.ProjectBrowser and 
        v.ViewType != ViewType.DrawingSheet and 
        v.ViewType != ViewType.SystemBrowser):
            viewCounter =+ 1
            paras = v.GetOrderedParameters()
            ruleMatch = True
            for paraName, paraCondition, conditionValue in viewRules:
                for p in paras:
                    if(p.Definition.Name == paraName):
                        ruleMatch = ruleMatch and com.CheckParameterValue(p, paraCondition, conditionValue)
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
    """deletes all views not placed on sheets includes schedules and legends"""
    ids = []
    returnvalue = res.Result()
    viewsNotOnSheets = GetViewsNotOnSheet(doc)
    for viewNotOnSheet in viewsNotOnSheets:
        if(filter(viewNotOnSheet)):
            ids.append(viewNotOnSheet.Id)
    # check we are not trying to delete all views
    if(len(viewsNotOnSheets) == len(ids) and len(viewsNotOnSheets) > 0):
        # remove a random view from this list
        ids.pop(0)
    if(len(ids) > 0):
        returnvalue = com.DeleteByElementIds(doc,ids, 'deleting '+ str(len(viewsNotOnSheets)) +' views not on sheets', 'views')
    else:
        returnvalue.UpdateSep(True, 'No views not placed on sheets found.')
    return returnvalue

def DeleteUnusedElevationViewMarkers(doc):
    """deletes unused elevation markers"""
    returnvalue = res.Result()
    ele = FilteredElementCollector(doc).OfClass(ElevationMarker)
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
        returnvalue = com.DeleteByElementIds(doc,ids, 'deleting unused view markers: ' + str(counter),'view marker')
    else:
        returnvalue.UpdateSep(True, 'No unused elevation markers in model')
    return returnvalue

def DeleteSheets(doc, viewRules, collectorViews):
    """deletes sheets based on view rules: array in format [parameter name, condition test method, value to test against]"""
    ids = []
    for v in collectorViews:
        if(v.ViewType == ViewType.DrawingSheet):
            paras = v.GetOrderedParameters()
            ruleMatch = True
            for paraName, paraCondition, conditionValue in viewRules:
                for p in paras:
                    if(p.Definition.Name == paraName):
                        ruleMatch = ruleMatch and com.CheckParameterValue(p, paraCondition, conditionValue)
            if (ruleMatch == True):
                # delete view
                ids.append(v.Id)
    result = com.DeleteByElementIds(doc,ids, 'deleting sheets', 'sheets')
    return result

def DeleteAllSheetsInModel(doc):
    """deletes all sheets in a model"""
    returnvalue = res.Result()
    ids = []
    collectorSheets = FilteredElementCollector(doc).OfClass(View)
    for v in collectorSheets:
        if(v.ViewType == ViewType.DrawingSheet):
           ids.append(v.Id)
    if (len(ids)>0):
        returnvalue = com.DeleteByElementIds(doc,ids, 'deleting all sheets', 'sheets')
    else:
        returnvalue.UpdateSep(True, 'No sheets in the model')
    return returnvalue

# view rules: array in format [parameter name, condition test method, value to test against]
def GetSheetsByFilters(doc, viewRules = None):
    """returns sheets matching filters provided"""
    collectorViews = FilteredElementCollector(doc).OfClass(ViewSheet)
    views = []
    for v in collectorViews:
        # if no filter rules applied return al sheets
        if(viewRules is not None):
            paras = v.GetOrderedParameters()
            ruleMatch = True
            for paraName, paraCondition, conditionValue in viewRules:
                for p in paras:
                    if(p.Definition.Name == paraName):
                        ruleMatch = ruleMatch and com.CheckParameterValue(p, paraCondition, conditionValue)
            if (ruleMatch == True):
                # delete view
                views.append(v)
        else:
            views.append(v)
    return views

# ------------------------------------------------------- sheet reporting --------------------------------------------------------------------

# method writing out sheet data
# doc:          current model document
# fileName:     fully qualified file path
def WriteSheetData(doc, fileName, currentFileName):
    """writes out sheet data to file"""
    returnvalue = res.Result()
    try:
        data = GetSheetReportData(doc, currentFileName)
        headers = GetReportHeaders(doc)
        util.writeReportData(
            fileName, 
            headers, 
            data)
        returnvalue.UpdateSep(True, 'Succesfully wrote data file')
    except Exception as e:
        returnvalue.UpdateSep(False, str(e))
    return returnvalue


# doc       the current revit document
# hostanme  the file hostname, which is added to data returned
def GetSheetReportData(doc, hostName):
    """returns sheet data including file name and sheet id"""
    collectorViews = FilteredElementCollector(doc).OfClass(ViewSheet)
    views = []
    for v in collectorViews:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        data = [hostName, str(v.Id)]
        for para in paras:
            # get values as utf-8 encoded strings
            value = com.GetParameterValueUTF8String(para)
            try:
                # replace non utf-8 sqm symbol
                # 
                data.append (value)
            except:
                data.append('Failed to retrieve value')
        views.append(data)
    return views

# doc       the current revit document
def GetReportHeaders(doc):
    """returns sheet data including file name and sheet id"""
    collectorViews = FilteredElementCollector(doc).OfClass(ViewSheet)
    # copy headers list
    headers = REPORT_SHEETS_HEADER[:]
    for v in collectorViews:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        for para in paras:
            headers.append (para.Definition.Name)
        break
    return headers