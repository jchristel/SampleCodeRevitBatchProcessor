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
import RevitCommonAPI as com
import Result as res
import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

clr.ImportExtensions(System.Linq)

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

# ------------------------------------------------------- parameter utilitis --------------------------------------------------------------------

def CheckWhetherSharedParametersAreInFile(doc, parameterGuids):
    '''
    Filters the passt in list of shared parameter guids by using the shared parameters in the document.\
        Only parameter in both will be returned.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :param parameterGuids: list of shared parameter guids as string values
    :type parameterGuids: list str
    
    :return: list of shared parameter guids as string values
    :rtype: list str
    '''

    filteredGUIDs = []
    paras = GetAllSharedParameters(doc)
    for p in paras:
        if(p.GuidValue.ToString() in parameterGuids):
            filteredGUIDs.append(p.GuidValue.ToString())
    return filteredGUIDs

# ------------------------------------------------------- parameter utilitis - delete --------------------------------------------------------------------

def DeleteSharedParameterByGUID(doc, guid):
    '''
    Deletes a single shared parameter based on a guid provided.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param guid: A shared parameter GUID as string.
    :type guid: str
    :return: True if parameter exists and got deleted succesfully, otherwise False.
    :rtype: bool
    '''

    returnvalue = res.Result()
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
        returnvalue = com.DeleteByElementIds(doc, deleteIds, 'Delete Shared Parameter' , parameterName)
    else:
        returnvalue.UpdateSep(False, 'parameter with guid: ' + guid + ' does not exist in file.')
    return returnvalue

def DeleteSharedParameters(doc, parameterGuids):
    '''
    Deletes shared parameters by GUID from document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterGuids: List of shared parameter GUIDs as string.
    :type parameterGuids: list str

    :return: 
        Result class instance.

        - Parameter deletion status returned in result.status. False if an exception occured, otherwise True.
        - result.message will contain the name of the shared parameter deleted.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
    
    :rtype: :class:`.Result`
    '''

    returnvalue = res.Result()
    deleteGuids = CheckWhetherSharedParametersAreInFile(doc, parameterGuids)
    if(len(deleteGuids) > 0):
        for deleteGuid in  deleteGuids:
            deleteStatus = DeleteSharedParameterByGUID(doc, deleteGuid)
            returnvalue.Update(deleteStatus)
    else:
        returnvalue.UpdateSep(True, 'No matching shard parameters in file!')
    return returnvalue

# ------------------------------------------------------- parameter reporting --------------------------------------------------------------------

def ParamBindingExists(doc, paramName, paramType):
    '''
    Gets all paramterbindings for a given parameter.

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
        pdef = p.GetDefinition()
        pbindings = []
        # parameter bindings do not exist in a family document
        if(doc.IsFamilyDocument == False):
            pbindings = ParamBindingExists(doc, rdb.Element.Name.GetValue(p), pdef.ParameterType)
        
        # just in case parameter name is not unicode
        parameterName = 'unknonw'
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
            str(pbindings)
            ])
    return data