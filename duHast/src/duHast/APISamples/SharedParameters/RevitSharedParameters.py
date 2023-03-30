'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit shared parameters.
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
import System

# import common library modules
from duHast.APISamples import RevitCommonAPI as com
from duHast.Utilities import Result as res
from duHast.APISamples import RevitTransaction as rTran
from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: headers used in reports
REPORT_SHAREDPARAMETERS_HEADER = ['HOSTFILE', 'GUID', 'ID', 'NAME', 'PARAMETERBINDINGS']

# --------------------------------------------- utility functions ------------------

def GetAllSharedParameters(doc):  
    '''
    Gets all shared parameters in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing shared parameter elements
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.SharedParameterElement)
    return collector

def GetFamilySharedParameters(doc):
    '''
    Gets all family parameters which are shared parameters.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :raises Exception: "Document is not a family document." when a non family document is past in.
    
    :return: A list of family parameters 
    :rtype: [Autodesk.Revit.DB.FamilyParameter]
    '''

    if(doc.IsFamilyDocument):
        famManager = doc.FamilyManager
        sharedFamParas = []
        for famPara in  famManager.GetParameters():
            try:
                # only shared parameters hav .GUID property...
                if(str(famPara.GUID) != ''):
                    sharedFamParas.append(famPara)
            except Exception as e:
                pass
    else:
        raise Exception("Document is not a family document.")
    return sharedFamParas

def GetFamilyParameters(doc):
    '''
    Gets all family parameters.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :raises Exception: "Document is not a family document." when a non family document is past in.
    
    :return: A list of family parameters 
    :rtype: [Autodesk.Revit.DB.FamilyParameter]
    '''

    if(doc.IsFamilyDocument):
        famManager = doc.FamilyManager
        sharedFamParas = []
        for famPara in  famManager.GetParameters():
            sharedFamParas.append(famPara)
    else:
        raise Exception("Document is not a family document.")
    return sharedFamParas

# ------------------------------------------------------- parameter utilities --------------------------------------------------------------------

def CheckWhetherSharedParametersAreInFile(doc, parameterGUIDs):
    '''
    Filters the past in list of shared parameter GUIDs by using the shared parameters in the document.
        Only parameter in both will be returned.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterGUIDs: list of shared parameter GUIDs as string values
    :type parameterGUIDs: list str
    
    :return: list of shared parameter GUIDs as string values
    :rtype: list str
    '''

    filteredGUIDs = []
    paras = GetAllSharedParameters(doc)
    for p in paras:
        if(p.GuidValue.ToString() in parameterGUIDs):
            filteredGUIDs.append(p.GuidValue.ToString())
    return filteredGUIDs

def CheckWhetherSharedParameterByNameIsFamilyParameter(doc, parameterName):
    '''
    Checks, by name, whether a shared parameter exists as a family parameter in a family.

    param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterName: The name of the parameter.
    :type parameterName: str

    :return: A family parameter if match was found, otherwise None
    :rtype: Autodesk.Revit.DB.FamilyParameter
    '''

    para = None
    paras = GetFamilyParameters(doc)
    for famPara in paras:
        if(famPara.Definition.Name == parameterName):
            try:
                # only shared parameters hav .GUID property...
                if(str(famPara.GUID) != ''):
                    para = famPara
                    break
            except Exception as e:
                pass
    return para

def IsSharedParameterDefinitionUsed(doc, sharedPara):
    '''
    Tests if a shared parameter GUID is used by a family parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sharedPara: A shared parameter
    :type sharedPara: Autodesk.Revit.DB.SharedParameterElement

    :return: True is match is found, otherwise False
    :rtype: bool
    '''

    famSharedParas = GetFamilySharedParameters(doc)
    match = False
    for famSharedPara in famSharedParas:
        if(famSharedPara.GUID == sharedPara.GuidValue):
            match = True
            break
    return match

def GetUnusedSharedParameterDefinitions(doc):
    '''
    Returns all unused shard parameter definitions in a family document.

    Note: These shared parameters might be used in any nested family!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of shared parameters 
    :rtype: [Autodesk.Revit.DB.SharedParameterElement]
    '''

    famSharedParas = GetFamilySharedParameters(doc)
    sharedParas = GetAllSharedParameters(doc)
    unusedSharedParameterDefinition = []
    for sharedPara in sharedParas:
        match = False
        for famSharedPara in famSharedParas:
            if(famSharedPara.GUID == sharedPara.GuidValue):
                match = True
                break
        if(match == False):
            unusedSharedParameterDefinition.append(sharedPara)
    return unusedSharedParameterDefinition

def GetSharedParameterDefinition(parameterName, defFile):
    '''
    Returns a shared parameter definition from a shared parameter file.

    :param parameterName: The shared parameter name.
    :type parameterName: str
    :param defFile: The shared parameter file definition.
    :type defFile: Autodesk.Revit.DB.DefinitionFile

    :return: The shared parameter definition. None if no parameter with a matching name was found.
    :rtype: Autodesk.Revit.DB.ExternalDefinition
    '''

    parameterDefinition = None
    try:
        # loop through parameters and try to find matching one 
        # loop through all definition groups
        for group in defFile.Groups:
            # loop through para's within definition group
            for defPara in group.Definitions:
                # check whether this is the parameter we are after
                if (defPara.Name == parameterName):
                    # match and out
                    parameterDefinition = defPara
                    break
            if(parameterDefinition != None):
                break
    except Exception as e:
        pass
    return parameterDefinition

# ------------------------------------------------------- parameter utilities - delete --------------------------------------------------------------------


def DeleteSharedParameterByName(doc, sharedParameterName):
    '''
    Deletes a single shared parameter based on a name provided.

    param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sharedParameterName: The name of the shared parameter.
    :type sharedParameterName: str

    :return: 
        Result class instance.

        - Parameter delete status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter.
        - result.status will be an empty list.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    paras = GetAllSharedParameters(doc)
    deleteIds = []
    parameterName = 'Unknown'
    for p in paras:
        if(p.Name == sharedParameterName):
            deleteIds.append(p.Id)
            # there should just be one match
            parameterName = util.EncodeAscii(rdb.Element.Name.GetValue(p))
            break
    if(len(deleteIds) > 0):
        returnValue = com.DeleteByElementIds(doc, deleteIds, 'Delete Shared Parameter' , parameterName)
    else:
        returnValue.UpdateSep(False, 'parameter with guid: ' + sharedParameterName + ' does not exist in file.')
    return returnValue

def DeleteSharedParameterByGUID(doc, guid):
    '''
    Deletes a single shared parameter based on a guid provided.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param guid: A shared parameter GUID as string.
    :type guid: str
    
    :return: 
        Result class instance.

        - Parameter delete status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter.
        - result.status will be an empty list.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    paras = GetAllSharedParameters(doc)
    deleteIds = []
    parameterName = 'Unknown'
    for p in paras:
        if(p.GuidValue.ToString() == guid):
            deleteIds.append(p.Id)
            # there should just be one match
            parameterName = util.EncodeAscii(rdb.Element.Name.GetValue(p))
            break
    if(len(deleteIds) > 0):
        returnValue = com.DeleteByElementIds(doc, deleteIds, 'Delete Shared Parameter' , parameterName)
    else:
        returnValue.UpdateSep(False, 'parameter with guid: ' + guid + ' does not exist in file.')
    return returnValue

def DeleteSharedParameters(doc, parameterGUIDs):
    '''
    Deletes shared parameters by GUID from document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterGUIDs: List of shared parameter GUIDs as string.
    :type parameterGUIDs: list str

    :return: 
        Result class instance.

        - Parameter deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter deleted.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    oneGotDeleted = False
    deleteGUIDs = CheckWhetherSharedParametersAreInFile(doc, parameterGUIDs)
    if(len(deleteGUIDs) > 0):
        for deleteGuid in  deleteGUIDs:
            deleteStatus = DeleteSharedParameterByGUID(doc, deleteGuid)
            # preserve TRUE value!
            if(deleteStatus.status == True):
                oneGotDeleted = True
            returnValue.Update(deleteStatus)
        returnValue.UpdateSep(oneGotDeleted, 'Finished deleting parameters!')
    else:
        returnValue.UpdateSep(True, 'No matching shared parameters in file!')

    return returnValue

# ------------------------------------------------------- parameter utilities - change parameter type --------------------------------------------------------------------

def ChangeSharedParameterToFamilyParameter(doc, parameterName, prefix = '_'):
    '''
    Changes a shared family parameter to a standard family parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterName: The shared parameter name.
    :type parameterName: str
    :param prefix: Revit requires the new parameter to have a different name to the shard parameter, therefore a prefix to the name is applied, defaults to '_'
    :type prefix: str, optional
    
    :return: 
        Result class instance.

        - Parameter change status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter and the new family parameter name.
        - result.status will contain the new family parameter.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get the family manager
    manager = doc.FamilyManager
    # get family parameters
    paras = GetFamilyParameters(doc)
    # flag
    changedParameter = False
    # check whether any parameter in family requires changing
    for p in paras:
        if (p.Definition.Name == parameterName):
            paraOldName = p.Definition.Name
            def action():
                actionReturnValue = res.Result()
                try:

                    parameterNew = manager.ReplaceParameter(
                        p, 
                        prefix + paraOldName, 
                        p.Definition.ParameterGroup, 
                        p.IsInstance
                        )
                    
                    actionReturnValue.UpdateSep(True, paraOldName + ': Successfully changed shared parameter to family parameter: ' + prefix + paraOldName)
                    actionReturnValue.result.append(parameterNew)
                except Exception as e:
                    actionReturnValue.UpdateSep(False, paraOldName + ': Failed to change shared parameter to family parameter: ' + str(e))
                return actionReturnValue
            transaction = rdb.Transaction(doc, "change to family parameter")
            returnValue = rTran.in_transaction(transaction, action)
            changedParameter = returnValue.status
    if(changedParameter == False):
        returnValue.status = False
        returnValue.message = 'No parameter matching: ' + parameterName + ' was found. No shared parameter was changed.'
    return returnValue


def ChangeFamilyParameterToSharedParameter(doc, parameterName, parameterData, parameterDef):
    '''
    Changes a family parameter to a shared parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterName: The family parameter name.
    :type parameterName: str
    :param parameterData: A named tup[le containing the shared parameter information
    :type parameterData: RevitSharedParametersTuple.parameterData
    :param parameterDef: The external definition of the shared parameter.
    :type parameterDef: Autodesk.Revit.DB.ExternalDefinition

    :return: 
        Result class instance.

        - Parameter change status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the family parameter and the new shared parameter name.
        - result.status will contain the new shared parameter.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get the family manager
    manager = doc.FamilyManager
    # get family parameters
    paras = GetFamilyParameters(doc)
    # flag
    changedParameter = False
    # check whether any parameter in family requires changing
    for p in paras:
        if (p.Definition.Name  == parameterName):
            def action():
                actionReturnValue = res.Result()
                try:
                
                    parameterNew = manager.ReplaceParameter(
                        p,
                        parameterDef,
                        parameterData.builtInParameterGroup,
                        parameterData.isInstance
                        )
                    
                    actionReturnValue.UpdateSep(True, parameterName+': Changed family parameter to shared parameter: ' + parameterData.name)
                    actionReturnValue.result.append(parameterNew)
                except Exception as e:
                    actionReturnValue.UpdateSep(False, parameterName+': Failed to change family parameter to shared parameter.')
                return actionReturnValue
            transaction = rdb.Transaction(doc, "change to shared parameter")
            returnValue = rTran.in_transaction(transaction, action)
            changedParameter = returnValue.status
    if(changedParameter == False):
        returnValue.status = False
        returnValue.message = 'No parameter matching: ' + parameterName + ' was found. No family parameter was changed.'   
    return returnValue

# ------------------------------------------------------- parameter reporting --------------------------------------------------------------------

def ParamBindingExists(doc, paramName, paramType):
    '''
    Gets all parameter bindings for a given parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param paramName: The name of the parameter.
    :type paramName: str
    :param paramType: The parameter type. (Area, vs text vs... (deprecated in Revit 2022!)
    :type paramType: Autodesk.Revit.DB.ParameterType

    :return: List of categories a parameter is attached to.
    :rtype: list of str
    '''

    categories = []
    map = doc.ParameterBindings
    iterator = map.ForwardIterator()
    iterator.Reset()
    while iterator.MoveNext():
        if iterator.Key != None and iterator.Key.Name == paramName and iterator.Key.ParameterType == paramType:
            elemBind = iterator.Current
            for cat in elemBind.Categories:
                categories.append(cat.Name)
            break
    return categories

def GetSharedParameterReportData(doc, revitFilePath):
    '''
    Gets shared parameter data ready for being printed to file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str

    :return: list of list of parameter properties.
    :rtype: list of list of str
    '''

    data = []
    paras = GetAllSharedParameters(doc)
    for p in paras:
        parameterDefinition = p.GetDefinition()
        parameterBindings = []
        # parameter bindings do not exist in a family document
        if(doc.IsFamilyDocument == False):
            parameterBindings = ParamBindingExists(doc, rdb.Element.Name.GetValue(p), parameterDefinition.ParameterType)
        
        # just in case parameter name is not unicode
        parameterName = 'unknown'
        try:   
            parameterName = util.EncodeAscii(rdb.Element.Name.GetValue(p))
        except Exception as ex:
            parameterName = 'Exception: ' + str(ex)
        # build data
        data.append([
            revitFilePath, 
            p.GuidValue.ToString(), 
            str(p.Id.IntegerValue), 
            parameterName,
            str(parameterBindings)
            ])
    return data