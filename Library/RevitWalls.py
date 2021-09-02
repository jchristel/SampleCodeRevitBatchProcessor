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

# import common library modules
import RevitCommonAPI as com
import RevitMaterials as rMat
import RevitFamilyUtils as rFam
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_WALLS_HEADER = ['HOSTFILE', 'WALLTYPEID', 'WALLTYPENAME', 'FUNCTION', 'LAYERWIDTH', 'LAYERMATERIALNAME', 'LAYERMATERIALMARK']

STACKED_WALL_FAMILY_NAME = 'Stacked Wall'
CURTAIN_WALL_FAMILY_NAME = 'Curtain Wall'
BASIC_WALL_FAMILY_NAME = 'Basic Wall'

BUILTIN_WALL_TYPE_FAMILY_NAMES = [
    STACKED_WALL_FAMILY_NAME,
    CURTAIN_WALL_FAMILY_NAME,
    BASIC_WALL_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

# returns all wall types in a model
# doc:   current model document
def GetAllWallTypes(doc):  
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType()
    return collector

# doc   current model document
def GetWallTypesByClass(doc):
    """ this will return a filtered element collector of all wall types in the model
    it will therefore not return any in place wall types since revit treats those as Families..."""
    return  FilteredElementCollector(doc).OfClass(WallType)

# collector   fltered element collector containing walltype elments of family symbols representing in place families
# dic         dictionary containing key: wall type family name, value: list of ids
def BuildWallTypeDictionary(collector, dic):
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
def SortWallTypesByFamilyName(doc):
    """returns a dictionary where key is the build in wall family name, values are ids of associated wall types"""
    # get all Wall Type Elements
    wts = GetWallTypesByClass(doc)
    # get all wall types including in place wall families
    wts_two = GetAllWallTypes(doc)
    usedWts = {}
    usedWts = BuildWallTypeDictionary(wts, usedWts)
    usedWts = BuildWallTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- stacked wall types -------------------------------------------------------

# doc   current model document
def GetAllStackedWallInstancesInModel(doc):
    """ returns all stacked wall elements placed in model...ignores legend elements"""
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StackedWalls).WhereElementIsNotElementType()

def GetAllStackedWallTypesInModel(doc):
    """ returns all stacked wall element types used by instances placed in model """
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StackedWalls).WhereElementIsElementType()

def GetAllStackedWallTypeIdsInModel(doc):
    """ returns all stacked wall element types available in model """
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StackedWalls).WhereElementIsElementType()
    ids = []
    for c in col:
        ids.append(c.Id)
    return ids

# doc   current document
def GetUsedStackedWallTypeIds(doc):
    """ returns all used stack wall type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllStackedWallTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedStackedWallTypeIdsToPurge(doc):
    """ returns all unused stack wall type ids, will leave one behind if none is used """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllStackedWallTypeIdsInModel, 0)
    availableTypeCount = len(GetAllStackedWallTypeIdsInModel(doc).ToList())
    if len(ids) == availableTypeCount:
        ids.pop(0)
    return ids

# -------------------------------- in place wall types -------------------------------------------------------

# doc   current document
def GetInPlaceWallFamilyInstances(doc):
    """ returns all instances in place families of category wall """
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    filter = ElementCategoryFilter(BuiltInCategory.OST_Walls)
    return FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)

# doc   current document
def GetAllInPlaceWallTypeIdsInModel(doc):
    """ returns type ids off all available in place families of category wall """
    filter = ElementCategoryFilter(BuiltInCategory.OST_Walls)
    col = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    ids = []
    for c in col:
            ids.append(c.Id)
    return ids

# doc   current document
def GetUsedInPlaceWallTypeIds(doc):
    """ returns all used in place type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceWallTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedInPlaceWallTypeIds(doc):
    """ returns all unused in place type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceWallTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceWallIdsForPurge(doc):
    """returns symbol(type) ids and family ids (when no type is in use) of in place wall familis which can be purged"""
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceWallTypeIds)
    return ids

# -------------------------------- curtain wall types -------------------------------------------------------

# doc   current document
def GetAllCurtainWallTypeIdsInModel(doc):
    """ returns type ids off all available curtain wall types"""
    return SortWallTypesByFamilyName(doc)[CURTAIN_WALL_FAMILY_NAME]

# doc           current model document
# availableIds  type ids to check for use a curtain panel
def GetAllCurtainWallInstancesInModel(doc, availableIds):
    """ returns all stacked wall elements placed in model...ignores legend elements"""
    instances = []
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            instances.append(c)
    return instances

# doc           current model document
# availableIds  type ids to check for use a curtain panel
def GetPlacedCurtainWallTypeIdsInModel(doc, availableIds):
    """ returns all stacked wall elements placed in model...ignores legend elements"""
    instances = []
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            instances.append(c.GetTypeId())
    return instances

# doc   current document
def GetUsedCurtainWallTypeIds(doc):
    """ returns type ids off all used curtain wall types """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnUsedCurtainWallTypeIdsToPurge(doc):
    """ returns type ids off all unused curtain wall types, will leave one behind if none is used"""
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallTypeIdsInModel, 0)
    availableTypeCount = len(GetAllCurtainWallTypeIdsInModel(doc).ToList())
    if len(ids) == availableTypeCount:
        ids.pop(0)
    return ids

# -------------------------------- basic wall types -------------------------------------------------------

# doc   current document
def GetAllBasicWallTypeIdsInModel(doc):
    """ returns type ids off all available basic wall types"""
    return SortWallTypesByFamilyName(doc)[BASIC_WALL_FAMILY_NAME]
    
# doc           current model document
# availableIds  type ids to check for use as basic wall type
def GetAllBasicWallInstancesInModel(doc, availableIds):
    """ returns all basic wall elements placed in model...ignores legend elements"""
    instances = []
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            instances.append(c)
    return instances

# doc           current model document
# availableIds  type ids to check for use a curtain panel
def GetPlacedBasicWallTypeIdsInModel(doc, availableIds):
    """ returns all basic wall type elements used in model"""
    ids = []
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            ids.append(c.GetTypeId())
    return ids

# doc   current document
def GetUsedBasicWallTypeIds_OLD(doc):
    """ returns type ids off all used basic wall types """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllBasicWallTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnUsedBasicWallTypeIdsToPurge(doc):
    """ returns type ids off all unused curtain wall types, will leave one behind if none is used"""
    ids = com.GetUsedUnusedTypeIds(doc, GetAllBasicWallTypeIdsInModel, 0)
    availableTypeCount = len(GetAllBasicWallTypeIdsInModel(doc).ToList())
    if len(ids) == availableTypeCount:
        ids.pop(0)
    return ids

# ------------------------------------------------------- walls reporting --------------------------------------------------------------------

# gets wall data ready for being printed to file
# doc: the current revit document
# revitFilePath: fully qualified file path of Revit file
def GetWallReportData(doc, revitFilePath):
    data = []
    wallTypes = GetAllWallTypes(doc)
    for wt in wallTypes:
        try:
            wallTypeName = str(Element.Name.GetValue(wt))
            cs = wt.GetCompoundStructure()
            if cs != None:
                csls = cs.GetLayers()
                print(len(csls))
                for csl in csls:
                    layerMat = rMat.GetMaterialbyId(doc, csl.MaterialId)
                    materialMark = com.GetElementMark(layerMat)
                    materialName = rMat.GetMaterialNameById(doc, csl.MaterialId)
                    layerFunction = str(csl.Function)
                    layerWidth = str(util.ConvertImperialToMetricMM(csl.Width)) # conversion from imperial to metric
                    data.append([
                        revitFilePath, 
                        str(wt.Id), 
                        util.EncodeAscii(wallTypeName),
                        layerFunction, 
                        layerWidth, 
                        util.EncodeAscii(materialName),
                        util.EncodeAscii(materialMark)
                        ])
            else:
                data.append([
                    revitFilePath, 
                    str(wt.Id), 
                    util.EncodeAscii(wallTypeName),
                    'no layers - in place family or curtain wall',
                    str(0.0),
                    'NA',
                    'NA'
                ])              
        except:
            data.append([
                revitFilePath, 
                str(wt.Id)
            ])
    return data