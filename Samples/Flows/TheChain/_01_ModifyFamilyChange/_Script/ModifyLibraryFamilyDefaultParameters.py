'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is used to make changes to families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The changes made to families do not require any further input (from another script / text file):

- Purge unused (requires Autodesk eTransmit)
- Purge unused sub categories
- purge unused line patterns
- purge unused shared parameter definitions

- Saves marker files:
    - to help copy family back to origin in post process
    - change family log which can be used is reload advanced flows

'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# ---------------------------
# default file path locations
# ---------------------------

import clr
import System

import utilModifyBVN as utilR # sets up all commonly used variables and path locations!
# import common library

import Result as res
import RevitCommonAPI as com
import Utility as util

import RevitSharedParameterSwap as rSharedParaSwap
import RevitSharedParameters as rSharedP
import RevitSharedParameterAdd as rSharedPAdd
import RevitSharedParametersTuple as rSharedParaTuple
import RevitFamilyParameterUtils as rFamParaUtils

from Autodesk.Revit.DB import *



# ----------------------------------------------------- default family actions ------------------------------------------
def _getFamilyParameters(doc):
    '''
    Gets all family parameters.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :raises Exception: "Document is not a family document." when a non family document is passt in.
    
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

def ChangeParamterToFamilyParameter(doc):
    '''
    Changes shared parameters to family parameters based on text file in \_Input folder

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if change of shared parameters to family parameters was successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnvalue = res.Result()
    #  dictionary used to change shard parameters to family parameters
    parameterMapper = {}
    returnvalue.AppendMessage('Changing shared parameters to family parameters...start')
    # parameter change directives
    try:
        fileData = util.ReadCSVfile(utilR.CHANGE_SHARED_PARAMETER_TO_FAMILY_PARAMETER_PATH)
        if(len(fileData) > 0):
            for row in fileData:
                if(len(row) > 1):
                    parameterMapper[row[0]] = row[1]# get the family manager
        else:
            returnvalue.UpdateSep(False, 'No shared parameter change directives file found ot file is empty.')
    except Exception as e:
        returnvalue.UpdateSep(False, 'No shared parameter change directives file found.')

    #a match wass found
    matchFound = False
    #check if any change directives where found
    if(len(parameterMapper)>0):
        manager = doc.FamilyManager
        # get family parameters
        paras = _getFamilyParameters(doc)
        # check whether any parameter in family requires changing
        for p in paras:
            if (p.Definition.Name in parameterMapper):
                # update flage
                matchFound = True
                # save the old name
                paraOldName = p.Definition.Name
                # define action to change shared parameter to family parameter
                def action():
                    returnvalueTranny = res.Result()
                    try:
                        manager.ReplaceParameter(p, parameterMapper[p.Definition.Name], p.Definition.ParameterGroup, p.IsInstance)
                        returnvalueTranny.UpdateSep(True, 'Successfully changed parameter ' + paraOldName + ' to a family parameter: '+ parameterMapper[paraOldName])
                    except Exception as e:
                        returnvalueTranny.UpdateSep(False, 'Failed to change parameter ' + paraOldName + ' to a family parameter with exception: '+ str(e))
                    return returnvalueTranny
                # put everythin in a transaction
                transaction = Transaction(doc, "change to family parameter "+ paraOldName)
                result = com.InTransaction(transaction, action)
                returnvalue.Update(result)
                if(result.status):
                    # delete shared parameter definition:
                    sharedParas = rSharedP.GetAllSharedParameters(doc)
                    for sp in sharedParas:
                        if(sp.Name == paraOldName):
                            resultDelete = com.DeleteByElementIds(doc, [sp.Id], 'deleting: '+ paraOldName, 'shared parameter')
                            returnvalue.Update(resultDelete)
                            break
    else:
        returnvalue.UpdateSep(False, 'No shared parameter change directives where found.')
    if(matchFound == False):
        returnvalue.UpdateSep(False, 'No matching shared parameter(s) where found in family.')
    return returnvalue


def DeleteUnwantedSharedParameters(doc):
    '''
    Deletes all shared paras in a project file flaged as unwanted
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if deleting unwated shared parameters was successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnvalue = res.Result()
    returnvalue.AppendMessage('Deleting unwanted shared parameters...start')
    try:
        # read data file
        fileData = util.ReadCSVfile(utilR.DELTETE_SHARED_PARAMETER_LIST_FILE_PATH)
        guidsToDelete = []
        for row in fileData:
            if(len(row) > 1):
                if(len(row[1]) == 36):
                    guidsToDelete.append(row[1])
            else:
                returnvalue.UpdateSep(False,'Shared parameter file contains malformed row: ' + str(row))
    except Exception as e:
        returnvalue.UpdateSep(False, 'No unwanted shared parameter file found.')
    # go ahaed and delete...
    if(len(guidsToDelete) > 0):
        resultDelete = rSharedP.DeleteSharedParameters(doc, guidsToDelete)
        returnvalue.Update(resultDelete)
    else:
        returnvalue.UpdateSep(False, "No valid GUIDS found in guid data file: " + utilR.DELTETE_SHARED_PARAMETER_LIST_FILE_PATH)
    return returnvalue


def SwapSharedParameters(doc):
    '''
    Swaps out shared parameters as per directive

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status. True if swapping shared parameters was successful, otherwise False.
        - result.message be generic success message.
        - result.result  list of new shared parameters
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnvalue = rSharedParaSwap.SwapSharedParameters(doc, utilR.SWAP_SHARED_PARAMETER_DIRECTIVE_PATH)
    return returnvalue


# shared parameter file path
sharedParameterFilePathRename_ = r'\\bvn\data\studio\SharedAssets\Revit\RevitContent\CentralHealthLibrary\05 Python\Shared_Parameters_Renaming.txt'
sharedParameterFilePathIFC_ = r"\\bvn\data\studio\SharedAssets\Revit\RevitContent\CentralHealthLibrary\05 Python\IFC Shared Parameters.txt"

todaysDate_ = util.GetFileDateStamp()
# tuple containing the shared parameters to be added
sharedParametersToAdd_= {
    'CreatedByURL_ANZRS' : [rSharedParaTuple.parameterData('CreatedByURL_ANZRS', True, BuiltInParameterGroup.PG_IDENTITY_DATA), '', 'www.bvn.com.au', sharedParameterFilePathRename_],
    'CreatedBy_ANZRS' : [rSharedParaTuple.parameterData('CreatedBy_ANZRS', True, BuiltInParameterGroup.PG_IDENTITY_DATA), '"BVN"' ,'', sharedParameterFilePathRename_],
    'ModifiedIssue_ANZRS' : [rSharedParaTuple.parameterData('ModifiedIssue_ANZRS', True, BuiltInParameterGroup.PG_IDENTITY_DATA), '"' + todaysDate_ + '"','', sharedParameterFilePathRename_],
    'IfcExportType': [rSharedParaTuple.parameterData('IfcExportType', False, BuiltInParameterGroup.PG_IFC), '','', sharedParameterFilePathRename_],
    'IfcExportAs': [rSharedParaTuple.parameterData('IfcExportAs', False, BuiltInParameterGroup.PG_IFC), '','', sharedParameterFilePathRename_],
    'IfcName[Type]': [rSharedParaTuple.parameterData('IfcName[Type]', False, BuiltInParameterGroup.PG_IFC), '','', sharedParameterFilePathRename_],
    'IfcDescription[Type]': [rSharedParaTuple.parameterData('IfcDescription[Type]', False, BuiltInParameterGroup.PG_IFC), '','', sharedParameterFilePathRename_],
    'IfcTag[Type]': [rSharedParaTuple.parameterData('IfcTag[Type]', False, BuiltInParameterGroup.PG_IFC), '','', sharedParameterFilePathRename_],
    'IfcObjectType[Type]': [rSharedParaTuple.parameterData('IfcObjectType[Type]', True, BuiltInParameterGroup.PG_IFC), '','', sharedParameterFilePathRename_]
}

def AddDefaultParameters(doc, sharedParametersToAdd):
    '''
    Assigns default parameters to family. Refer to list sharedParametersToAdd_.

    Note: if not type is set up in the family, the parameters will be added without values assigned.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sharedParametersToAdd: A dictionary where the key is the parameter name and the value is a list in format: tuple, formula value, value. If formula value is an empty string, the value entry will be assigned to the parameter instead.
    :type sharedParametersToAdd: {str:[tuple, str, str]}

    :return: 
        Result class instance.

        - result.status. True if shared parameters where added successfully, otherwise False.
        - result.message be generic success message.
        - result.result  empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get the family manager
    manager = doc.FamilyManager
    # get a curent type
    familyTypes = manager.Types
    # add parameters and values
    for para in sharedParametersToAdd:
        # load shared para file
        sharedParaDefFile = rSharedPAdd.LoadSharedParameterFile(doc, sharedParametersToAdd[para][3])
        if(sharedParaDefFile!=None):
            # check whether parameter already in family
            famSharedParameter = rSharedP.CheckWhetherSharedParameterByNameIsFamilyParameter(doc, para)
            # if not add it to family
            if(famSharedParameter == None):
                famParaResult = rSharedPAdd.AddSharedParameterToFamily(sharedParametersToAdd[para][0], manager, doc, sharedParaDefFile)
                returnValue.Update(famParaResult)
                if (famParaResult.status):
                    famSharedParameter = famParaResult.result[0]
                else:
                    returnValue.UpdateSep(False, 'Failed to add parameter:  ' + para + ' to family!')
            # add parameter value if at least one type exists
            if(familyTypes.Size > 0):
                # check whether a formula or a value needs to be set
                if(sharedParametersToAdd_[para][1] != '' and famSharedParameter != None):
                    # set formula
                    returnValue.Update(rFamParaUtils.SetParameterFormula(doc, manager, famSharedParameter, sharedParametersToAdd[para][1]))
                elif(sharedParametersToAdd_[para][2] != '' and famSharedParameter != None):
                    # set value
                    returnValue.Update(rFamParaUtils.SetFamilyParameterValue(doc, manager, famSharedParameter, sharedParametersToAdd[para][2])) 
                elif(sharedParametersToAdd_[para][1] == '' and  sharedParametersToAdd_[para][2] == ''):
                    returnValue.AppendMessage('No parameter value provided for parameter:  ' + para )
                else:
                    returnValue.AppendMessage('Failed to add value to parameter:  ' + para )
            else:
                returnValue.AppendMessage('No parameter value set since no type exists in family')
        else:
            returnValue.UpdateSep(False, 'Failed to load shared parameter file.')
    return returnValue
