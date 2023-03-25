'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of helper functions relating to Revit worksets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

import System

# import common library modules
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res
from duHast.APISamples import RevitTransaction as rTran
from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_WORKSETS_HEADER = ['HOSTFILE','ID', 'NAME', 'ISVISIBLEBYDEFAULT']

# --------------------------------------------- utility functions ------------------

def GetWorksetIdByName(doc, worksetName):
    '''
    Returns the element id of a workset identified by its name, otherwise invalid Id (-1) if no such workset exists

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param worksetName: The name of the workset of which to retrieve the Element Id
    :type worksetName: str
    
    :return: The workset element id, otherwise invalid Id (-1) if no such workset exists
    :rtype: Autodesk.Revit.DB.ElementId
    '''

    id = rdb.ElementId.InvalidElementId
    for p in rdb.FilteredWorksetCollector(doc).OfKind(rdb.WorksetKind.UserWorkset):
        if(p.Name == worksetName):
            id = p.Id
            break
    return id

def GetWorksetNameById(doc, idInteger):
    '''
    Returns the name of the workset identified by its Element Id, otherwise 'unknown' if no such workset exists

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param idInteger: The element id as integer value.
    :type idInteger: int
    
    :return: The name of the workset identified by its Id, otherwise 'unknown'
    :rtype: str
    '''

    name = 'unknown'
    for p in rdb.FilteredWorksetCollector(doc).OfKind(rdb.WorksetKind.UserWorkset):
        if(p.Id.IntegerValue == idInteger):
            name = p.Name
            break
    return name

def GetWorksetIds(doc):
    '''
    Gets all ids of all user defined worksets in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of all user defined workset element ids
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    id = []
    for p in rdb.FilteredWorksetCollector(doc).OfKind(rdb.WorksetKind.UserWorkset):
      id.append(p.Id)
    return id

def GetWorksets(doc):
    '''
    Returns all user defined worksets in the model as list.

    Will return a list of zero length if no worksets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of worksets
    :rtype: list of Autodesk.Revit.DB.Workset
    '''

    worksets = rdb.FilteredWorksetCollector(doc).OfKind(rdb.WorksetKind.UserWorkset).ToList()
    return worksets

def GetWorksetsFromCollector(doc):
    '''
    Returns all user defined worksets in the model as collector.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered elements collector of user defined worksets
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredWorksetCollector(doc).OfKind(rdb.WorksetKind.UserWorkset)
    return collector

def OpenWorksetsWithElementsHack(doc):
    '''
    This is based on a hack from the AutoDesk forum and an article from the building coder:

    - https://forums.autodesk.com/t5/revit-api-forum/open-closed-worksets-in-open-document/td-p/6238121
    - https://thebuildingcoder.typepad.com/blog/2018/03/switch-view-or-document-by-showing-elements.html

    this method will open worksets in a model containing elements only

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    '''

    # get worksets in model
    worksetIds = GetWorksetIds(doc)
    # loop over workset and open if anything is on them
    for wId in worksetIds:
        workset = rdb.ElementWorksetFilter(wId)
        elemIds = rdb.FilteredElementCollector(doc).WherePasses(workset).ToElementIds()
        if (len(elemIds)>0):
            # this will force Revit to open the workset containing this element
           rdb.uidoc.ShowElements(elemIds.First())

def ModifyElementWorkset(doc, defaultWorksetName, collector, elementTypeName):
    '''
    Attempts to change the worksets of elements provided through an element collector.

    Will return false if target workset does not exist in file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param defaultWorksetName: The name of the workset the elements are to be moved to.
    :type defaultWorksetName: str
    :param collector: The element collector containing the elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param elementTypeName: A description used in the status message returned.
    :type elementTypeName: str
    
    :return: 
        Result class instance.
        
        - .result = True if successfully moved all elements to new workset. Otherwise False.
        - .message will contain stats in format [success :: failure]
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    returnValue.message = 'Changing ' + elementTypeName + ' workset to '+ defaultWorksetName
    # get the ID of the default grids workset
    defaultId = GetWorksetIdByName(doc, defaultWorksetName)
    counterSuccess = 0
    counterFailure = 0
    # check if invalid id came back..workset no longer exists..
    if(defaultId != rdb.ElementId.InvalidElementId):
        # get all elements in collector and check their workset
        for p in collector:
            if (p.WorksetId != defaultId):
                # get the element name
                elementName = 'Unknown Element Name'
                try:
                    elementName = rdb.Element.Name.GetValue(p)
                except Exception :
                    pass
                # move element to new workset
                transaction = rdb.Transaction(doc, "Changing workset: " + elementName)
                trannyStatus = rTran.in_transaction(transaction, GetActionChangeElementWorkset(p, defaultId))
                if (trannyStatus.status == True):
                    counterSuccess += 1
                else:
                    counterFailure += 1
                returnValue.status = returnValue.status & trannyStatus.status
            else:
                counterSuccess += 1
                returnValue.status = returnValue.status & True 
    else:
        returnValue.UpdateSep(False, 'Default workset '+ defaultWorksetName + ' does no longer exists in file!')
    returnValue.AppendMessage('Moved ' + elementTypeName + ' to workset ' + defaultWorksetName + ' [' + str(counterSuccess) + ' :: ' + str(counterFailure) +']')
    return returnValue

def GetActionChangeElementWorkset(el, defaultId):
    '''
    Contains the required action to change a single elements workset

    :param el: The element
    :type el: Autodesk.Revit.DB.Element
    :param defaultId: The workset element Id
    :type defaultId: Autodesk.Revit.DB.ElementId
    '''

    def action():
        actionReturnValue = res.Result()
        try:
            wsParam = el.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
            wsParam.Set(defaultId.IntegerValue)
            actionReturnValue.message = 'Changed element workset.'
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
        return actionReturnValue
    return action

def IsElementOnWorksetById(doc, el, worksetId):
    '''
    Checks whether an element is on a given workset

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param el: The element.
    :type el: Autodesk.Revit.DB.Element
    :param worksetId: The workset element Id
    :type worksetId: Autodesk.Revit.DB.ElementId
    
    :return: True if element is on given workset, otherwise False
    :rtype: bool
    '''

    flag = True
    try:
        wsParam = el.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        currentWorksetName = rParaGet.get_parameter_value(wsParam)
        compareToWorksetName = GetWorksetNameById(doc, worksetId.IntegerValue)
        if(compareToWorksetName != currentWorksetName):
            flag = False
    except Exception as e:
        print (e)
        flag = False
    return flag

def IsElementOnWorksetByName(el, worksetName):
    '''
    Checks whether an element is on a workset identified by name

    :param el: The element
    :type el: Autodesk.Revit.DB.Element
    :param worksetName: The name of the workset
    :type worksetName: str

    :return: True if element is on given workset, otherwise False
    :rtype: bool
    '''

    flag = True
    try:
        wsParam = el.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        currentWorksetName = rParaGet.get_parameter_value(wsParam)
        if(worksetName != currentWorksetName):
            flag = False
    except Exception as e:
        print ("IsElementOnWorksetByName: " + str(e))
        flag = False
    return flag

def GetElementWorksetName(el):
    '''
    Returns the name of the workset an element is on, or 'invalid workset'.

    :param el: The element.
    :type el: Autodesk.Revit.DB.Element
    :return: The name of the workset. If an exception occurred it wil return 'invalid workset'.
    :rtype: str
    '''

    workSetname = 'invalid workset'
    try:
        wsParam = el.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        workSetname = rParaGet.get_parameter_value(wsParam)
    except Exception as e:
        print ("GetElementWorksetName: " + str(e))
    return workSetname

def UpdateWorksetDefaultVisibilityFromReport(doc, reportPath, revitFilePath):
    '''
    Updates the default visibility of worksets based on a workset report file.

    The data for the report files is generated by GetWorksetReportData() function in this module

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param reportPath: The fully qualified file path to tab separated report text file containing workset data.
    :type reportPath: str
    :param revitFilePath: The fully qualified file path of the Revit file. Will be used to identify the file in the report data.
    :type revitFilePath: str

    :return: 
        Result class instance.
        
        - .result = True if:

            - successfully updated all workset default visibility where different to report
            - or none needed updating. 
        
        - Otherwise False:

            - An exception occurred.
            - A workset has no matching data in the report.
        
        - Common:
        
            - .message will contain each workset and whether it needed updating or not
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # read report
    worksetData = util.ReadTabSeparatedFile(reportPath)
    fileName = util.GetFileNameWithoutExt(revitFilePath)
    worksetDataForFile = {}
    for row in worksetData:
        if(util.GetFileNameWithoutExt(row[0]).startswith(fileName) and len(row) > 3):
            worksetDataForFile[row[1]] = util.ParsStringToBool(row[3])
    if(len(worksetDataForFile) > 0): 
        # updates worksets
        worksets = GetWorksets(doc)
        for workset in worksets:
            if(str(workset.Id) in worksetDataForFile):
                if (workset.IsVisibleByDefault != worksetDataForFile[str(workset.Id)]):
                    def action():
                        actionReturnValue = res.Result()
                        defaultVisibility  = rdb.WorksetDefaultVisibilitySettings.GetWorksetDefaultVisibilitySettings(doc)
                        try:
                            defaultVisibility.SetWorksetVisibility(workset.Id, worksetDataForFile[str(workset.Id)])
                            actionReturnValue.UpdateSep(True, workset.Name + ': default visibility settings changed to: \t[' + str(worksetDataForFile[str(workset.Id)]) + ']')
                        except Exception as e:
                            actionReturnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
                        return actionReturnValue
                    # move element to new workset
                    transaction = rdb.Transaction(doc, workset.Name + ": Changing default workset visibility")
                    trannyStatus = rTran.in_transaction(transaction, action)
                    returnValue.Update(trannyStatus)
                else:
                    returnValue.UpdateSep(True, util.EncodeAscii(workset.Name) + ': default visibility settings unchanged.')
            else:
                returnValue.UpdateSep(False, util.EncodeAscii(workset.Name) + ': has no corresponding setting in settings file.')
    else:
        returnValue.UpdateSep(True, 'No settings found for file: ' + fileName)
    return returnValue

# ------------------------------------------------------- workset reporting --------------------------------------------------------------------


def GetWorksetReportData(doc, revitFilePath):
    '''
    Gets workset data ready for being written to file.

    - HOSTFILE
    - ID
    - NAME
    - ISVISIBLEBYDEFAULT

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified file path of Revit file.
    :type revitFilePath: str
    
    :return: The workset data in a nested list of string
    :rtype: list of list of str
    '''

    data = []
    worksets = GetWorksetsFromCollector(doc)
    for ws in worksets:
        data.append([
            revitFilePath, 
            str(ws.Id.IntegerValue), 
            util.EncodeAscii(ws.Name), 
            str(ws.IsVisibleByDefault)])
    return data
