'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit stairs. 
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

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitFamilyUtils as rFam


# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_ROOFS_HEADER = ['HOSTFILE', 'STAIRTYPEID', 'STAIRTYPENAME']

#: Built in stair family name for basic stairs
BASIC_STAIR_FAMILY_NAME = 'Stair'

#: Built in stair family name for assembled stairs
ASSEMBLED_STAIR_FAMILY_NAME = 'Assembled Stair'

#: Built in stair family name for precast stairs
PRECAST_STAIR_FAMILY_NAME = 'Precast Stair'

#: Built in stair family name for cast in place stairs
CAST_IN_PLACE_STAIR_FAMILY_NAME = 'Cast-In-Place Stair'

#: List of all Built in stair family names
BUILTIN_STAIR_TYPE_FAMILY_NAMES = [
    BASIC_STAIR_FAMILY_NAME,
    ASSEMBLED_STAIR_FAMILY_NAME,
    PRECAST_STAIR_FAMILY_NAME,
    CAST_IN_PLACE_STAIR_FAMILY_NAME
]

#: list of built in parameters attached to stair sub types
STAIR_LANDING_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_LANDING_TYPE
]

#: list of built in parameters for stair cut mark
STAIR_CUT_MARK_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_CUTMARK_TYPE
]

#: list of built in parameters for stair support types
STAIR_SUPPORT_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_LEFT_SIDE_SUPPORT_TYPE, 
    rdb.BuiltInParameter.STAIRSTYPE_INTERMEDIATE_SUPPORT_TYPE,
    rdb.BuiltInParameter.STAIRSTYPE_RIGHT_SIDE_SUPPORT_TYPE
]

#: list of built in parameters for stair run type
STAIR_RUN_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_RUN_TYPE
]

def GetAllStairTypesByCategory(doc):
    '''
    Gets a filtered element collector of all Stair types in the model.

    Return includes:
    - Stair
    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair
    - In place families or loaded families
   
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Stairs).WhereElementIsElementType()
    return collector

def GetStairTypesByClass(doc):
    '''
    Gets a filtered element collector of all Stair types in the model.

    Return includes:

    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair

    It will not return any in place family or Stair types! These are internally treated as Families or Family Symbols class objects.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsType)

def GetStairPathTypesByClass(doc):
    '''
    Gets a filtered element collector of all Stair path types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair path types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsPathType)

def GetAllStairPathElementsInModel(doc):
    '''
    Gets a filtered element collector of all Stair path elements in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair path elements.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StairsPaths).WhereElementIsNotElementType()

def GetStairLandingTypesByClass(doc):
    '''
    Gets a filtered element collector of all Stair landing types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair landing types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsLandingType)

def GetStairRunTypesByClass(doc):
    '''
    Gets a filtered element collector of all Stair run types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair run types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsRunType)

def GetStairCutMarkTypesByClass(doc):
    '''
    Gets a filtered element collector of all cut mark types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair cut mark types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbA.CutMarkType)

def GetAllStairStringersCarriageByCategory(doc):
    '''
    Gets a filtered element collector of all stair stringers and carriage types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair stringers and carriage types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StairsStringerCarriage).WhereElementIsElementType()
    return collector

def BuildStairTypeDictionary(collector, dic):
    '''
    Amends dictionary past in with keys and or values added retrieved from collector past in.

    Key values are as per BUILTIN_STAIR_TYPE_FAMILY_NAMES.

    :param collector: A filtered element collector containing Stair type elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: stair type family name, value: list of ids.
    :type dic: dic { str: [Autodesk.Revit.DB.ElementId]}

    :return: A dictionary containing key: stair type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortStairTypesByFamilyName(doc):
    '''
    Returns a dictionary containing all stair types in the model.

    Key values are as per BUILTIN_STAIR_TYPE_FAMILY_NAMES.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: stair type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    '''

    # get all Stair Type Elements
    wts = GetStairTypesByClass(doc)
    # get all stair types including in place stair families
    wts_two = GetAllStairTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildStairTypeDictionary(wts, usedWts)
    usedWts = BuildStairTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Stair types -------------------------------------------------------

def GetAllStairInstancesInModelByCategory(doc):
    '''
    Gets a filtered element collector of all Stair elements placed in model.

    TODO: Confirm it  ignores in place families?

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType()
    
def GetAllStairInstancesInModelByClass(doc):
    '''
    Gets a filtered element collection all Stair elements placed in model...
    
    TODO: Confirm it ignores Stair soffits.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A filtered element collector containing stair instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.Stairs).WhereElementIsNotElementType()

def GetAllStairTypeIdsInModelByCategory(doc):
    '''
    Gets all Stair element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllStairTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllStairTypeIdsInModelByClass(doc):
    '''
    Gets all Stair element type ids available in model.

    Ignores in place families of category stair.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetStairTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetAllStairPathTypeIdsInModelByClass(doc):
    '''
    Gets all Stair path element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stair path types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetStairPathTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetAllStairLandingTypeIdsInModelByClass(doc):
    '''
    Gets all Stair landing element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stair landing types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetStairLandingTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetAllStairRunTypeIdsInModelByClass(doc):
    '''
    Gets all Stair run element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of element ids representing stair run types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetStairRunTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetAllStairCutMarkTypeIdsInModelByClass(doc):
    '''
    Get all Stair cut mark element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stair cut mark types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetStairCutMarkTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetAllStairStringCarriageTypeIdsInModelByCategory(doc):
    '''
    Get all Stair stringers and carriage element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stair stringer and carriage types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllStairStringersCarriageByCategory (doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetUsedStairTypeIds(doc):
    '''
    Gets all used in Stair type ids.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllStairTypeIdsInModelByCategory, 1)
    return ids

def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of ids. True if any id is not in unUsedTypeIds.

    TODO: check for more generic list comparison and remove this function.

    :param famTypeIds: List of family type ids to check.
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: Reference list of ids.
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId

    :return: True if any id from amTypeIds is not in unUsedTypeIds.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match

# -------------------------------- none in place Stair types purge -------------------------------------------------------

def GetUnusedNonInPlaceStairTypeIdsToPurge(doc):
    '''
    Gets all unused Stair type ids for.

    Included are:

    - Stair Soffit
    - Compound Stair
    - Basic Stair

    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllStairTypeIdsInModelByClass, 0)
    # make sure there is at least on Stair type per system family left in model
    StairTypes = SortStairTypesByFamilyName(doc)
    for key, value in StairTypes.items():
       if(key in BUILTIN_STAIR_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids

#--------------------------------utility functions to ge unused sub types ----------------------

def GetUsedSubTypeIdsFromStairType(doc, stairTypeId, paras):
    '''
    Gets the id of types making up a stair.

    These could be stair landing types, stringer and carriage types etc.
    Types returned depend on parameter definitions past in. 
    Refer to: 

    - STAIR_LANDING_TYPE_PARAS, 
    - STAIR_CUTMARK_TYPE_PARAS, 
    - STAIR_SUPPORT_TYPE_PARAS 

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param stairTypeId: An element id representing a stair type. 
    :type stairTypeId: Autodesk.Revit.DB.ElementId
    :param paras: Parameters containing a type making up a stair.
    :type paras: list Autodesk.Revit.DB.BuiltInParameterDefinition
    
    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    stairType = doc.GetElement(stairTypeId)
    for pDef in paras:
        pValue = rParaGet.get_built_in_parameter_value(stairType, pDef)
        if(pValue !=None and pValue not in ids):
            ids.append(pValue)
    return ids

def GetAllSimilarTypeIds(doc, ids):
    '''
    Gets all unique ids of similar types of element ids passed in.

    TODO: check for similar function elsewhere!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: list of type ids to be added to.
    :type ids: list of Autodesk.Revit.ElementIds

    :return: List of unique ids of similar types.
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    simIds = []
    for id in ids:
         el = doc.GetElement(id)
         simTypes = el.GetSimilarTypes()
         for st in simTypes:
            if (st not in simIds):
                simIds.append(st)
    return simIds

def BuildSystemFamilyDictionary(doc, ids):
    '''
    Returns dictionary where key is the system family name and values list of available type ids of that system family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List of system family ids.
    :type ids: list of Autodesk.Revit.ElementIds
    
    :return: Dictionary of unique ids of similar types.
    :rtype: dictionary {str: list of Autodesk.Revit.ElementIds } 
    '''

    dic = {}
    for id in ids:
        el = doc.GetElement(id)
        if(dic.has_key(el.FamilyName)):
            dic[el.FamilyName].append(id)
        else:
            dic[el.FamilyName] = [id]
    return dic

def CheckSystemFamilies(doc, ids, leaveOneBehind):
    '''
    Check whether a list of ids of system family is the entire list of types available in the model. If so it will remove one\
    type id per system family to allow safe purging.
    Revit requires at least one type definition per system family to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List of ids to check
    :type ids: list of Autodesk.Revit.ElementIds
    :param leaveOneBehind: True: at least one type will be omitted from list.
    :type leaveOneBehind: bool
    
    :return: List of unique ids of similar types.
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    dicToCheck = BuildSystemFamilyDictionary(doc, ids)
    similarIds = GetAllSimilarTypeIds(doc, ids)
    dicReference = BuildSystemFamilyDictionary(doc, similarIds)
    ids = []
    for key,value in dicToCheck.items():
        if (dicReference.has_key(key)):
            if(len(dicReference[key]) == len(dicToCheck[key]) and leaveOneBehind):
                # need to leave one behind...
                if(len(dicToCheck[key])>0):
                    dicToCheck[key].pop(0)
                    ids = ids + dicToCheck[key]
            else:
                 ids = ids + dicToCheck[key]
        else:
            ids = ids + dicToCheck[key]
    return ids

def GetUsedSubTypes(doc, availableIdsGetter, paras, leaveOneBehind = True):
    '''
    Returns a list of type ids which are not used in any stair types. 
    
    Type ids are provided via an id getter function

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param availableIdsGetter: function returning available type ids
    :type availableIdsGetter: func(doc)
    :param paras: list of built in parameters attached to a stair type for given sub types (stringers, path, run, landing)
    :type paras: list of Autodesk.Revit.DB.BuiltInParameter
    :param leaveOneBehind: _description_, defaults to True
    :type leaveOneBehind: bool, optional

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = []
    # get all available type ids and then check against all Stair type ids
    idsAvailable = availableIdsGetter(doc)
    allUsedStairTypeIds = GetAllStairTypeIdsInModelByCategory(doc)
    idsUsedTypes = []
    for used in allUsedStairTypeIds:
        idsUsed = GetUsedSubTypeIdsFromStairType(doc, used, paras)
        for id in idsUsed:
            if(id not in idsUsedTypes):
                idsUsedTypes.append(id)
    for idAvailable in idsAvailable:
        if(idAvailable not in idsUsedTypes):
            ids.append(idAvailable)
    # need to check that we are not trying to delete last type of a system family....
    ids = CheckSystemFamilies(doc, ids, leaveOneBehind)
    return ids

# --------------------------------- purging subtypes ------------------------------------------------

def GetUnusedStairPathTypeIdsToPurge(doc):
    '''
    Gets all unused Stair path ids to purge, will omit on path type id per system family if none are used.

    This method can be used to safely delete unused stair path types. In the case that no stair\
        path instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair path type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    idsUsed = []
    availableTypes = GetAllStairPathTypeIdsInModelByClass(doc)
    col = GetAllStairPathElementsInModel(doc)
    for c in col:
        if (c.GetTypeId() not in idsUsed):
            idsUsed.append(c.GetTypeId())
    ids = []
    for at in availableTypes:
        if(at not in idsUsed):
            ids.append(at)
    ids = CheckSystemFamilies(doc, ids, True)
    return ids

def GetUnusedStairLandingTypeIdsToPurge(doc):
    '''
    Gets all unused Stair landing type ids.

    This method can be used to safely delete unused stair landing types. In the case that no stair\
        landing instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair landing type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = GetUsedSubTypes(doc, GetAllStairLandingTypeIdsInModelByClass, STAIR_LANDING_TYPE_PARAS)
    return ids

def GetUnusedStairRunTypeIdsToPurge(doc):
    '''
    Gets all unused Stair run type ids.

    This method can be used to safely delete unused stair run types. In the case that no stair\
        run instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair run type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = GetUsedSubTypes(doc, GetAllStairRunTypeIdsInModelByClass, STAIR_RUN_TYPE_PARAS)
    return ids

def GetUnusedStairCutMarkTypeIdsToPurge(doc):
    '''
    Gets all unused Stair cut mark type ids.

    This method can be used to safely delete unused stair cut mark types. In the case that no stair\
        cut mark instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair cut mark type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = GetUsedSubTypes(doc, GetAllStairCutMarkTypeIdsInModelByClass, STAIR_CUT_MARK_TYPE_PARAS)
    return ids

def GetUnusedStairStringersCarriageTypeIdsToPurge(doc):
    '''
    Gets all unused Stair stringer / carriage type ids.

    This method can be used to safely delete unused stair stringer / carriage types. In the case that no stair\
        string carriage instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stringer carriage type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = GetUsedSubTypes(doc, GetAllStairStringCarriageTypeIdsInModelByCategory, STAIR_SUPPORT_TYPE_PARAS)
    return ids

# -------------------------------- In place Stair types -------------------------------------------------------

def GetInPlaceStairFamilyInstances(doc):
    '''
    Gets all instances in place families of category stair.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing in place stair family instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Stairs)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceStairTypeIdsInModel(doc):
    '''
    Gets all type ids off all available in place families of category stair.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Stairs)
    return ids

def GetUsedInPlaceStairTypeIds(doc):
    '''
    Gets all used in place stair type ids.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceStairTypeIdsInModel, 1)
    return ids

def GetUnusedInPlaceStairTypeIds(doc):
    '''
    Gets all unused in place stair type ids.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceStairTypeIdsInModel, 0)
    return ids

def GetUnusedInPlaceStairIdsForPurge(doc):
    '''
    Gets symbol (type) ids and family ids (when no type is in use) of in place Stair families which can be purged.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceStairTypeIds)
    return ids
