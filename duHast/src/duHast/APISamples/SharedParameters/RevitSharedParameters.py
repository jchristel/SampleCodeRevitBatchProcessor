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

# import Autodesk
import Autodesk.Revit.DB as rdb


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

