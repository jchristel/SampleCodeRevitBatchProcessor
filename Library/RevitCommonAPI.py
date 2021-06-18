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
