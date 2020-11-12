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

import datetime
import System
import clr
import glob
import Result as res

from System.IO import Path
from Autodesk.Revit.DB import *
import os.path as path

clr.ImportExtensions(System.Linq)

#----------------------------------------views-----------------------------------------------

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
        #f iler out browser organisation and other views which cant be deleted
        if(v.IsTemplate == False and filter(v) == True and v.ViewType != ViewType.SystemBrowser and v.ViewType != ViewType.ProjectBrowser and v.ViewType != ViewType.Undefined and v.ViewType != ViewType.Internal and v.ViewType != ViewType.DrawingSheet):
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

#----------------------------------------modify views-----------------------------------------------
# currently known filter conditions
# returns True if valueOne does not match valueTwo
def ConDoesNotEqual (valueOne, valueTwo):
    if (valueOne != valueTwo):
        return True
    else:
        return False

# checks a paramter value based on passed in condition  
def CheckParameterValue(para, paraCondition, conditionValue):
    isMatch = False
    pValue = 'no Value'
    if(para.StorageType == StorageType.ElementId or para.StorageType == StorageType.Double or para.StorageType == StorageType.Integer):
        if(para.AsValueString()!= None and para.AsValueString() != ''):
            pValue = para.AsValueString()
    elif(para.StorageType == StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            pValue = para.AsString()
    isMatch = paraCondition(EncodeAscii(conditionValue), EncodeAscii(pValue))
    return isMatch

# deletes views based on
# view rules: array in format [parameter name, condition test method, value to test against]
def DeleteViews(doc, viewRules, collectorViews):
    ids = []
    viewCounter = 0
    for v in collectorViews:
        # filter out revision schedules '<', sheets and other view types which can not be deleted
        if(EncodeAscii(v.Name)[0] != '<' and v.ViewType != ViewType.Internal and v.ViewType != ViewType.Undefined and v.ViewType != ViewType.ProjectBrowser and v.ViewType != ViewType.DrawingSheet and v.ViewType != ViewType.SystemBrowser):
            viewCounter =+ 1
            paras = v.GetOrderedParameters()
            ruleMatch = True
            for paraName, paraCondition, conditionValue in viewRules:
                for p in paras:
                    if(p.Definition.Name == paraName):
                        ruleMatch = ruleMatch and CheckParameterValue(p, paraCondition, conditionValue)
            if (ruleMatch == True):
                # delete view
                ids.append(v.Id)
    # make sure we are not trying to delete all views (this allowed when a model is opened into memory only, but that model will crash when trying to open into UI)
    if(len(ids) == viewCounter and len(ids) > 0):
        ids.pop()
    # delete all views at once
    result = DeleteByElementIds(doc,ids, 'deleting views not matching filters','views')
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
        returnvalue = DeleteByElementIds(doc,ids, 'deleting '+ str(len(viewsNotOnSheets)) +' views not on sheets', 'views')
    else:
        returnvalue.UpdateSep(True, 'No views not placed on sheets found.')
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
                        ruleMatch = ruleMatch and CheckParameterValue(p, paraCondition, conditionValue)
            if (ruleMatch == True):
                # delete view
                ids.append(v.Id)
    result = DeleteByElementIds(doc,ids, 'deleting sheets', 'sheets')
    return result

#----------------------------------------elements-----------------------------------------------

# method deleting elements by list of element id's
# transactionName : name the transaction will be given
# elementName: will appear in description of what got deleted
def DeleteByElementIds(doc, ids, transactionName, elementName):
    returnvalue = res.Result()
    def action():
        actionReturnValue = res.Result()
        try:
            doc.Delete(ids.ToList[ElementId]())
            actionReturnValue.message = 'Deleted ' + str(len(ids)) + ' ' + elementName
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed to delete ' + elementName + ' with exception: ' + str(e))
        return actionReturnValue
    transaction = Transaction(doc,transactionName)
    returnvalue = InTransaction(transaction, action)
    return returnvalue

# attemps to change the worksets of elements provided through an element collector
def ModifyElementWorkset(doc, defaultWorksetName, collector, elementTypeName):
    returnvalue = res.Result()
    returnvalue.message = 'Changing ' + elementTypeName + ' workset to '+ defaultWorksetName + '\n'
    # get the ID of the default grids workset
    defaultId = GetWorksetIdByName(doc, defaultWorksetName)
    counterSuccess = 0
    counterFailure = 0
    # check if invalid id came back..workset no longer exists..
    if(defaultId != ElementId.InvalidElementId):
        # get all elements in collector and check their workset
        for p in collector:
            if (p.WorksetId != defaultId):
                # move element to new workset
                transaction = Transaction(doc, "Changing workset " + p.Name)
                trannyStatus = InTransaction(transaction, GetActionChangeElementWorkset(p, defaultId))
                if (trannyStatus.status == True):
                    counterSuccess += 1
                else:
                    counterFailure += 1
                returnvalue.status = returnvalue.status & trannyStatus.status
            else:
                counterSuccess += 1
                returnvalue.status = returnvalue.status & True 
    else:
        returnvalue.UpdateSep(False, 'Default workset '+ defaultWorksetName + ' does no longer exists in file!')
    returnvalue.AppendMessage('Moved ' + elementTypeName + ' to workset ' + defaultWorksetName + ' [' + str(counterSuccess) + ' :: ' + str(counterFailure) +']')
    return returnvalue

# returns the required action to change a single elements workset
def GetActionChangeElementWorkset(el, defaultId):
    def action():
        actionReturnValue = res.Result()
        try:
            wsparam = el.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
            wsparam.Set(defaultId.IntegerValue)
            actionReturnValue.message = 'Changed element workset.'
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
        return actionReturnValue
    return action

#----------------------------------------worksets-----------------------------------------------

# returns the element id of a workset identified by its name
# returns invalid Id (-1) if no such workset exists
def GetWorksetIdByName(doc, worksetName):
    id = ElementId.InvalidElementId
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if(p.Name == worksetName):
            id = p.Id
            break
    return id

#-------------------------------------------LINKS------------------------------------------------

# deletes all revit links in a file
def DeleteRevitLinks(doc):
    ids = []
    returnvalue = res.Result()
    for p in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RvtLinks):
        ids.append(p.Id)
    # delete all links at once
    returnvalue = DeleteByElementIds(doc, ids, 'Deleting Revit links', 'Revit link(s)')
    return returnvalue

# deletes all CAD links in a file
def DeleteCADLinks(doc):
    ids = []
    returnvalue = res.Result()
    for p in FilteredElementCollector(doc).OfClass(ImportInstance):
        ids.append(p.Id)
    # delete all links at once
    returnvalue = DeleteByElementIds(doc, ids, 'Deleting CAD links', 'CAD link(s)')
    return returnvalue

# reloads revit links from a given location based on the original link type name (starts with)
# link locations: a list of directories where the revit files can be located
# dosomethingwithLinkName can be used to truncate i.e. the revision details of a link
# worksetconfig: None: to use the previously apllied workset config
def ReloadRevitLinks(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    returnvalue = res.Result()
    try:
        # get all revit link types in model
        for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
            linkTypeName = doSomethingWithLinkName(Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnvalue.AppendMessage(linkTypeName + ' :: ' + str(result.LoadResult))
                else:
                    returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

# reloads revit links from a given location based on the original link type name (starts with)
# link locations: a list of directories where the revit files can be located
# linkTypesTobReloaded is a list of elements of class RevitLinkType
# dosomethingwithLinkName can be used to truncate i.e. the revision details of a link
# worksetconfig: None: to use the previously apllied workset config
def ReloadRevitLinksFromList(doc, linkTypesTobReloaded, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    returnvalue = res.Result()
    try:
        # loop over links supplied
        for p in linkTypesTobReloaded:
            linkTypeName = doSomethingWithLinkName(Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnvalue.AppendMessage(linkTypeName + ' :: ' + str(result.LoadResult))
                else:
                    returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

# reloads CAD links from a given location based on the original link type name (starts with)
# link locations: a list of directories where the revit files can be located
# dosomethingwithLinkName can be used to truncate i.e. the revision details of a link
def ReloadCADLinks(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName):
    returnvalue = res.Result()
    try:
        # get all CAD link types in model
        for p in FilteredElementCollector(doc).OfClass(CADLinkType):
            linkTypeName = doSomethingWithLinkName(Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.dwg')
                if(newLinkPath != None):
                    # reloading CAD links requires a transaction
                    def action():
                        actionReturnValue = res.Result()
                        try:
                            result = p.LoadFrom(newLinkPath)
                            actionReturnValue.message = linkTypeName + ' :: ' + str(result.LoadResult)
                        except Exception as e:
                            actionReturnValue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
                        return actionReturnValue
                    transaction = Transaction(doc, 'Reloading: ' + linkTypeName)
                    reloadResult = InTransaction(transaction, action)
                    returnvalue.Update(reloadResult)
                else:
                    returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

# returns a fully qualified file path to a file name (revit project file extension .rvt) match in given directory locations
# returns None if multiple or no matches where found
def GetLinkPath(fileName, possibleLinkLocations, fileExtension):
    linkPath = None
    counter = 0
    try:
        foundMatch = False
        # attempt to find filename match in given locations
        for linkLocation in possibleLinkLocations:
            fileList = glob.glob(linkLocation + '\\*' + fileExtension)
            if (fileList != None):
                for file in fileList:
                    fileNameInFolder = path.basename(file)
                    if (fileNameInFolder.startswith(fileName)):
                        linkPath = file
                        counter =+ 1
                        foundMatch = True
                        break
        # return none if multiple matches where found            
        if(foundMatch == True and counter > 1):
            linkPath = None
    except Exception:
        linkPath = None
    return linkPath

# default 'do something with link name' method
# which returns the name unchanged
# could be replaced with something which i.e. truncates the revision...
def DefaultLinkName(name):
    return name

# default method for returning a workset configuration
# None in this case reloads a link with the last used workset settings
def DefaultWorksetConfigForReload():
    return None
#-------------------------------------------------------file IO --------------------------------------

# get a time stamp in format year_month_day
def GetFileDateStamp():
    d = datetime.datetime.now()
    return d.strftime('%y_%m_%d')

# returns an time stamped output file name based on the revit file name
# file extension needs to include '.', default is '.txt'
# file suffix will be appended after the name but before the file extension. Default is blank.
def GetOutPutFileName(revitFilePath, fileExtension = '.txt', fileSuffix = ''):
    # get date prefix for file name
    filePrefix = GetFileDateStamp()
    name = Path.GetFileNameWithoutExtension(revitFilePath)
    return filePrefix + '_' + name + fileSuffix + fileExtension

# returns the revit file name without the file extension
def GetRevitFileName(revitFilePath):
    name = Path.GetFileNameWithoutExtension(revitFilePath)
    return name

# removes '..\..' or '..\' from relative file path supplied by Revit and replaces it with full path derived from Revit document
def ConvertRelativePathToFullPath(relativeFilePath, fullFilePath):
    if( r'..\..' in relativeFilePath):
        two_up = path.abspath(path.join(fullFilePath ,r'..\..'))
        return two_up + relativeFilePath[5:]
    elif('..' in relativeFilePath):
        one_up = path.abspath(path.join(fullFilePath ,'..'))
        return one_up + relativeFilePath[2:]
    else:
        return relativeFilePath


# synchronises a Revit central file
# returns:
#   - true if sync without exception been thrown
#   - false if an exception occured
def SyncFile (doc):
    returnvalue = res.Result()
    # set up sync settings
    ro = RelinquishOptions(True)
    transActOptions = TransactWithCentralOptions()
    sync = SynchronizeWithCentralOptions()
    sync.Comment = 'Synchronised by Revit Batch Processor'
    sync.SetRelinquishOptions(ro)
    # Synch it
    try:
        # save local first ( this seems to prevent intermittend crash on sync(?))
        doc.Save()
        doc.SynchronizeWithCentral(transActOptions, sync)
        # relinquish all
        WorksharingUtils.RelinquishOwnership(doc, ro, transActOptions)
        returnvalue.message = 'Succesfully synched file.'
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

# saves a new central file to given location
def SaveAsWorksharedFile(doc, fullFileName):
    returnvalue = res.Result()
    try:
        workSharingSaveAsOption = WorksharingSaveAsOptions()
        workSharingSaveAsOption.OpenWorksetsDefault = SimpleWorksetConfiguration.AskUserToSpecify
        workSharingSaveAsOption.SaveAsCentral = True
        saveOption = SaveAsOptions()
        saveOption.OverwriteExistingFile = True
        saveOption.SetWorksharingOptions(workSharingSaveAsOption)
        saveOption.MaximumBackups = 5
        saveOption.Compact = True
        doc.SaveAs(fullFileName, saveOption)
        returnvalue.message = 'Succesfully saved file: ' + str(fullFileName)
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

#save file under new name in given location
# targetFolderPath: directory path of where the file is to be saved
# currentFullFileName: fully qualified file name of the current Revit file
# name data: list of arrays in format[[oldname, newName]] where old name and new name are revit file names without file extension
def SaveAs(doc, targetFolderPath, currentFullFileName, nameData):
    returnvalue = res.Result()
    revitFileName = GetRevitFileName(currentFullFileName)
    newFileName= ''
    match = False
    for oldName, newName in nameData:
        if (revitFileName.startswith(oldName)):
            match = True
            returnvalue.message = ('Found file name match for: ' + revitFileName + ' new name: ' + newName)
            # save file under new name
            newFileName = targetFolderPath + '\\'+ newName +'.rvt'
            break
    if(match == False):
        # save under same file name
        newFileName = targetFolderPath + '\\'+ revitFileName +'.rvt'
        returnvalue.message = 'Found no file name match for: ' + currentFullFileName
    try:
        returnvalue.status = SaveAsWorksharedFile(doc, newFileName).status
        returnvalue.AppendMessage('Saved file: ' + newFileName)
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed to save revit file to new location!' + ' exception: ' + str(e))
    return returnvalue

# enables work sharing
def EnableWorksharing(doc, worksetNameGridLevel = 'Shared Levels and Grids', worksetName = 'Workset1'):
    returnvalue = res.Result()
    try:
        doc.EnableWorksharing('Shared Levels and Grids','Workset1')
        returnvalue.message = 'Succesfully enabled worksharing.'
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

#--------------------------------------------Transactions-----------------------------------------

# transaction wrapper
# returns:
#   - False if something went wrong
#   - True if the action has no return value specified and no exception occured
# expects the actiooon to return a class object of type Result!!!
def InTransaction(tranny, action):
    returnvalue = res.Result()
    try:
        tranny.Start()
        try:
            trannyResult = action()
            tranny.Commit()
            # check what came back
            if (trannyResult != None):
                # store false value 
                returnvalue = trannyResult
        except Exception as e:
            tranny.RollBack()
            returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

#--------------------------------------------string-----------------------------------------

#encode string as ascii and replaces all non ascii characters
def EncodeAscii (string):
    return string.encode('ascii','replace')
