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
import RevitFamilyUtils as rFam

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_FLOORS_HEADER = ['HOSTFILE', 'FLOORTYPEID', 'FLOORTYPENAME']

FLOOR_FAMILY_NAME = 'Floor'
FOUNDATION_SLAB_FAMILY_NAME = 'Foundation Slab'

BUILTIN_FLOOR_TYPE_FAMILY_NAMES = [
    FLOOR_FAMILY_NAME,
    FOUNDATION_SLAB_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

# returns all wall types in a model
# doc:   current model document
def GetAllFloorTypesByCategory(doc):
    """ this will return a filtered element collector of all floor types in the model:
    - Floor
    - In place families or loaded families
    it will therefore not return any foundation slab types ..
    """
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType()
    return collector

# doc   current model document
def GetFloorTypesByClass(doc):
    """ this will return a filtered element collector of all floor types in the model:
    - Floor
    - Foundation Slab
    it will therefore not return any in place family types ..."""
    return  FilteredElementCollector(doc).OfClass(FloorType)

# collector   fltered element collector containing Floor type elments of family symbols representing in place families
# dic         dictionary containing key: wall type family name, value: list of ids
def BuildFloorTypeDictionary(collector, dic):
    """returns the dictioanry passt in with keys and or values added retrieved from collector passt in"""
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            # todo : check WallKind Enum???
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortFloorTypesByFamilyName(doc):
    # get all floor Type Elements
    wts = GetFloorTypesByClass(doc)
    # get all floor types including in place wall families
    wts_two = GetAllFloorTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildFloorTypeDictionary(wts, usedWts)
    usedWts = BuildFloorTypeDictionary(wts_two, usedWts)
    return usedWts

# doc             current document
# useTyep         0, no dependent elements; 1: has dependent elements
# typeIdGetter    list of type ids to be checked for dependent elements
def GetUsedUnusedTypeIds(doc, typeIdGetter, useType = 0):
    # get all types elements available
    allWallTypeIds = typeIdGetter(doc)
    ids = []
    for wallTypeId in allWallTypeIds:
        wallType = doc.GetElement(wallTypeId)
        hasDependents = com.HasDependentElements(doc, wallType)
        if(hasDependents == useType):
            ids.append(wallTypeId)
    return ids

# -------------------------------- none in place Floor types -------------------------------------------------------

# doc   current model document
def GetAllFloorInstancesInModelByCategory(doc):
    """ returns all Floor elements placed in model...ignores in foundation slabs"""
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllFloorInstancesInModelByClass(doc):
    """ returns all Floor elements placed in model...ignores in place"""
    return FilteredElementCollector(doc).OfClass(Floor).WhereElementIsNotElementType()

# doc   current model document
def GetAllFloorTypeIdsInModelByCategory(doc):
    """ returns all Floor element types available placed in model """
    ids = []
    colCat = GetAllFloorTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllFloorTypeIdsInModelByClass(doc):
    """ returns all Floor element types available placed in model """
    ids = []
    colClass = GetFloorTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

# doc   current document
def GetUsedFloorTypeIds(doc):
    """ returns all used in Floor type ids """
    ids = GetUsedUnusedTypeIds(doc, GetAllFloorTypeIdsInModelByCategory, 1)
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
def GetUnusedNonInPlaceFloorTypeIdsToPurge(doc):
    """ returns all unused Floor type ids for:
    - Floor
    - foundation slab
    it will therefore not return any in place family types ..."""
    # get unused type ids
    ids = GetUsedUnusedTypeIds(doc, GetAllFloorTypeIdsInModelByClass, 0)
    # make sure there is at least on Floor type per system family left in model
    floorTypes = SortFloorTypesByFamilyName(doc)
    for key, value in floorTypes.items():
        if(key in BUILTIN_FLOOR_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place Floor types -------------------------------------------------------

# doc   current document
def GetInPlaceFloorFamilyInstances(doc):
    """ returns all instances in place families of category floor"""
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    filter = ElementCategoryFilter(BuiltInCategory.OST_Floors)
    return FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)

# doc   current document
def GetAllInPlaceFloorTypeIdsInModel(doc):
    """ returns type ids off all available in place families of category floor"""
    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, BuiltInCategory.OST_Floors)
    return ids

# doc   current document
def GetUsedInPlaceFloorTypeIds(doc):
    """ returns all used in place type ids """
    ids = GetUsedUnusedTypeIds(doc, GetAllInPlaceFloorTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedInPlaceFloorTypeIds(doc):
    """ returns all unused in place type ids """
    ids = GetUsedUnusedTypeIds(doc, GetAllInPlaceFloorTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceFloorIdsForPurge(doc):
    """returns symbol(type) ids and family ids (when no type is in use) of in place floor familis which can be purged"""
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceFloorTypeIds)
    return ids