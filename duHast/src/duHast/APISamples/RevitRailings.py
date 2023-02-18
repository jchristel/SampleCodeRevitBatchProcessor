'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit railings. 
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
from System.Collections.Generic import List

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_RailingS_HEADER = ['HOSTFILE', 'RAILINGTYPEID', 'RAILINGTYPENAME']

#: Built in railing family name for railing
RAILING_FAMILY_NAME = 'Railing'
#: Built in railing family name for top rail
TOP_RAIL_FAMILY_NAME = 'Top Rail Type'
#: Built in railing family name for hand rail
HAND_RAIL_FAMILY_NAME = 'Handrail Type'

#: List of all Built in railing family names
BUILTIN_RAILING_TYPE_FAMILY_NAMES = [
    RAILING_FAMILY_NAME,
    TOP_RAIL_FAMILY_NAME,
    HAND_RAIL_FAMILY_NAME
]

#: category filter for all railing element filters by category
RAILING_CATEGORY_FILTER = List[rdb.BuiltInCategory] ([
        rdb.BuiltInCategory.OST_Railings,
        rdb.BuiltInCategory.OST_RailingBalusterRail,
        rdb.BuiltInCategory.OST_RailingHandRail,
        rdb.BuiltInCategory.OST_RailingSupport,
        rdb.BuiltInCategory.OST_RailingSystem,
        rdb.BuiltInCategory.OST_RailingTermination,
        rdb.BuiltInCategory.OST_RailingTopRail,
    ])

# --------------------------------------------- utility functions ------------------

def GetAllRailingTypesByCategory(doc):
    '''
    Gets a filtered element collector of all Railing types in the model.

    Collector will include types of:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - In place families or loaded families

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing related types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    multiCatFilter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    return collector

def GetAllRailingTypesByCategoryExclInPlace(doc):
    '''
    Gets a filtered element collector of all Railing types in the model.

    Collector will include types of:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - loaded families

    Will exclude any inplace families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list railing related types
    :rtype: list of types
    '''

    multiCatFilter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    elements=[]
    for c in collector:
        if(c.GetType() != rdb.FamilySymbol):
            elements.append(c)
    return elements

def GetRailingTypesByClass(doc):
    '''
    Gets a filtered element collector of all Railing types in the model:
    
    Collector will include types of:
    - Railing

    It will therefore not return any top rail or hand rail or in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbA.RailingType)

def BuildRailingTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param collector: A filtered element collector containing railing type elements of family symbols
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: dictionary containing key: railing type family name, value: list of ids
    :type dic: Dictionary {str:[Autodesk.Revit.DB.ElementId]}

    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortRailingTypesByFamilyName(doc):
    '''
    Returns a dictionary where key is the family name and values are ids of types belonging to that family.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    # get all Railing Type Elements
    wts = GetRailingTypesByClass(doc)
    # get all Railing types including in place railing families
    wts_two = GetAllRailingTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildRailingTypeDictionary(wts, usedWts)
    usedWts = BuildRailingTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Railing types -------------------------------------------------------

def GetAllRailingInstancesInModelByCategory(doc):
    '''
    Gets all Railing elements placed in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    multiCatFilter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    return rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType()

def GetAllRailingInstancesInModelByClass(doc):
    '''
    Gets all Railing elements placed in model. Ignores any in place families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.Railing).WhereElementIsNotElementType()

def GetAllRailingTypeIdsInModelByCategory(doc):
    '''
    Gets all railing element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''
    
    ids = []
    colCat = GetAllRailingTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllRailingTypeIdsInModelByClass(doc):
    '''
    Gets all railing element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetRailingTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

def GetAllRailingTypeIdsInModelByClassAndCategory(doc):
    '''
    Gets all Railing element types available in model excluding in place types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetRailingTypesByClass(doc)
    idsClass = com.GetIdsFromElementCollector(colClass)
    colCat = GetAllRailingTypesByCategoryExclInPlace(doc)
    idsCat = com.GetIdsFromElementCollector(colCat)
    for idClass in idsClass:
        if (idClass not in ids):
            ids.append (idClass)
    for idCat in idsCat:
        if( idCat not in ids):
            ids.append(idCat)
    return ids

def GetUsedRailingTypeIds(doc):
    '''
    Gets all used Railing element types available in model excluding in place types.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllRailingTypeIdsInModelByClassAndCategory, 1)
    return ids

def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    
    Returns False if any symbols (types) of a family (first list) are in use in a model (second list).
    
    TODO: repetitive code...Consider generic function!

    :param famTypeIds: List of family symbols (types).
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: List of unused family symbols (types)
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId

    :return: True if all ids in first list are also in second list, otherwise False.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match
 
def GetUnusedNonInPlaceRailingTypeIdsToPurge(doc):
    '''
    Gets all unused Railing type ids for:
    
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - loaded families

    Excludes any in place family types.
    This method can be used to safely delete unused railing types:
    In the case that no railing instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one railing type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRailingTypeIdsInModelByClassAndCategory, 0)
    # make sure there is at least on Railing type per system family left in model
    RailingTypes = SortRailingTypesByFamilyName(doc)
    for key, value in RailingTypes.items():
        if(key in BUILTIN_RAILING_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place Railing types -------------------------------------------------------

def GetInPlaceRailingFamilyInstances(doc):
    '''
    Gets all instances of in place families of category Railing in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    filter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceRailingTypeIdsInModel(doc):
    '''
    Gets type ids off all available in place families of category Railing.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for cat in RAILING_CATEGORY_FILTER: 
        idsByCat = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, cat)
        if(len(idsByCat) > 0):
            ids = ids + idsByCat
    return ids

def GetUsedInPlaceRailingTypeIds(doc):
    '''
    Gets all used in place railing type ids.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRailingTypeIdsInModel, 1)
    return ids

def GetUnusedInPlaceRailingTypeIds(doc):
    '''
    Gets all unused in place railing type ids.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRailingTypeIdsInModel, 0)
    return ids

def GetUnusedInPlaceRailingIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of in place Railing families which can be purged.

    This method can be used to safely delete unused in place railing types and families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceRailingTypeIds)
    return ids


# -------------------------------- baluster types -------------------------------------------------------
# -------------baluster utility -------------


def MergeIntoUniqueList(listSource, listMerge):
    '''
    Merges the second list into the first by adding elements from second list which are not already in first list.

    TODO: Consider more generic code!

    :param listSource: List to add unique values to.
    :type listSource: list var
    :param listMerge: List containing values.
    :type listMerge: list var

    :return: List of unique objects.
    :rtype: list var
    '''

    for i in listMerge:
        if (i not in listSource):
            listSource.append(i)
    return listSource

def GetBalustersUsedInPattern(bPattern):
    '''
    Gets list of unique baluster family ids used in a pattern only.

    :param bPattern: A revit baluster pattern.
    :type bPattern: Autodesk.Revit.DB.Architecture.BalusterPattern 

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for i in range(0, bPattern.GetBalusterCount()):
        balInfo = bPattern.GetBaluster(i)
        if(balInfo.BalusterFamilyId not in ids and balInfo.BalusterFamilyId != rdb.ElementId.InvalidElementId ):
            ids.append(balInfo.BalusterFamilyId)
    # add excess pattern baluster id
    if (bPattern.ExcessLengthFillBalusterId not in ids and bPattern.ExcessLengthFillBalusterId != rdb.ElementId.InvalidElementId):
        ids.append(bPattern.ExcessLengthFillBalusterId)
    return ids

def GetUsedBalusterPostIds(bPostPattern):
    '''
    Gets list of unique baluster posts ids only.

    Includes:

    - CornerPost
    - EndPost
    - StartPost

    :param bPostPattern: A revit post pattern.
    :type bPostPattern: Autodesk.Revit.DB.Architecture.PostPattern 

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''
    
    ids = []
    # get corner post
    if(bPostPattern.CornerPost.BalusterFamilyId != rdb.ElementId.InvalidElementId):
        ids.append(bPostPattern.CornerPost.BalusterFamilyId)
    # get end post id
    if(bPostPattern.EndPost.BalusterFamilyId != rdb.ElementId.InvalidElementId and bPostPattern.EndPost.BalusterFamilyId not in ids):
        ids.append(bPostPattern.EndPost.BalusterFamilyId)
    # get start post id
    if(bPostPattern.StartPost.BalusterFamilyId != rdb.ElementId.InvalidElementId and bPostPattern.StartPost.BalusterFamilyId not in ids):
        ids.append(bPostPattern.StartPost.BalusterFamilyId)
    return ids

def GetUsedBalusterPerTread(bPlacement):
    '''
    Gets the id of the baluster per stair tread.

    :param bPlacement: A baluster placement element.
    :type bPlacement: Autodesk.Revit.DB.Architecture.BalusterPlacement 

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # get baluster per tread
    if(bPlacement.BalusterPerTreadFamilyId != rdb.ElementId.InvalidElementId):
        ids.append(bPlacement.BalusterPerTreadFamilyId)
    return ids

# -------------baluster utility end-------------

def GetAllBalusterSymbols(doc):
    '''
    Gets all baluster symbols (fam types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A filtered element collector of baluster symbols (types).
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StairsRailingBaluster).WhereElementIsElementType()
    return col

def GetAllBalusterSymbolIds(doc):
    '''
    Gets all baluster symbol (fam type) ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = GetAllBalusterSymbols(doc)
    ids = com.GetIdsFromElementCollector (col)
    return ids

def GetBalusterTypesFromRailings(doc):
    '''
    Gets a list of unique baluster symbol (fam type) ids used in railing types in the model.

    Incl:
    - baluster patterns
    - baluster posts
    - baluster per stair 
    
    There can be additional baluster symbols in the model. Those belong to loaded families which are not used in\
        any railing type definition.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    railingTypeIds = GetAllRailingTypeIdsInModelByClassAndCategory(doc)
    for rtId in railingTypeIds:
        el = doc.GetElement(rtId)
        # put into try catch since some rail types have no balusters ...top rail
        try:
            balusterPlacement = el.BalusterPlacement
            idsPattern = GetBalustersUsedInPattern(balusterPlacement.BalusterPattern)
            idsPosts = GetUsedBalusterPostIds(balusterPlacement.PostPattern)
            idsPerTread = GetUsedBalusterPerTread(balusterPlacement)
            # build overall ids list
            ids = MergeIntoUniqueList(ids, idsPattern)
            ids = MergeIntoUniqueList(ids, idsPosts)
            ids = MergeIntoUniqueList(ids, idsPerTread)
        except:
            pass
    return ids

def GetUsedBalusterTypeIds(doc):
    '''
    Gets all used baluster type ids in the model.

    Used: at least one instance of this family symbol (type) is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsedInModel = com.GetUsedUnusedTypeIds(doc, GetAllBalusterSymbolIds, 1)
    idsUsedInRailings = GetBalusterTypesFromRailings(doc)
    ids = MergeIntoUniqueList(ids, idsUsedInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInRailings)
    return ids

def GetUnUsedBalusterTypeIds(doc):
    '''
    Gets all unused baluster type ids in the model.

    Unused: Not one instance of this family symbol (type) is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = GetUsedBalusterTypeIds(doc)
    idsAvailable = GetAllBalusterSymbolIds(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

def GetUnUsedBalusterTypeIdsForPurge(doc):
    '''
    Gets all unused baluster type ids in the model.

    Unused: at least one instance of this family symbol (type) is placed in the model.
    This method can be used to safely delete unused baluster families and symbols.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedBalusterTypeIds)
    return ids
    # no need to keep anything...?
    #idsAll =  GetAllBalusterSymbolIds(doc)
    # need to keep at least one ( do I ...?)
    #if(len(idsAll) == len(ids)):
    #    ids.pop(0)
    #return ids
