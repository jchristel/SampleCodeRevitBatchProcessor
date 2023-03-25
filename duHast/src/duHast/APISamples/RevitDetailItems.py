'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit detail items.
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
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_GROUPS_HEADER = ['HOSTFILE','ID', 'ITEM TYPE']

# --------------------------------------------- utility functions ------------------

def GetFilledRegionsInModel(doc):
    '''
    Gets all filled region instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list containing floor instances.
    :rtype: list Autodesk.Revit.DB.FilledRegion
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.FilledRegion).ToList()

'''
TODO: check for actual class...
'''
#: class name Autodesk.Revit.DB.ElementType
ELEMENT_TYPE = 'Autodesk.Revit.DB.ElementType'
#: class name Autodesk.Revit.DB.FilledRegionType
FILLED_REGION_TYPE = 'Autodesk.Revit.DB.FilledRegionType'
#: class name Autodesk.Revit.DB.FamilySymbol
FAMILY_SYMBOL = 'Autodesk.Revit.DB.FamilySymbol'

#: List of class names which can be detailed components
DETAIL_COMPONENT_TYPES = [
    ELEMENT_TYPE,
    FILLED_REGION_TYPE,
    FAMILY_SYMBOL
]

def GetAllDetailTypesByCategory(doc):
    '''
    Gets all detail component types in the model.

    Filters by built in category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing detail component types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_DetailComponents).WhereElementIsElementType()
    return collector

def BuildDetailTypeIdsDictionary(collector):
    '''
    Returns the dictionary keys is autodesk.revit.db element type as string and values are available type ids.

    :param collector: A filtered element collector containing detail component types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all type ids belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.ElementId]}
    '''

    dic = {}
    for c in collector:
        if(dic.has_key(str(c.GetType()))):
            if(c.Id not in dic[str(c.GetType())]):
                dic[str(c.GetType())].append(c.Id)
        else:
            dic[str(c.GetType())] = [c.Id]
    return dic

def BuildDependentElementsDictionary(doc, collector):
    '''
    Returns the dictionary keys is autodesk.revit.db element type as string and values are elements of that type.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param collector: A filtered element collector containing elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all elements belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.Element]}
    '''
   
    dic = {}
    for c in collector:
        el = doc.GetElement(c)
        if(dic.has_key(str(el.GetType()))):
            if(c not in dic[str(el.GetType())]):
                dic[str(el.GetType())].append(c)
        else:
            dic[str(el.GetType())] = [c]
    return dic
    
# -------------------------------- repeating detail types -------------------------------------------------------

def GetAllRepeatingDetailTypeIdsAvailable(doc):
    '''
    Get all repeating detail type id's in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(ELEMENT_TYPE)):
        return dic[ELEMENT_TYPE]
    else:
        return []

def GetUsedRepeatingDetailTypeIds(doc):
    '''
    Gets all used repeating detail type ids in the model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypeIdsAvailable, 1, 1)
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

    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypeIdsAvailable, 0, 1)
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

    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypeIdsAvailable, 0, 1)
    allIds = GetAllRepeatingDetailTypeIdsAvailable(doc)
    # need to keep at least one
    if(len(allIds) == len(ids)):
        ids.pop(0)
    return ids

# -------------------------------- Detail families -------------------------------------------------------

def GetAllDetailSymbolIdsAvailable(doc):
    '''
    Gets all detail symbol (types) ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing detail symbols.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(FAMILY_SYMBOL)):
        return dic[FAMILY_SYMBOL]
    else:
        return []

def GetDetailSymbolsUsedInRepeatingDetails(doc, idsRepeatDet):
    '''
    Gets the ids of all symbols used in repeating details.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param idsRepeatDet: List of repeating detail type ids.
    :type idsRepeatDet: list Autodesk.Revit.DB.ElementIds

    :return: List of family symbol (type) ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    for idR in idsRepeatDet:
        repeatDetail = doc.GetElement(idR)
        id = rParaGet.get_built_in_parameter_value(repeatDetail, rdb.BuiltInParameter.REPEATING_DETAIL_ELEMENT)
        if(id not in ids and id != rdb.ElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids

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
    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(ELEMENT_TYPE)):
        idsUnfiltered = dic[FAMILY_SYMBOL]
        # check if used in repeating details
        idsRepeatDet = GetAllRepeatingDetailTypeIdsAvailable(doc)
        #print('ids used in repeating details ' + str(len(idsRepeatDet)))
        # get detail types used in repeating details only
        idsOfDetailsUsedRepeatDetails = GetDetailSymbolsUsedInRepeatingDetails(doc, idsRepeatDet)
        # get detail types used in model
        idsUsedInModel = com.GetUsedUnusedTypeIds(doc, GetAllDetailSymbolIdsAvailable, 1)
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
    allAvailableIds = GetAllDetailSymbolIdsAvailable(doc)
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

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetAllUnUsedDetailSymbolIds)
    return ids
    #ids = GetAllUnUsedDetailSymbolIds(doc)
    #allAvailableIds = GetAllDetailSymbolIdsAvailable(doc)
    # need to keep at least one
    #if(len(allAvailableIds) == len(ids)):
    #    ids.pop(0)
    #return ids

# -------------------------------- filled region types -------------------------------------------------------

def GetAllFilledRegionTypeIdsAvailable(doc):
    '''
    Gets all filled region types ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing filled region types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(FILLED_REGION_TYPE)):
        return dic[FILLED_REGION_TYPE]
    else:
        return []

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
    idsAll = GetAllFilledRegionTypeIdsAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
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
    idsAll = GetAllFilledRegionTypeIdsAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
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
    idsAll = GetAllFilledRegionTypeIdsAvailable(doc)
    # need to keep at least one
    if(len(idsAll) == len(ids)):
        ids.pop(0)
    return ids