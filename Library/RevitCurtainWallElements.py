'''
This module contains a number of functions around Revit curtain walls. 
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


import RevitCommonAPI as com
import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_CURTAINWALL_ELEMENTS_HEADER = ['HOSTFILE', 'CURTAINWALL_ELEMENT_TYPEID', 'ReplaceMeTYPENAME']

CURTAINWALL_PANEL_EMPTY_FAMILY_NAME = 'Empty System Panel'
CURTAINWALL_PANEL_SYSTEM_FAMILY_NAME = 'Empty System Panel'
CURTAINWALL_MULLION_V_FAMILY_NAME = 'V Corner Mullion'
CURTAINWALL_MULLION_CIRCULAR_FAMILY_NAME = 'Circular Mullion'
CURTAINWALL_MULLION_QUAD_FAMILY_NAME = 'Quad Corner Mullion'
CURTAINWALL_MULLION_L_FAMILY_NAME = 'L Corner Mullion'
CURTAINWALL_MULLION_RECT_FAMILY_NAME = 'Rectangular Mullion'
CURTAINWALL_MULLION_TRAPEZ_FAMILY_NAME = 'Trapezoid Corner Mullion'

BUILTIN_ReplaceMe_TYPE_FAMILY_NAMES = [
    CURTAINWALL_PANEL_EMPTY_FAMILY_NAME,
    CURTAINWALL_PANEL_SYSTEM_FAMILY_NAME,
    CURTAINWALL_MULLION_V_FAMILY_NAME,
    CURTAINWALL_MULLION_CIRCULAR_FAMILY_NAME,
    CURTAINWALL_MULLION_QUAD_FAMILY_NAME,
    CURTAINWALL_MULLION_L_FAMILY_NAME,
    CURTAINWALL_MULLION_RECT_FAMILY_NAME,
    CURTAINWALL_MULLION_TRAPEZ_FAMILY_NAME
]

# category filter for all element filters by category
CURTAINWALL_ELEMENTS_CATEGORYFILTER = List[rdb.BuiltInCategory] ([
        rdb.BuiltInCategory.OST_CurtainWallPanels,
        rdb.BuiltInCategory.OST_CurtainWallMullions
    ])


# --------------------------------------------- utility functions ------------------

# returns all curtain panel element types in a model
# doc:   current model document
def GetAllCurtainWallElementTypesByCategory(doc):
    ''' this will return a filtered element collector of all curtain wall element types in the model:
    - curtain wall panels
    - curtain wall mullions
    - family symbols!
    '''
    multiCatFilter = rdb.ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORYFILTER )
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    return collector

# collector   fltered element collector containing ReplaceMe type elments of family symbols representing in place families
# dic         dictionary containing key: curtainwall element type family name, value: list of ids
def BuildCurtainWallElementTypeDictionary(collector, dic):
    '''returns the dictioanry passt in with keys and or values added retrieved from collector passt in'''
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortCurtainWallElementTypesByFamilyName(doc):
    # get all CurtainWallElement types including in place wall families
    wts_two = GetAllCurtainWallElementTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildCurtainWallElementTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place or loadable Curtain Wall Element types -------------------------------------------------------

# doc   current model document
def GetCurtainWallElementInstancesInModelByCategory(doc):
    ''' returns all CurtainWallElement elements placed in model'''
    multiCatFilter = rdb.ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORYFILTER )
    return rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType()

# doc   current model document
def GetAllCurtainWallElementTypeIdsInModelByCategory(doc):
    ''' returns all CurtainWallElement element type ids available in model '''
    ids = []
    colCat = GetAllCurtainWallElementTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# returns all CurtainWallElement types in a model
# doc:   current model document
def GetAllCurtainWallElementTypesByCategoryExclInPlace(doc):
    ''' this will return a filtered element collector of all CurtainWallElement types in the model:
    - curtain wall panels
    - curtain wall mullions
    '''
    collector = GetAllCurtainWallElementTypesByCategory(doc)
    elements=[]
    for c in collector:
        if(c.GetType() != rdb.FamilySymbol):
            elements.append(c)
    return elements

# returns all CurtainWallElement types in a model
# doc:   current model document
def GetAllCurtainWallElementTypeIdsByCategoryExclSymbols(doc):
    ''' this will return a filtered element collector of all CurtainWallElement type Ids in the model:
    - curtain wall panels
    - curtain wall mullions
    '''
    collector = GetAllCurtainWallElementTypesByCategory(doc)
    ids=[]
    for c in collector:
        if(c.GetType() != rdb.FamilySymbol):
            ids.append(c.Id)
    return ids

# doc   current document
def GetUsedCurtainWallElementTypeIds(doc):
    ''' returns all used in CurtainWallElement type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallElementTypeIdsInModelByCategory, 1)
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
def GetUnusedNonSymbolCurtainWallElementTypeIdsToPurge(doc):
    ''' returns all unused CurtainWallElement type ids for:
    - curtain wall panels
    - curtain wall mullions
    it will therefore not return any family types ...'''
    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallElementTypeIdsByCategoryExclSymbols, 0)
    # unlike other element types, here I do NOT make sure there is at least on curtain wall element type per system family left in model!!
    return ids


# -------------------------------- loadable Curtain Wall Element types -------------------------------------------------------

# doc   current document
def GetAllCurtainWallNonSharedSymbolIdsByCategory(doc):
    ''' 
    this will return a list of all loadable non shared symbols (types) in the model:
    - curtain wall panels
    - curtain wall mullions
    '''
    ids = []
    multiCatFilter = rdb.ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORYFILTER )
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    for c in collector:
        if(c.GetType() == rdb.FamilySymbol):
            fam = c.Family
            pValue = com.GetBuiltInParameterValue(fam, rdb.BuiltInParameter.FAMILY_SHARED)
            if(pValue != None and  pValue == 'No' and c.Id not in ids):
                ids.append(c.Id)
    return ids

# doc   current document
def GetUsedCurtainWallSymbolIds(doc):
    ''' returns all used loadable symbol (type) ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallNonSharedSymbolIdsByCategory, 1)
    return ids

# doc   current document
def GetUnusedCurtainWallSymbolIds(doc):
    ''' returns all unused loadable symbol (type) ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallNonSharedSymbolIdsByCategory, 0)
    return ids

# doc   current document
def GetUnusedICurtainWallSymbolIdsForPurge(doc):
    '''returns symbol(type) ids and family ids (when no type is in use) of loadable symbols which can be purged'''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedCurtainWallSymbolIds)
    return ids