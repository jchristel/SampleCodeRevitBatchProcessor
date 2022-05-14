'''
This module contains a number of helper functions relating to Revit shared parameters. 
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
# header used in reports
REPORT_SHAREDPARAMETERS_HEADER = ['HOSTFILE', 'GUID', 'ID', 'NAME', 'PARAMETERBINDINGS']

# --------------------------------------------- utility functions ------------------

# returns all shared parameters in a model
# doc   current model document
def GetAllSharedParameters(doc):  
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.SharedParameterElement)
    return collector

# ------------------------------------------------------- parameter utilitis --------------------------------------------------------------------

# doc               current model document
# parameterGuids    list of guids to check the document for
def CheckWhetherSharedParametersAreInFile(doc, parameterGuids):
    '''returns the passt in list filtered by whether the shared parameter are in the file'''
    filteredGUIDs = []
    paras = GetAllSharedParameters(doc)
    for p in paras:
        if(p.GuidValue.ToString() in parameterGuids):
            filteredGUIDs.append(p.GuidValue.ToString())
    return filteredGUIDs

# ------------------------------------------------------- parameter utilitis - delete --------------------------------------------------------------------

# doc   current model document
# guid  the guid of the shared parameter as string
def DeleteSharedParameterByGUID(doc, guid):
    '''deletes a single shared parameter based on a guid provided'''
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

# doc               current model document
# parameterGuids    list of guids of shared parameters to be deleted
def DeleteSharedParameters(doc, parameterGuids):
    '''deletes shared parameters by GUID from document'''
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

# returns all paramterbindings for a given parameter
# doc:              the current revit document
# paramName:        the parameter name
# paramType:        the parameter type
def ParamBindingExists(doc, paramName, paramType):
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

# doc:              the current revit document
# revitFilePath:    fully qualified file path of Revit file
def GetSharedParameterReportData(doc, revitFilePath):
    '''gets shared parameter data ready for being printed to file'''
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