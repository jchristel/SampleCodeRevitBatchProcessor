'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit detail items. 
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


from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
from duHast.APISamples.DetailItems import RevitDetailItems as rDetail
from duHast.APISamples.DetailItems.Utility import RevitDetailItemsTypeSorting as rDetailTypeSort

# -------------------------------- repeating detail types -------------------------------------------------------

def GetUsedRepeatingDetailTypeIds(doc):
    '''
    Gets all used repeating detail type ids in the model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = rPurgeUtils.GetUsedUnusedTypeIds(doc, rDetail.GetAllRepeatingDetailTypeIdsAvailable, 1, 1)
    return ids


def GetUnUsedRepeatingDetailTypeIds(doc):
    '''
    Gets all unused repeating detail type ids in the model.
    Unused: not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = rPurgeUtils.GetUsedUnusedTypeIds(doc, rDetail.GetAllRepeatingDetailTypeIdsAvailable, 0, 1)
    return ids


def GetUnUsedRepeatingDetailTypeIdsForPurge(doc):
    '''
    Gets type ids off all unused repeating detail types in model.
    This method can be used to safely delete unused repeating detail types. In the case that no basic\
        wall instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one repeating detail type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all repeating detail types not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.GetUsedUnusedTypeIds(doc, rDetail.GetAllRepeatingDetailTypeIdsAvailable, 0, 1)
    allIds = rDetail.GetAllRepeatingDetailTypeIdsAvailable(doc)
    # need to keep at least one
    if(len(allIds) == len(ids)):
        ids.pop(0)
    return ids

# -------------------------------- Detail families -------------------------------------------------------

def GetAllUsedDetailSymbolIds(doc):
    '''
    Gets all used detail symbol type ids in model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of family symbol (type) ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    dic = rDetailTypeSort.BuildDetailTypeIdsDictionary(rDetail.GetAllDetailTypesByCategory(doc))
    if (dic.has_key(rDetail.ELEMENT_TYPE)):
        idsUnfiltered = dic[rDetail.FAMILY_SYMBOL]
        # check if used in repeating details
        idsRepeatDet = rDetail.GetAllRepeatingDetailTypeIdsAvailable(doc)
        #print('ids used in repeating details ' + str(len(idsRepeatDet)))
        # get detail types used in repeating details only
        idsOfDetailsUsedRepeatDetails = rDetail.GetDetailSymbolsUsedInRepeatingDetails(doc, idsRepeatDet)
        # get detail types used in model
        idsUsedInModel = rPurgeUtils.GetUsedUnusedTypeIds(doc, rDetail.GetAllDetailSymbolIdsAvailable, 1)
        print('ids used in model ' + str(len(idsUsedInModel)))
        # built overall ids list
        for id in idsOfDetailsUsedRepeatDetails:
            if (id not in ids):
                ids.append(id)
        for id in idsUsedInModel:
            if(id not in ids):
                ids.append(id)
        return ids
    else:
        return []


def GetAllUnUsedDetailSymbolIds(doc):
    '''
    Gets all unused detail symbol type ids in model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of family symbol (type) ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    allAvailableIds = rDetail.GetAllDetailSymbolIdsAvailable(doc)
    allUsedIds = GetAllUsedDetailSymbolIds(doc)
    for id in allAvailableIds:
        if(id not in allUsedIds):
            ids.append(id)
    return ids


def GetAllUnUsedDetailSymbolIdsForPurge(doc):
    '''
    Gets type ids off all unused detail symbols (types) in model.
    This method can be used to safely delete all unused detail symbols (types) and families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all unused detail symbols and families not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.GetUnusedInPlaceIdsForPurge(doc, GetAllUnUsedDetailSymbolIds)
    return ids


def GetUsedFilledRegionTypeIds(doc):
    '''
    Gets all used filled region type ids in model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of filled region type ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    idsAll = rDetail.GetAllFilledRegionTypeIdsAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = rDetailTypeSort.BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
        if(dic.has_key('Autodesk.Revit.DB.FilledRegion')):
            ids.append(id)
    return ids


def GetUnUsedFilledRegionTypeIds(doc):
    ''''
    Gets all unused filled region type ids in model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of filled region type ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    idsAll = rDetail.GetAllFilledRegionTypeIdsAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = rDetailTypeSort.BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
        if(dic.has_key('Autodesk.Revit.DB.FilledRegion') == False):
            ids.append(id)
    return ids


def GetUnUsedFilledRegionTypeIdsForPurge(doc):
    '''
    Gets ids off all unused filled region types in model.
    This method can be used to safely delete all unused filled region types in model. In the case that no filled\
        region instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one filled region type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing all unused filled region types not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedFilledRegionTypeIds(doc)
    idsAll = rDetail.GetAllFilledRegionTypeIdsAvailable(doc)
    # need to keep at least one
    if(len(idsAll) == len(ids)):
        ids.pop(0)
    return ids