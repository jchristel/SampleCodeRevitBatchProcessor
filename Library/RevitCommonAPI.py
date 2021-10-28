#!/usr/bin/python
# -*- coding: utf-8 -*-
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
    try:
        if(para.StorageType == StorageType.Double or para.StorageType == StorageType.Integer):
            if(para.AsValueString()!= None and para.AsValueString() != ''):
                pValue = para.AsValueString()
        elif(para.StorageType == StorageType.String):
            if(para.AsString() != None and para.AsString() != ''):
                pValue = para.AsString()
        elif(para.StorageType == StorageType.ElementId):
            if(para.AsElementId() != None):
                pValue = para.AsElementId()
    except  Exception as e:
        pValue = 'Exception: '+str(e)
    return pValue

# para      revit parameter to get value of
def GetParameterValueUTF8String(para):
    """ returns parameter values as utf-8 encoded strings"""
    pValue = 'no Value'
    if(para.StorageType == StorageType.Double or para.StorageType == StorageType.Integer):
        if(para.AsValueString()!= None and para.AsValueString() != ''):
            pValue = para.AsValueString().encode('utf-8')
    elif(para.StorageType == StorageType.String):
        if(para.AsString() != None and para.AsString() != ''):
            pValue = para.AsString().encode('utf-8')
    elif(para.StorageType == StorageType.ElementId):
        if(para.AsElementId() != None):
            pValue = str(para.AsElementId()).encode('utf-8')
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
                actionReturnValue.message = 'Changed parameter value of type Id.[' + para.Definition.Name + '] : '  + str(oldValue) + ' to: ' + valueAsString
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
                actionReturnValue.message = 'Changed parameter value of type double.[' + para.Definition.Name + '] : ' + str(oldValue) + ' to: ' + valueAsString
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
                actionReturnValue.message = 'Changed parameter value of type integer.[' + para.Definition.Name + '] : ' + str(oldValue) + ' to: ' + valueAsString
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

#----------------------------------------Legend Components -----------------------------------------------

# typeIds       types to check whether they have been placed as legend components
# doc           current model document
def GetLegendComponentsInModel(doc, typeIds):
    """ returns all type ids which have been placed as legend components"""
    ids = []
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LegendComponents)
    for c in col:
        paras = c.GetOrderedParameters()
        for p in paras:
            if (p.Definition.BuiltInParameter == BuiltInParameter.LEGEND_COMPONENT):
                id = com.getParameterValue(p)
                if (id in typeIds and id not in ids):
                    ids.append(id)
                break
    return ids

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
        # simData.sort() # not sure a sort is actually doing anything
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
    # flag indicating that at leat one type was removed from list because it is in use
    # this flag used when checking how many items are left...
    removedAtLeastOne = []
    # set index to 0, type names might not be unique!!
    counter = 0
    # loop over avaiable types and check which one is used
    for t in familTypesAvailable:
        # remove all used family type Id's from the available list...
        # whatever is left can be deleted if not last available item in list for type
        # there should always be just one match
        for usedfamilyTypeId in usedFamilyTypeIds:
            # get the index of match
            index = util.IndexOf(t[1],usedfamilyTypeId)
            # remove used item from list
            if (index > -1):
                t[1].pop(index)
                if(t not in removedAtLeastOne):
                    removedAtLeastOne.append(counter)
        counter = counter + 1
    # filter these by family types where is only one left
    # make sure to leave at least one family type behind, since the last type cannot be deleted
    filteredUnusedTypeIds = []
    # reset index
    counter = 0
    for t in familTypesAvailable:
        if (counter in removedAtLeastOne):
            # at least one item was already removed from list...so all left over ones can be purged
            for id in t[1]:
                # get the element
                tFam = doc.GetElement(id)
                if (tFam.CanBeDeleted):
                    filteredUnusedTypeIds.append(id)
        else:
            # need to keep at least one item
            if(len(t[1]) > 1):
                #maxLength = len(t[1])
                # make sure to leave the first one behind to match Revit purge behaviour
                for x in range(1, len(t[1])):
                    id = t[1][x]
                    # get the element
                    tFam = doc.GetElement(id)
                    # check whether this can be deleted...
                    if (tFam.CanBeDeleted):
                        filteredUnusedTypeIds.append(id)
        counter = counter + 1 
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

# doc           current document
# groupType     group to be checked whether it contains elements of types passt in
# typeIds       list of type ids to confirm whether they are in use a group
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

# doc           current model document
# elementIds    elements of which to build a dictionary by category
def BuildCategoryDictionary(doc, elementIds):
    dic = {}
    for elId in elementIds:
        try:
            el = doc.GetElement(elId)
            try:
                if(dic.has_key(el.Category.Name)):
                    dic[el.Category.Name].append(el)
                else:
                    dic[el.Category.Name] = [el]
            except:
                if(dic.has_key('invalid category')):
                    dic['invalid category'].append(el)
                else:
                    dic['invalid category'] = [el]
        except:
            if(dic.has_key('invalid element')):
                dic['invalid element'].append(el)
            else:
                dic['invalid element'] = [el]
    return dic

# doc           current model document
# elementIds    dependent elements of which to  check whether orphaned legend components
def CheckWhetherDependentElementsAreMultipleOrphanedLegendComponents (doc, elementIds):
    """ returns True if all but one dependent element are orphaned legend components"""
    flag = True
    categoryName = 'Legend Components'
    # build dependent type dictionary
    # check whether dictionary is made of
    #   1 entry for type
    #   multiple entries for legend components
    #   no other entry
    # if so: check whether any of the legend component entry has a valid view id
    #   if none has return true, otherwise return false
    dic = BuildCategoryDictionary(doc,  elementIds)
    # check if dictioanry has legend component key first up
    if(dic.has_key(categoryName) == True):
        # if so check number of keys and length of elements per key
        if(len(dic.keys()) == 2  and len(dic[categoryName]) == len(elementIds)-1):
            # this should be the only code path returning true...
            for value in dic[categoryName]:
                if value.OwnerViewId != ElementId.InvalidElementId:
                    flag = False
                    break
        else:
            flag = False
    else:
        flag = False
    return flag

# doc                 current model document
# dependentElements   list of elements ids               
def FilterOutWarnings(doc, dependentElements):
    """attempts to filter out any warnings from ids supplied by checking the workset name
    of each element for 'Reviewable Warnings'"""
    ids = []
    for id in dependentElements:
        el = doc.GetElement(id)
        paras = el.GetOrderedParameters()
        isWarning = False
        for p in paras:
            if(p.Definition.BuiltInParameter == BuiltInParameter.ELEM_PARTITION_PARAM):
                if (getParameterValue(p) == 'Reviewable Warnings'):
                    isWarning = True
                break
        if(isWarning == False):
            ids.append(id)
    return ids

# doc   current model document
# el    the element of which to check for dependent elements
# filter  what type of dependent elements to filter, Default is None whcih will return all dependent elements
# threshold   once there are more elements depending on element passed in then specified in threshold value it is deemed that other elements 
#             are dependent on this element (stacked walls for instance return as a minimum 2 elements: the stacked wall type and the legend component
#             available for this type
def HasDependentElements(doc, el, filter = None, threshold = 2):
    """ returns 0 for no dependent elements, 1, for other elements depend on it, -1 if an exception occured"""
    value = 0 # 0: no dependent Elements, 1: has dependent elements, -1 an exception occured
    try:
        dependentElements = el.GetDependentElements(filter)
        # remove any warnings from dependent elements
        dependentElements = FilterOutWarnings(doc, dependentElements)
        # check if dependent elements pass threshold value
        if(len(dependentElements)) > threshold :
            # there appear to be situations where dependent elements are multiple (orphaned?) legend components only
            # or warnings belonging to a type (same type mark ...)
            # these are legend components with an invalid OwnerViewId, check whether this is the case...
            if (CheckWhetherDependentElementsAreMultipleOrphanedLegendComponents(doc, dependentElements) == False):
                value = 1
    except Exception as e:
        value = -1
    return value

# doc             current document
# useTyep         0, no dependent elements; 1: has dependent elements
# typeIdGetter    list of type ids to be checked for dependent elements
def GetUsedUnusedTypeIds(doc, typeIdGetter, useType = 0, threshold = 2):
    # get all types elements available
    allTypeIds = typeIdGetter(doc)
    ids = []
    for typeId in allTypeIds:
        type = doc.GetElement(typeId)
        hasDependents = HasDependentElements(doc, type, None, threshold)
        if(hasDependents == useType):
            ids.append(typeId)
    return ids

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
                actionReturnValue.message = 'Deleted [' + str(id) + '] ' + n
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to delete ' + n + '[' +str(id) + '] with exception: ' + str(e))
            return actionReturnValue
        transaction = Transaction(doc,transactionName)
        returnvalue.Update( InTransaction(transaction, action))
    return returnvalue

# col    element collector
def GetIdsFromElementCollector(col):
    """ this will return a list of all element ids in collector """
    ids = []
    for c in col:
        ids.append(c.Id)
    return ids

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
