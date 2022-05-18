'''
This module contains a number of helper functions relating to Revit stairs. 
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

import RevitCommonAPI as com
import Result as res
import RevitFamilyUtils as rFam
import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdba
clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_ROOFS_HEADER = ['HOSTFILE', 'STAIRTYPEID', 'STAIRTYPENAME']

BASIC_STAIR_FAMILY_NAME = 'Stair'
ASSEMBLED_STAIR_FAMILY_NAME = 'Assembled Stair'
PRECAST_STAIR_FAMILY_NAME = 'Precast Stair'
CAST_IN_PLACE_STAIR_FAMILY_NAME = 'Cast-In-Place Stair'


BUILTIN_STAIR_TYPE_FAMILY_NAMES = [
    BASIC_STAIR_FAMILY_NAME,
    ASSEMBLED_STAIR_FAMILY_NAME,
    PRECAST_STAIR_FAMILY_NAME,
    CAST_IN_PLACE_STAIR_FAMILY_NAME
]

# list of built in parameters attached to stair sub types
STAIR_LANDING_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_LANDING_TYPE
]

STAIR_CUTMARK_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_CUTMARK_TYPE
]

STAIR_SUPPORT_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_LEFT_SIDE_SUPPORT_TYPE, 
    rdb.BuiltInParameter.STAIRSTYPE_INTERMEDIATE_SUPPORT_TYPE,
    rdb.BuiltInParameter.STAIRSTYPE_RIGHT_SIDE_SUPPORT_TYPE
]

STAIR_RUN_TYPE_PARAS = [
    rdb.BuiltInParameter.STAIRSTYPE_RUN_TYPE
]

# doc:   current model document
def GetAllStairTypesByCategory(doc):
    ''' this will return a filtered element collector of all Stair types in the model:
    - Stair
    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair
    - In place families or loaded families
    '''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Stairs).WhereElementIsElementType()
    return collector

# doc   current model document
def GetStairTypesByClass(doc):
    ''' this will return a filtered element collector of all Stair types in the model:
    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair
    it will therefore not return any in place family types or Stair types...'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdba.StairsType)

# doc   current model document
def GetStairPathTypesByClass(doc):
    ''' this will return a filtered element collector of all Stair path types in the model '''
    return  rdb.FilteredElementCollector(doc).OfClass(rdba.StairsPathType)

def GetAllStairPathElementsInModel(doc):
    ''' this will return a filtered element collector of all Stair path elements in the model '''
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StairsPaths).WhereElementIsNotElementType()

# doc   current model document
def GetStairLandingTypesByClass(doc):
    ''' this will return a filtered element collector of all Stair landing types in the model '''
    return  rdb.FilteredElementCollector(doc).OfClass(rdba.StairsLandingType)

# doc   current model document
def GetStairRunTypesByClass(doc):
    ''' this will return a filtered element collector of all Stair run types in the model '''
    return  rdb.FilteredElementCollector(doc).OfClass(rdba.StairsRunType)

# doc   current model document
def GetStairCutMarkTypesByClass(doc):
    ''' this will return a filtered element collector of all cut mark types in the model '''
    return  rdb.FilteredElementCollector(doc).OfClass(rdba.CutMarkType)

# returns all stringers and carriage types in a model
# doc:   current model document
def GetAllStairStringersCarriageByCategory(doc):
    ''' this will return a filtered element collector of all Stair stringers and cariage types in the model'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StairsStringerCarriage).WhereElementIsElementType()
    return collector

# collector   fltered element collector containing Stair type elments of family symbols representing in place families
# dic         dictionary containing key: stair type family name, value: list of ids
def BuildStairTypeDictionary(collector, dic):
    '''returns the dictioanry passt in with keys and or values added retrieved from collector passt in'''
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortStairTypesByFamilyName(doc):
    # get all Stair Type Elements
    wts = GetStairTypesByClass(doc)
    # get all stair types including in place stair families
    wts_two = GetAllStairTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildStairTypeDictionary(wts, usedWts)
    usedWts = BuildStairTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Stair types -------------------------------------------------------

# doc   current model document
def GetAllStairInstancesInModelByCategory(doc):
    ''' returns all Stair elements placed in model...ignores in place families'''
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllStairInstancesInModelByClass(doc):
    ''' returns all Stair elements placed in model...ignores Stair soffits(???)'''
    return rdb.FilteredElementCollector(doc).OfClass(rdba.Stairs).WhereElementIsNotElementType()

# doc   current model document
def GetAllStairTypeIdsInModelByCategory(doc):
    ''' returns all Stair element types available in model '''
    ids = []
    colCat = GetAllStairTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllStairTypeIdsInModelByClass(doc):
    ''' returns all Stair element types available in model '''
    ids = []
    colClass = GetStairTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairPathTypeIdsInModelByClass(doc):
    ''' returns all Stair path element type ids available in model '''
    ids = []
    colClass = GetStairPathTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairLandingTypeIdsInModelByClass(doc):
    ''' returns all Stair landing element type ids available in model '''
    ids = []
    colClass = GetStairLandingTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairRunTypeIdsInModelByClass(doc):
    ''' returns all Stair run element type ids available in model '''
    ids = []
    colClass = GetStairRunTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairCutMarkTypeIdsInModelByClass(doc):
    ''' returns all Stair cut mark element type ids available in model '''
    ids = []
    colClass = GetStairCutMarkTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairstringCarriageTypeIdsInModelByCategory(doc):
    ''' returns all Stair stringers and carriage element type ids available in model '''
    ids = []
    colCat = GetAllStairStringersCarriageByCategory (doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current document
def GetUsedStairTypeIds(doc):
    ''' returns all used in Stair type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllStairTypeIdsInModelByCategory, 1)
    return ids

# famTypeIds        symbol(type) ids of a family
# usedTypeIds       symbol(type) ids in use in a project
def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    ''' returns false if any symbols (types) of a family are in use in a model'''
    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match

# -------------------------------- none in place Stair types purge -------------------------------------------------------

# doc   current document
def GetUnusedNonInPlaceStairTypeIdsToPurge(doc):
    ''' returns all unused Stair type ids for:
    - Stair Soffit
    - Compound Stair
    - Basic Stair
    it will therefore not return any in place family types ...'''
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

#--------------------------------utlity functions to ge unused sub types ----------------------

# doc   current document
def GetUsedSubTypeIdsFromStairType(doc, stairTypeId, paras):
    ''' gets the ids returned from stair type belonging to parameter list passt in'''
    ids = []
    stairType = doc.GetElement(stairTypeId)
    for pDef in paras:
        pValue = com.GetBuiltInParameterValue(stairType, pDef)
        if(pValue !=None and pValue not in ids):
            ids.append(pValue)
    return ids

# doc   current document
# ids   list of system type ids
def GetAllSimilarTypeIds(doc, ids):
    '''returns all ids of similar types of elemet ids passed in'''
    simIds = []
    for id in ids:
         el = doc.GetElement(id)
         simTypes = el.GetSimilarTypes()
         for st in simTypes:
            if (st not in simIds):
                simIds.append(st)
    return simIds

# doc   current document
# ids   list of system type ids
def BuildSystemFamilyDictionary(doc, ids):
    '''returns dictionary where key is the system family name and values available types of that system family'''
    dic = {}
    for id in ids:
        el = doc.GetElement(id)
        if(dic.has_key(el.FamilyName)):
            dic[el.FamilyName].append(id)
        else:
            dic[el.FamilyName] = [id]
    return dic

# doc   current document
# ids   list of ids to check
# leaveOneBehind        flag default is true: leave at least one type of a system family behind
def CheckSystemFamilies(doc, ids, leaveOneBehind):
    '''check whether a list of ids of system family is the entire list of types avaialble
    if so it will remove one type id per system family to allow purging'''
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

# doc   current document
# availavbleIdsGetter   function returning available type ids
# paras                 list of built in parameters attached to a stair type for given sub types (stringers, path, run, landing)
# leaveOneBehind        flag default is true: leave at least one type of a system family behind
def GetUsedSubTypes(doc, availavbleIdsGetter, paras, leaveOneBehind = True):
    ''' returns a list of type ids which are not used in any stair types. Type ids are furnished via an id getter function '''
    ids = []
    # get all available type ids and then check against all Stair type ids
    idsAvailable = availavbleIdsGetter(doc)
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

# doc   current document
def GetUnusedStairPathTypeIdsToPurge(doc):
    ''' returns all unused Stair path ids to purge, will elave on path type id behinf ber system family'''
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

# doc   current document
def GetUnusedStairLandingTypeIdsToPurge(doc):
    ''' returns all unused Stair landing ids'''
    ids = GetUsedSubTypes(doc, GetAllStairLandingTypeIdsInModelByClass, STAIR_LANDING_TYPE_PARAS)
    return ids

# doc   current document
def GetUnusedStairRunTypeIdsToPurge(doc):
    ''' returns all unused Stair landing ids'''
    ids = GetUsedSubTypes(doc, GetAllStairRunTypeIdsInModelByClass, STAIR_RUN_TYPE_PARAS)
    return ids

# doc   current document
def GetUnusedStairCutMarkTypeIdsToPurge(doc):
    ''' returns all unused Stair cut mark type ids'''
    ids = GetUsedSubTypes(doc, GetAllStairCutMarkTypeIdsInModelByClass, STAIR_CUTMARK_TYPE_PARAS)
    return ids

# doc   current document
def GetUnusedStairStringersCarriageTypeIdsToPurge(doc):
    ''' returns all unused Stair stringer / carriage type ids'''
    ids = GetUsedSubTypes(doc, GetAllStairstringCarriageTypeIdsInModelByCategory, STAIR_SUPPORT_TYPE_PARAS)
    return ids

# -------------------------------- In place Stair types -------------------------------------------------------

# doc   current document
def GetInPlaceStairFamilyInstances(doc):
    ''' returns all instances in place families of category stair '''
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Stairs)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

# doc   current document
def GetAllInPlaceStairTypeIdsInModel(doc):
    ''' returns type ids off all available in place families of category stair '''
    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Stairs)
    return ids

# doc   current document
def GetUsedInPlaceStairTypeIds(doc):
    ''' returns all used in place type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceStairTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedInPlaceStairTypeIds(doc):
    ''' returns all unused in place type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceStairTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceStairIdsForPurge(doc):
    '''returns symbol(type) ids and family ids (when no type is in use) of in place Stair familis which can be purged'''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceStairTypeIds)
    return ids