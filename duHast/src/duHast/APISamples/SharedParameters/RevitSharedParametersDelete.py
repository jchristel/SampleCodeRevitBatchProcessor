'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to deleting Revit shared parameters.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Utilities import Result as res, Utility as util
from duHast.APISamples.SharedParameters.RevitSharedParameters import CheckWhetherSharedParametersAreInFile, GetAllSharedParameters
from duHast.APISamples.Common import RevitDeleteElements as rDel


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
        returnValue = rDel.DeleteByElementIds(doc, deleteIds, 'Delete Shared Parameter' , parameterName)
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
        returnValue = rDel.DeleteByElementIds(doc, deleteIds, 'Delete Shared Parameter' , parameterName)
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