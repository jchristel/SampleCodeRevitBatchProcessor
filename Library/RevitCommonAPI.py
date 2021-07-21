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

#import datetime
import System
import clr
import glob
import Result as res

#from System.IO import Path
from Autodesk.Revit.DB import *
import os.path as path

import Utility as util
import RevitGroups as rGroup

clr.ImportExtensions(System.Linq)


#----------------------------------------parameters-----------------------------------------------

# checks a paramter value based on passed in condition  
def CheckParameterValue(para, paraCondition, conditionValue):
    isMatch = False
    pValue = getParameterValue(para)
    isMatch = paraCondition(util.EncodeAscii(conditionValue), util.EncodeAscii(pValue))
    return isMatch

# returns a parameter value as string
def getParameterValue(para):
    pValue = 'no Value'
    if(para.StorageType == StorageType.ElementId or para.StorageType == StorageType.Double or para.StorageType == StorageType.Integer):
        if(para.AsValueString()!= None and para.AsValueString() != ''):
            pValue = para.AsValueString()
    elif(para.StorageType == StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            pValue = para.AsString()
    return pValue

# sets a parameter value by trying to convert the past in string representing the value into the appropriate value type:
def setParameterValue(para, valueAsString, doc):
    returnvalue = res.Result()
    oldValue = getParameterValue(para)
    transactionName = 'Update to parameter value'
    if(para.StorageType == StorageType.ElementId):
        newId = ElementId(int(valueAsString))
        def action():
            actionReturnValue = res.Result()
            try:
                para.Set(newId)
                actionReturnValue.message = 'Changed parameter value of type Id.[' + para.Definition.Name + '] : '  + oldValue + ' to: ' + valueAsString
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = Transaction(doc,transactionName)
        returnvalue = InTransaction(transaction, action)
    elif(para.StorageType == StorageType.Double):
        # THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in
        # whatever internal units of measure Revit uses. SetValueString expects your value to 
        # be in whatever the current DisplayUnitType (units of measure) the document is set to 
        # for the UnitType associated with the parameter.
        #
        # So SetValueString is basically how the Revit GUI works.
        def action():
            actionReturnValue = res.Result()
            try:
                para.SetValueString(valueAsString)
                actionReturnValue.message = 'Changed parameter value of type double.[' + para.Definition.Name + '] : ' + oldValue + ' to: ' + valueAsString
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = Transaction(doc,transactionName)
        returnvalue = InTransaction(transaction, action)
    elif (para.StorageType == StorageType.Integer):
        def action():
            actionReturnValue = res.Result()
            try:
                para.Set(int(valueAsString))
                actionReturnValue.message = 'Changed parameter value of type integer.[' + para.Definition.Name + '] : ' + oldValue + ' to: ' + valueAsString
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = Transaction(doc,transactionName)
        returnvalue = InTransaction(transaction, action)
    elif (para.StorageType == StorageType.String):
        def action():
            actionReturnValue = res.Result()
            try:
                para.Set(valueAsString)
                actionReturnValue.message = 'Changed parameter value of type string.[' + para.Definition.Name + '] : ' + oldValue + ' to: ' + valueAsString
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
            return actionReturnValue
        transaction = Transaction(doc,transactionName)
        returnvalue = InTransaction(transaction, action)
    else:  
        # dead end
        returnvalue.UpdateSep(False,'Dont know what to do with this storage type: (NONE) '+ str(para.StorageType))
    return returnvalue

# returns the mark value of an element
# e:    the element
# returns 'Can not retrieve mark value!' if an exception occured
def GetElementMark(e):
    mark = ''
    try:
        paraMark = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
        mark = '' if paraMark == None else paraMark.AsString()
    except:
        mark = 'Can not retrieve mark value!'
    return mark
#----------------------------- revisions ----------------

# returns the revision of a sheet by its name
# since multiple sheets can have the same name it will return the revision of the first match...
# default value is '-'
def GetSheetRevByName(doc, sheetName):
    revValue = '-'
    collector = FilteredElementCollector(doc).OfClass(ViewSheet).Where(lambda e: e.Name == sheetName)
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        revP = sheet.get_Parameter(BuiltInParameter.SHEET_CURRENT_REVISION)
        revValue = util.PadSingleDigitNumericString(revP.AsString())
    return revValue

# returns the revision of a sheet by its number
# default value is '-'
def GetSheetRevByNumber(doc, sheetNumber):
    revValue = '-'
    collector = FilteredElementCollector(doc).OfClass(ViewSheet).Where(lambda e: e.SheetNumber == sheetNumber)
    results = collector.ToList()
    if (len(results)>0):
        sheet = results[0]
        revP = sheet.get_Parameter(BuiltInParameter.SHEET_CURRENT_REVISION)
        revValue = revP.AsString()
    return revValue
#----------------------------------------types - Autodesk.Revit.DB ElementType -----------------------------------------------

# doc   current model document
# typeGetter    method needs to accept the current document as argument and need to return a collector of Autodesk.Revit.DB ElementType
def GetSimilarTypeFamiliesByType(doc, typeGetter):
    """returns a list of uniqe types and similar family types in format:
    [[type, similar type id, similar type id,...]]"""
    simTypes=[]
    types = typeGetter(doc)
    for t in types:
        tData = [t]
        sims = t.GetSimilarTypes()
        simData = []
        for sim in sims:
            simData.append(sim)
        tData.append(simData)
        if(CheckUniqueTypeData(simTypes, tData)):
            simTypes.append(tData)
    return simTypes

# existingTypes     list in format [[type, similar type id, similar type id,...]]
# newTypeData       list in format [type, similar type id, similar type id,...] 
def CheckUniqueTypeData(existingTypes, newTypeData):
    """checking whether we have type and associated similar types already
    returns true:
    -if type is not in list existing Types passed in or
    -if ids of similar family types do not match any similar types already in list"""
    result = True
    for s in existingTypes:
        # check for matching family name
        if (s[0].FamilyName == newTypeData[0].FamilyName):
            # check if match has the same amount of similar family types
            # if not it is unique
            if (len(s[1]) == len(newTypeData[1])):
                # assume IDs do match
                matchIDs = True
                for i in range(len(s[1])):
                    if(s[1][i] != newTypeData[1][i]):
                          # id's dont match, this is unique
                          matchIDs = False
                          break
                if(matchIDs):
                    # data is not unique
                    result = False
                    break
    return result

# doc   current model document
# typeGetter: method asccepting current document as argument and returning a collector of types in model
# instanceGetter: method asccepting current document as argument and returning a list of instances in model
def GetUnusedTypeIdsInModel(doc, typeGetter, instanceGetter):
    """returns ID of unused family types in the model"""
    # get all  types available and associated family types
    familTypesAvailable = GetSimilarTypeFamiliesByType(doc, typeGetter)
    # get used type ids
    usedFamilyTypeIds = instanceGetter(doc)
    # loop over avaiable types and check which one is used
    for vt in familTypesAvailable:
        # remove all used family type Id's from the available list...
        # whatever is left can be deleted if not last available item in list for type
        # there should always be just one match
        for usedfamilyTypeId in usedFamilyTypeIds:
                # get the index of match
                index = util.IndexOf(vt[1],usedfamilyTypeId)
                # remove used item from list
                if (index > -1):
                   vt[1].pop(index) 
    # filter these by family types where is only one left
    # make sure to leave at least one family type behind, since the last type cannot be deleted
    filteredUnusedTypeIds = []
    for vt in familTypesAvailable:
        if(len(vt[1]) > 1):
            # make sure to leave one behind
            maxLength = len(vt[1]) - 1
            # check whether this can be deleted...
            for x in range(maxLength):
                id = vt[1][x]
                # get the element
                vtFam = doc.GetElement(id)
                if (vtFam.CanBeDeleted):
                    filteredUnusedTypeIds.append(id)
    return filteredUnusedTypeIds

#----------------------------------------instances of types - Autodesk.Revit.DB ElementType -----------------------------------------------

# doc   current document
# getTypes:         available types getter. Needs to accept doc as argument and return a collector of type foo
# getInstances:     placed instances getter. Needs to accept doc as argument and return a collector of instances foo
def GetNotPlacedTypes(doc, getTypes, getInstances):
    """returns a list of unused Types foo by compring type Ids of placed instances with all avialable types"""
    availTypes = getTypes(doc)
    placedInstances = getInstances(doc)
    notPlaced = []
    allreadyChecked = []
    # loop over all types and check for matching instances
    for at in availTypes:
        match = False
        for pi in placedInstances:
            # check if we had this type checked allready, if so ignore and move to next
            if(pi.GetTypeId() not in allreadyChecked):
                #  check for type id match
                if(pi.GetTypeId() == at.Id):
                    # add to allready checked and verified as match list
                    allreadyChecked.append(pi.GetTypeId())
                    match = True
                    break
        if(match == False):
            notPlaced.append(at)
    return notPlaced


# --------------------------------------------- check whether groups contain certain element types - Autodesk.Revit.DB ElementType  ------------------
# doc       current document
# typeIds   types ids to check for matches in group
# group     to check for matching type id
def CheckGroupForTypeIds(doc, groupType, typeIds):
    """Filters passed in list of type ids by type ids found in group and returns list of unmatched Id's
    This only returns valid data if at least one instance of the group is placed in the model, otherwise GetMemberIds() returns empty!!"""
    unusedTypeIds = []
    usedTypeIds = []
    # get the first group from the group type and get its members
    for g in groupType.Groups:
        # get ids of group elements:
        memberIds = g.GetMemberIds()
        # built list of used type ids
        for memberId in memberIds:
            member = doc.GetElement(memberId)
            usedTypeId = member.GetTypeId()
            if (usedTypeId not in usedTypeIds):
                usedTypeIds.append(usedTypeId)
    for checkId in typeIds:
        if(checkId not in usedTypeIds):
            unusedTypeIds.append(checkId)
    return unusedTypeIds

def CheckGroupsForMatchingTypeIds(doc, groupTypes, typeIds):
    """checks all elements in groups passt in whether type Id is matching any type ids passt in
    returns all type ids not matched"""
    for groupType in groupTypes:
        typeIds = CheckGroupForTypeIds(doc, groupType, typeIds)
        # check if all type ids where matched up
        if (len(typeIds) == 0):
            break
    return typeIds

# doc   current document
# typeIds   types ids to check for matches in groups
def GetUnusedTypeIdsFromDetailGroups(doc, typeIds):
    """checks elements in nested detail groups and detail groupd whether their type ID is in the list passt in.
    Returns all type Ids from list passt in not found in group definitions
    This only returns valid data if at least one instance of the group is placed in the model!!"""
    unusedTypeIds = []
    nestedDetailGroups = rGroup.GetNestedDetailGroups(doc)
    detailGroups = rGroup.GetDetailGroups(doc)
    unusedTypeIds = CheckGroupsForMatchingTypeIds(doc, nestedDetailGroups, typeIds)
    unusedTypeIds = CheckGroupsForMatchingTypeIds(doc, detailGroups, typeIds)
    return unusedTypeIds

#----------------------------------------elements-----------------------------------------------

# transactionName : name the transaction will be given
# elementName: will appear in description of what got deleted
def DeleteByElementIds(doc, ids, transactionName, elementName):
    """method deleting elements by list of element id's"""
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

# transactionName : name the transaction will be given
# elementName: will appear in description of what got deleted
def DeleteByElementIdsOneByOne(doc, ids, transactionName, elementName):
    """method deleting elements by list of element id's one at the time"""
    returnvalue = res.Result()
    for id in ids:
        def action():
            actionReturnValue = res.Result()
            element = doc.GetElement(id)
            n = Element.Name.GetValue(element)
            try:
                doc.Delete(id)
                actionReturnValue.message = 'Deleted ' + str(len(ids)) + ' ' + n
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to delete ' + n + '[' +str(id) + '] with exception: ' + str(e))
            return actionReturnValue
        transaction = Transaction(doc,transactionName)
        returnvalue.Update( InTransaction(transaction, action))
    return returnvalue

#-------------------------------------------------------file IO --------------------------------------
# synchronises a Revit central file
# doc: the document to be synced
# compactCentralFile: option to compact the central file ... default is False (no compacting)
# returns:
#   - true if sync without exception been thrown
#   - false if an exception occured
def SyncFile (doc, compactCentralFile = False):
    returnvalue = res.Result()
    # set up sync settings
    ro = RelinquishOptions(True)
    transActOptions = TransactWithCentralOptions()
    sync = SynchronizeWithCentralOptions()
    sync.Comment = 'Synchronised by Revit Batch Processor'
    sync.Compact = compactCentralFile
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
    revitFileName = util.GetFileNameWithoutExt(currentFullFileName)
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
