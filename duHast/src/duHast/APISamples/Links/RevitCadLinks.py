'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to CAD links.
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

from duHast.APISamples.Common import RevitTransaction as rTran, RevitCommonAPI as com
from duHast.Utilities import Result as res
from duHast.APISamples.Links.Utility.LinkPath import GetLinkPath


def GetAllCADLinkTypes(doc):
    '''
    Gets all CAD link types in a model.
    Filters by class.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of CAD link types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType)
    return collector


def GetAllCADLinkInstances(doc):
    '''
    Gets all CAD link instances in a model.
    Filters by class.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of import instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ImportInstance)
    return collector


def GetCADTypeImportsOnly(doc):
    '''
    Gets all CAD imports in a model.
    Filters by class and check whether the element is an external file reference (True its a link, False it is an import)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of all CAD imports in a model.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    '''

    cadImports = []
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType)
    for cad in collector:
        if(cad.IsExternalFileReference() == False):
            cadImports.append(cad)
    return cadImports


def SortCADLinkTypesByModelOrViewSpecific(doc):
    '''
    Returns two lists: First one: cad links types linked by view (2D) , second one cad link types linked into model (3D).
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Two lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType, list Autodesk.Revit.DB.CADLinkType
    '''

    cadLinksByView = []
    cadLinksByModel = []
    collectorCADTypes = GetAllCADLinkTypes(doc)
    collectorCADInstances = GetAllCADLinkInstances(doc)
    idsByView = []
    # work out through the instance which cad link type is by view
    for cInstance in collectorCADInstances:
        if(cInstance.ViewSpecific):
            idsByView.append(cInstance.GetTypeId())
    # filter all cad link types by id's identified
    for cType in collectorCADTypes:
        if(cType.Id in idsByView and cType.IsExternalFileReference()):
            cadLinksByView.append(cType)
        elif(cType.IsExternalFileReference()):
            cadLinksByModel.append(cType)
    return cadLinksByView, cadLinksByModel


def GetAllCADLinkTypeByViewOnly(doc):
    '''
    Gets all CAD links by view in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    '''

    cadLinksByView, cadLinksByModel = SortCADLinkTypesByModelOrViewSpecific(doc)
    return cadLinksByView


def GetAllCADLinkTypeInModelOnly(doc):
    '''
    Gets all CAD links by model in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    '''

    cadLinksByView, cadLinksByModel = SortCADLinkTypesByModelOrViewSpecific(doc)
    return cadLinksByModel


def DeleteCADLinks(doc):
    '''
    Deletes all CAD links in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: 
        Result class instance.
        - .result = True if all CAD links got deleted. Otherwise False.
        - .message will contain status of deletion.
    :rtype: :class:`.Result`
    '''

    ids = []
    returnValue = res.Result()
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.ImportInstance):
        ids.append(p.Id)
    # delete all links at once
    returnValue = com.DeleteByElementIds(doc, ids, 'Deleting CAD links', 'CAD link(s)')
    return returnValue


def ReloadCADLinks(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName):
    '''
    Reloads CAD links from a given file location based on the original link type name (starts with comparison)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkLocations: A list of directories where CAD files can be located.
    :type linkLocations: list str
    :param hostNameFormatted: Not used yet
    :type hostNameFormatted: TBC
    :param doSomethingWithLinkName: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type doSomethingWithLinkName: func(str) -> str
    :return: 
        Result class instance.
        - .result = True if all CAD links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        # get all CAD link types in model
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType):
            linkTypeName = doSomethingWithLinkName(rdb.Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.dwg')
                if(newLinkPath != None):
                    # reloading CAD links requires a transaction
                    def action():
                        actionReturnValue = res.Result()
                        try:
                            result = p.LoadFrom(newLinkPath)
                            actionReturnValue.message = linkTypeName + ' :: ' + str(result.LoadResult)
                        except Exception as e:
                            actionReturnValue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
                        return actionReturnValue
                    transaction = rdb.Transaction(doc, 'Reloading: ' + linkTypeName)
                    reloadResult = rTran.in_transaction(transaction, action)
                    returnValue.Update(reloadResult)
                else:
                    returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue