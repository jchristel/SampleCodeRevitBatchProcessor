'''
This module contains a number of helper functions relating to Revit floors. 
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
import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

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

# doc:   current model document
def GetAllFloorTypesByCategory(doc):
    '''
    Function returning a filtered element collector of all floor types in the model.

    This uses builtincategory as filter. Return types includes:
    - Floor
    - In place families or loaded families

    It will therefore not return any foundation slab types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Floors).WhereElementIsElementType()
    return collector

# doc   current model document
def GetFloorTypesByClass(doc):
    '''
    Function returning a filtered element collector of all floor types in the model.

    - Floor
    - Foundation Slab

    it will therefore not return any in place family types ...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    return  rdb.FilteredElementCollector(doc).OfClass(rdb.FloorType)

# collector   fltered element collector containing Floor type elments of family symbols representing in place families
# dic         dictionary containing key: floor type family name, value: list of ids
def BuildFloorTypeDictionary(collector, dic):
    '''returns the dictionary passt in with keys and or values added retrieved from collector passt in'''
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortFloorTypesByFamilyName(doc):
    # get all floor Type Elements
    wts = GetFloorTypesByClass(doc)
    # get all floor types including in place floor families
    wts_two = GetAllFloorTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildFloorTypeDictionary(wts, usedWts)
    usedWts = BuildFloorTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Floor types -------------------------------------------------------

# doc   current model document
def GetAllFloorInstancesInModelByCategory(doc):
    ''' returns all Floor elements placed in model...ignores in foundation slabs'''
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Floors).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllFloorInstancesInModelByClass(doc):
    ''' returns all Floor elements placed in model...ignores in place'''
    return rdb.FilteredElementCollector(doc).OfClass(rdb.Floor).WhereElementIsNotElementType()

# doc   current model document
def GetAllFloorTypeIdsInModelByCategory(doc):
    ''' returns all Floor element types available placed in model '''
    ids = []
    colCat = GetAllFloorTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllFloorTypeIdsInModelByClass(doc):
    ''' returns all Floor element types available placed in model '''
    ids = []
    colClass = GetFloorTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

# doc   current document
def GetUsedFloorTypeIds(doc):
    ''' returns all used in Floor type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllFloorTypeIdsInModelByCategory, 1)
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
 
# doc   current document
def GetUnusedNonInPlaceFloorTypeIdsToPurge(doc):
    ''' returns all unused Floor type ids for:
    - Floor
    - foundation slab
    it will therefore not return any in place family types ...'''
    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllFloorTypeIdsInModelByClass, 0)
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
    ''' returns all instances in place families of category floor'''
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Floors)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

# doc   current document
def GetAllInPlaceFloorTypeIdsInModel(doc):
    ''' returns type ids off all available in place families of category floor'''
    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Floors)
    return ids

# doc   current document
def GetUsedInPlaceFloorTypeIds(doc):
    ''' returns all used in place type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceFloorTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedInPlaceFloorTypeIds(doc):
    ''' returns all unused in place type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceFloorTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceFloorIdsForPurge(doc):
    '''returns symbol(type) ids and family ids (when no type is in use) of in place floor familis which can be purged'''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceFloorTypeIds)
    return ids