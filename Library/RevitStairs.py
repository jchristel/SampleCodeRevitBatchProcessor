﻿#
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
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
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

# doc:   current model document
def GetAllStairTypesByCategory(doc):
    """ this will return a filtered element collector of all Stair types in the model:
    - Stair
    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair
    - In place families or loaded families
    """
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsElementType()
    return collector

# doc   current model document
def GetStairTypesByClass(doc):
    """ this will return a filtered element collector of all Stair types in the model:
    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair
    it will therefore not return any in place family types or Stair types..."""
    return  FilteredElementCollector(doc).OfClass(StairsType)

# doc   current model document
def GetStairPathTypesByClass(doc):
    """ this will return a filtered element collector of all Stair path types in the model """
    return  FilteredElementCollector(doc).OfClass(StairsPathType)

# doc   current model document
def GetStairLandingTypesByClass(doc):
    """ this will return a filtered element collector of all Stair landing types in the model """
    return  FilteredElementCollector(doc).OfClass(StairsLandingType)

# doc   current model document
def GetStairRunTypesByClass(doc):
    """ this will return a filtered element collector of all Stair run types in the model """
    return  FilteredElementCollector(doc).OfClass(StairsRunType)

# doc   current model document
def GetStairCutMarkTypesByClass(doc):
    """ this will return a filtered element collector of all cut mark types in the model """
    return  FilteredElementCollector(doc).OfClass(CutMarkType)

# returns all stringers and carriage types in a model
# doc:   current model document
def GetAllStairStringersCarriageByCategory(doc):
    """ this will return a filtered element collector of all Stair stringers and cariage types in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsStringerCarriage).WhereElementIsElementType()
    return collector

# collector   fltered element collector containing Stair type elments of family symbols representing in place families
# dic         dictionary containing key: stair type family name, value: list of ids
def BuildStairTypeDictionary(collector, dic):
    """returns the dictioanry passt in with keys and or values added retrieved from collector passt in"""
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
    """ returns all Stair elements placed in model...ignores in place families"""
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllStairInstancesInModelByClass(doc):
    """ returns all Stair elements placed in model...ignores Stair soffits(???)"""
    return FilteredElementCollector(doc).OfClass(Stair).WhereElementIsNotElementType()

# doc   current model document
def GetAllStairTypeIdsInModelByCategory(doc):
    """ returns all Stair element types available in model """
    ids = []
    colCat = GetAllStairTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllStairTypeIdsInModelByClass(doc):
    """ returns all Stair element types available placed in model """
    ids = []
    colClass = GetStairTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairPathTypeIdsInModelByClass(doc):
    """ returns all Stair path element type ids available in model """
    ids = []
    colClass = GetStairPathTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairLandingTypeIdsInModelByClass(doc):
    """ returns all Stair landing element type ids available in model """
    ids = []
    colClass = GetStairLandingTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairRunTypeIdsInModelByClass(doc):
    """ returns all Stair run element type ids available in model """
    ids = []
    colClass = GetStairRunTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairCutMarkTypeIdsInModelByClass(doc):
    """ returns all Stair cut mark element type ids available in model """
    ids = []
    colClass = GetStairCutMarkTypesByClass (doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllStairstringCarriageTypeIdsInModelByCategory(doc):
    """ returns all Stair stringers and carriage element type ids available in model """
    ids = []
    colCat = GetAllStairStringersCarriageByCategory (doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current document
def GetUsedStairTypeIds(doc):
    """ returns all used in Stair type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllStairTypeIdsInModelByCategory, 1)
    return ids

# famTypeIds        symbol(type) ids of a family
# usedTypeIds       symbol(type) ids in use in a project
def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    """ returns false if any symbols (types) of a family are in use in a model"""
    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match
 
# doc   current document
def GetUnusedNonInPlaceStairTypeIdsToPurge(doc):
    """ returns all unused Stair type ids for:
    - Stair Soffit
    - Compound Stair
    - Basic Stair
    it will therefore not return any in place family types ..."""
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

# doc   current document
def GetUnusedStairPathTypeIdsToPurge(doc):
    """ returns all unused Stair path ids"""
    # get unused type ids
    idsUnused = com.GetUsedUnusedTypeIds(doc, GetAllStairPathTypeIdsInModelByClass, 0)
    availableTypes = GetStairPathTypesByClass(doc)
    if(len(availableTypes.ToList()) == len(idsUnused)):
        idsUnused.pop(0)
    return idsUnused

# doc   current document
def GetUnusedStairLandingTypeIdsToPurge(doc):
    """ returns all unused Stair landing ids"""
    # get unused type ids
    idsUnused = com.GetUsedUnusedTypeIds(doc, GetAllStairLandingTypeIdsInModelByClass, 0)
    availableTypes = GetStairLandingTypesByClass(doc)
    if(len(availableTypes.ToList()) == len(idsUnused)):
        idsUnused.pop(0)
    return idsUnused

# doc   current document
def GetUnusedStairRunTypeIdsToPurge(doc):
    """ returns all unused Stair landing ids"""
    # get unused type ids
    idsUnused = com.GetUsedUnusedTypeIds(doc, GetAllStairRunTypeIdsInModelByClass, 0)
    availableTypes = GetStairRunTypesByClass(doc)
    if(len(availableTypes.ToList()) == len(idsUnused)):
        idsUnused.pop(0)
    return idsUnused

# doc   current document
def GetUnusedStairCutMarkTypeIdsToPurge(doc):
    """ returns all unused Stair cut mark type ids"""
    # get unused type ids
    idsUnused = com.GetUsedUnusedTypeIds(doc, GetAllStairCutMarkTypeIdsInModelByClass, 0)
    availableTypes = GetStairCutMarkTypesByClass(doc)
    if(len(availableTypes.ToList()) == len(idsUnused)):
        idsUnused.pop(0)
    return idsUnused

# doc   current document
def GetUnusedStairStringersCarriageTypeIdsToPurge(doc):
    """ returns all unused Stair stringer / carriage type ids"""
    # get unused type ids
    idsUnused = com.GetUsedUnusedTypeIds(doc, GetAllStairstringCarriageTypeIdsInModelByCategory, 0)
    availableTypes = GetAllStairStringersCarriageByCategory(doc)
    if(len(availableTypes.ToList()) == len(idsUnused)):
        idsUnused.pop(0)
    return idsUnused

# -------------------------------- In place Stair types -------------------------------------------------------

# doc   current document
def GetInPlaceStairFamilyInstances(doc):
    """ returns all instances in place families of category stair """
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    filter = ElementCategoryFilter(BuiltInCategory.OST_Stairs)
    return FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)

# doc   current document
def GetAllInPlaceStairTypeIdsInModel(doc):
    """ returns type ids off all available in place families of category stair """
    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, BuiltInCategory.OST_Stairs)
    return ids

# doc   current document
def GetUsedInPlaceStairTypeIds(doc):
    """ returns all used in place type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceStairTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedInPlaceStairTypeIds(doc):
    """ returns all unused in place type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceStairTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceStairIdsForPurge(doc):
    """returns symbol(type) ids and family ids (when no type is in use) of in place Stair familis which can be purged"""
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceStairTypeIds)
    return ids