'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Views purge unused utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Family import RevitFamilyUtils as rFamUPurge
from duHast.APISamples.Views import RevitViewReferencing as rViewRef
from duHast.APISamples.Views.Utility.ViewTypes import _get_view_types
from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge


# view reference purging

def GetUnusedContinuationMarkerTypeIdsForPurge(doc):
    '''
    Gets all unused view continuation type ids in model for purge.
    This method can be used to safely delete all unused view continuation marker types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    allAvailableTypeIds = rViewRef.GetAllViewContinuationTypeIds(doc)
    allUsedTypeIds = rViewRef.GetUsedViewContinuationTypeIds(doc)
    for aId in allAvailableTypeIds:
        if( aId not in allUsedTypeIds):
            ids.append(aId)
    return ids


def IsNestedFamilySymbol(doc, id, nestedFamilyNames):
    '''
    Returns true if symbol belongs to family in list past in.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id: The element id of a symbol.
    :type id: Autodesk.Revit.DB.ElementId
    :param nestedFamilyNames: list of family names know to be nested families.
    :type nestedFamilyNames: list str
    :return: True if family name derived from symbol is in list past in, otherwise False.
    :rtype: bool
    '''

    flag = False
    famSymbol = doc.GetElement(id)
    fam = famSymbol.Family
    if(fam.Name in nestedFamilyNames):
        flag = True
    return flag


def GetUnusedViewRefAndContinuationMarkerSymbolIds(doc):
    '''
    Gets the ids of all view reference symbols(types) and view continuation symbols (types) not used in the model.
    Not used: These symbols are not used in any view reference types, or nested in any symbols used in view reference types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # compare used vs available in view ref types
    # whatever is marked as unused: check for any instances in the model...placed on legends!
    availableIds = rViewRef.GetAllViewReferenceSymbolIds(doc) # check: does this really return all continuation marker types??
    usedIds = rViewRef.GetUsedViewReferenceAndContinuationMarkerSymbolIds(doc)
    # elevation marker families might use nested families...check!
    nestedFamilyNames = rViewRef.GetNestedFamilyMarkerNames(doc, usedIds)
    checkIds = []
    for aId in availableIds:
        if (aId not in usedIds):
            checkIds.append(aId)
    # check for any instances
    for id in checkIds:
        instances = rFamUPurge.GetFamilyInstancesBySymbolTypeId(doc, id).ToList()
        if(len(instances) == 0):
            if(IsNestedFamilySymbol(doc, id, nestedFamilyNames) == False):
                ids.append(id)
    return ids


def GetUnusedViewRefAndContinuationMarkerFamiliesForPurge(doc):
    '''
    Gets the ids of all view reference symbols(types) ids and or family ids not used in the model for purging.
    This method can be used to safely delete all unused view reference and continuation marker family symbols\
        or families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    return rFamPurge.GetUnusedInPlaceIdsForPurge(doc, GetUnusedViewRefAndContinuationMarkerSymbolIds)

def GetUnusedViewReferenceTypeIdsForPurge(doc):
    '''
    Gets all unused view references type ids in model for purge.
    This method can be used to safely delete all unused view reference types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    allAvailableTypeIds = rViewRef.GetAllViewReferenceTypeIdData(doc)
    allUsedTypeIds = rViewRef.GetUsedViewReferenceTypeIdData(doc)
    for key,value in allAvailableTypeIds.items():
        if(allUsedTypeIds.has_key(key)):
            for availableTypeId in allAvailableTypeIds[key]:
                if(availableTypeId not in allUsedTypeIds[key]):
                    ids.append(availableTypeId)
        else:
            # add all types under this key to be purge list...might need to check whether I need to leave one behind...
            if(len(allAvailableTypeIds[key])>0):
                ids = ids + allAvailableTypeIds[key]
    return ids


# view types purging

def GetUsedViewTypeIdsInTheModel(doc):
    '''
    Returns all view family types in use in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: ids of view family types in use
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    viewTypeIdsUsed = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out browser organization and other views which cant be deleted
        if(v.IsTemplate == False and
        v.ViewType != rdb.ViewType.SystemBrowser and
        v.ViewType != rdb.ViewType.ProjectBrowser and
        v.ViewType != rdb.ViewType.Undefined and
        v.ViewType != rdb.ViewType.Internal and
        v.ViewType != rdb.ViewType.DrawingSheet):
            if(v.GetTypeId() not in viewTypeIdsUsed):
                viewTypeIdsUsed.append(v.GetTypeId())
    return viewTypeIdsUsed


def GetUnusedViewTypeIdsInModel(doc):
    '''
    Returns all unused view family types in the model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: ids of view family types not in use
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filteredUnusedViewTypeIds = com.get_unused_type_ids_in_model(doc, _get_view_types, GetUsedViewTypeIdsInTheModel)
    return filteredUnusedViewTypeIds