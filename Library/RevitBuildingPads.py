'''
This module contains a number of functions around Revit building pads. 
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
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuildingPadType, BuildingPad

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_BUILDINGPAD_HEADER = ['HOSTFILE', 'BUILDINGPADTYPEID', 'BUILDINGPADTYPENAME']

BASIC_BUILDINGPAD_FAMILY_NAME = 'Pad'

BUILTIN_BUILDINGPAD_TYPE_FAMILY_NAMES = [
    BASIC_BUILDINGPAD_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

# doc:   current model document
def GetAllBuildingPadTypesByCategory(doc):
    ''' this will return a filtered element collector of all BuildingPad types in the model:
    - Basic BuildingPad'''
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_BuildingPad).WhereElementIsElementType()
    return collector

# doc   current model document
def GetBuildingPadTypesByClass(doc):
    ''' this will return a filtered element collector of all BuildingPad types in the model:
    - Basic BuildingPad.'''
    return  FilteredElementCollector(doc).OfClass(BuildingPadType)

# collector   fltered element collector containing BuildingPad type elments of family symbols representing in place families
# dic         dictionary containing key: pad type family name, value: list of ids
def BuildBuildingPadTypeDictionary(collector, dic):
    '''returns the dictioanry passt in with keys and or values added retrieved from collector passt in'''
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortBuildingPadTypesByFamilyName(doc):
    # get all building pad Type Elements
    wts = GetBuildingPadTypesByClass(doc)
    # get all pad types including in place pad families
    wts_two = GetAllBuildingPadTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildBuildingPadTypeDictionary(wts, usedWts)
    usedWts = BuildBuildingPadTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place BuildingPad types -------------------------------------------------------

# doc   current model document
def GetAllBuildingPadInstancesInModelByCategory(doc):
    ''' returns all BuildingPad elements placed in model'''
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_BuildingPad).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllBuildingPadInstancesInModelByClass(doc):
    ''' returns all BuildingPad elements placed in model'''
    return FilteredElementCollector(doc).OfClass(BuildingPad).WhereElementIsNotElementType()

# doc   current model document
def GetAllBuildingPadTypeIdsInModelByCategory(doc):
    ''' returns all BuildingPad element types available placed in model '''
    ids = []
    colCat = GetAllBuildingPadTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllBuildingPadTypeIdsInModelByClass(doc):
    ''' returns all BuildingPad element types available placed in model '''
    ids = []
    colClass = GetBuildingPadTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current document
def GetUsedBuildingPadTypeIds(doc):
    ''' returns all used in BuildingPad type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllBuildingPadTypeIdsInModelByCategory, 1)
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
def GetUnusedNonInPlaceBuildingPadTypeIdsToPurge(doc):
    ''' returns all unused BuildingPad type ids for:
    - Basic BuildingPad'''
    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllBuildingPadTypeIdsInModelByClass, 0)
    # make sure there is at least on BuildingPad type per system family left in model
    BuildingPadTypes = SortBuildingPadTypesByFamilyName(doc)
    for key, value in BuildingPadTypes.items():
        if(key in BUILTIN_BUILDINGPAD_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place BuildingPad types -------------------------------------------------------
# no such thing