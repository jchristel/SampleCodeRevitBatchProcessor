'''
This module contains a number of helper functions relating to Revit roofs. 
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
REPORT_ROOFS_HEADER = ['HOSTFILE', 'ROOFTYPEID', 'ROOFTYPENAME']

BASIC_ROOF_FAMILY_NAME = 'Basic Roof'
SLOPED_GLAZING_FAMILY_NAME = 'Sloped Glazing'

BUILTIN_ROOF_TYPE_FAMILY_NAMES = [
    BASIC_ROOF_FAMILY_NAME,
    SLOPED_GLAZING_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

# doc:   current model document
def GetAllRoofTypesByCategory(doc):
    ''' this will return a filtered element collector of all Roof types in the model:
    - Basic Roof
    - In place families or loaded families
    - sloped glazing
    '''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Roofs).WhereElementIsElementType()
    return collector

# doc   current model document
def GetRoofTypesByClass(doc):
    ''' this will return a filtered element collector of all Roof types in the model:
    - Basic Roof
    - sloped glazing
    it will therefore not return any in place family types ...'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdb.RoofType)

# collector   fltered element collector containing Roof type elments of family symbols representing in place families
# dic         dictionary containing key: roof type family name, value: list of ids
def BuildRoofTypeDictionary(collector, dic):
    '''returns the dictioanry passt in with keys and or values added retrieved from collector passt in'''
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortRoofTypesByFamilyName(doc):
    # get all Roof Type Elements
    wts = GetRoofTypesByClass(doc)
    # get all roof types including in place roof families
    wts_two = GetAllRoofTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildRoofTypeDictionary(wts, usedWts)
    usedWts = BuildRoofTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Roof types -------------------------------------------------------

# doc   current model document
def GetAllRoofInstancesInModelByCategory(doc):
    ''' returns all Roof elements placed in model...ignores in place families'''
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Roofs).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllRoofInstancesInModelByClass(doc):
    ''' returns all Roof elements placed in model...ignores roof soffits(???)'''
    return rdb.FilteredElementCollector(doc).OfClass(rdb.Roof).WhereElementIsNotElementType()

# doc   current model document
def GetAllRoofTypeIdsInModelByCategory(doc):
    ''' returns all Roof element types available in model '''
    ids = []
    colCat = GetAllRoofTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllRoofTypeIdsInModelByClass(doc):
    ''' returns all Roof element types available in model '''
    ids = []
    colClass = GetRoofTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

# doc   current document
def GetUsedRoofTypeIds(doc):
    ''' returns all used in Roof type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRoofTypeIdsInModelByCategory, 1)
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
def GetUnusedNonInPlaceRoofTypeIdsToPurge(doc):
    ''' returns all unused Roof type ids for:
    - Roof Soffit
    - Compound Roof
    - Basic Roof
    it will therefore not return any in place family types ...'''
    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRoofTypeIdsInModelByClass, 0)
    # make sure there is at least on Roof type per system family left in model
    RoofTypes = SortRoofTypesByFamilyName(doc)
    for key, value in RoofTypes.items():
        if(key in BUILTIN_ROOF_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place Roof types -------------------------------------------------------

# doc   current document
def GetInPlaceRoofFamilyInstances(doc):
    ''' returns all instances in place families of category roof '''
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Roofs)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

# doc   current document
def GetAllInPlaceRoofTypeIdsInModel(doc):
    ''' returns type ids off all available in place families of category roof '''
    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Roofs)
    return ids

# doc   current document
def GetUsedInPlaceRoofTypeIds(doc):
    ''' returns all used in place type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRoofTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedInPlaceRoofTypeIds(doc):
    ''' returns all unused in place type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRoofTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceRoofIdsForPurge(doc):
    '''returns symbol(type) ids and family ids (when no type is in use) of in place Roof familis which can be purged'''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceRoofTypeIds)
    return ids