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
REPORT_VIEWS_HEADER = ['HOSTFILE','ID', 'NAME']
REPORT_SHEETS_HEADER = ['HOSTFILE','ID', 'NAME']

# --------------------------------------------- utility functions ------------------

# --------------------------------------------- View Types  ------------------

# returns all view family types in a model
# doc: current model
def GetViewTypes(doc):
    return FilteredElementCollector(doc).OfClass(ViewFamilyType)

# returns all view family types in the model
# doc   current model document
def GetUsedViewTypeIdsInTheModel(doc):
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


# returns a list of uniqe viewtypes and similar view family types in format:
# [[view type, similar view type id, similar view type id]]
# doc   current model document
def GetSimilarViewTypeFamiliesByViewType(doc):
    simTypes=[]
    vts = GetViewTypes(doc)
    for vt in vts:
        vtData = [vt]
        sims = vt.GetSimilarTypes()
        simData = []
        for sim in sims:
            simData.append(sim)
        vtData.append(simData)
        if(CheckUniqueViewTypeData(simTypes, vtData)):
            simTypes.append(vtData)
    return simTypes

# checking whether we have view type and asociated viewfamily types already
# returns true 
# -if view type is not in list source passed in or
# -if ids of similar view family types do not match any similar view types already in list
def CheckUniqueViewTypeData(source, newData):
    result = True
    for s in source:
        # check for matching view family name
        if (s[0].FamilyName == newData[0].FamilyName):
            # check if match has the same amount of similar view family types
            # if not it is unique
            if (len(s[1]) == len(newData[1])):
                # assume IDs do match
                matchIDs = True
                for i in range(len(s[1])):
                    if(s[1][i] != newData[1][i]):
                          # id's dont match, this is unique
                          matchIDs = False
                          break
                if(matchIDs):
                    # data is not unique
                    result = False
                    break
    return result

# returns ID of unused view family types in the model
# doc   current model document
def GetUnusedViewTypeIdsInModel(doc):
    # get all view types available and associated view family types
    viewFamilTypesAvailable = GetSimilarViewTypeFamiliesByViewType(doc)
    # get used view type ids
    usedViewFamilyTypeIds = GetUsedViewTypeIdsInTheModel(doc)
    # loop over avaiable types and check which one is used
    for vt in viewFamilTypesAvailable:
        # remove all used view family type Id's from the available list...
        # whatever is left can be deleted if not last available item in list for view type
        # there should always be just one match
        for usedfamilyViewTypeId in usedViewFamilyTypeIds:
                # get the index of match
                index = util.IndexOf(vt[1],usedfamilyViewTypeId)
                # remove used item from list
                if (index > -1):
                   vt[1].pop(index) 
    # filter these by view family types where is only one left
    # make sure to leave at least one family type behind, since the last type cannot be deleted
    filteredUnusedViewTypeIds = []
    for vt in viewFamilTypesAvailable:
        if(len(vt[1]) > 1):
            # check whether this can be deleted...
            for id in vt[1]:
                # get the element
                vtFam = doc.GetElement(id)
                if (vtFam.CanBeDeleted):
                    filteredUnusedViewTypeIds.append(id)
    return filteredUnusedViewTypeIds     
 
# -------------------------------------------------------------------------------------------------------

# returns view ids of all schedules on a sheet
def GetScheduleIdsOnSheets(doc):
    ids=[]
    col = FilteredElementCollector(doc).OfClass(ScheduleSheetInstance)
    for s in col:
        if s.ScheduleId not in ids:
            ids.append(s.ScheduleId)
    return ids

# returns all views in a model of a given type 
# excludes templates!
def GetViewsofType(doc, viewtype):
    views=[]
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        if(v.ViewType == viewtype and v.IsTemplate == False):
            views.append(v)
    return views

# returns all sheets in a model
def GetSheetsInModel(doc):
    return GetViewsofType(doc, ViewType.DrawingSheet)

# returns all view ports
# doc:      current document
# sheets:   all sheets to retrieve view ports from
def GetViewportOnSheets(doc, sheets):
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

# returns true if the view name starts with '<', otherwise false
def FilterRevisionSchedules(view):
    if(view.Name.startswith('<')):
        return False
    else:
        return True

# returns all views in a model which are
# not template views
# not system browser
# not project broser
# not undefined
# not Internal
# not sheets
# match a filter
def GetViewsInModel(doc, filter):
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

# returns all schedules not on a sheet
def GetScheduleIdsNotOnSheets(doc):
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

# returns all views not on a sheet
# excludes schedules
def GetViewsNotOnSheet(doc):
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

# deletes all views not placed on sheets
# includes schedules and legends
def DeleteViewsNotOnSheets(doc, filter):
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

# deletes unused elevation markers
def DeleteUnusedElevationViewMarkers(doc):
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

# deletes sheets based on
# view rules: array in format [parameter name, condition test method, value to test against]
def DeleteSheets(doc, viewRules, collectorViews):
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

# deletes all sheets in a model
def DeleteAllSheetsInModel(doc):
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

# returns sheets matching filters provided
# view rules: array in format [parameter name, condition test method, value to test against]
def GetSheetsByFilters(doc, viewRules = None):
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
