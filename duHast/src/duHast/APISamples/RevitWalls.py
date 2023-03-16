'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit walls. 
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
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
import System

# import common library modules
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitMaterials as rMat
from duHast.APISamples import RevitFamilyUtils as rFam
from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: Header used in reports
REPORT_WALLS_HEADER = ['HOSTFILE', 'WALLTYPEID', 'WALLTYPENAME', 'FUNCTION', 'LAYERWIDTH', 'LAYERMATERIALNAME', 'LAYERMATERIALMARK']

#: Built in wall family name for stacked wall
STACKED_WALL_FAMILY_NAME = 'Stacked Wall'
#: Built in wall family name for curtain wall
CURTAIN_WALL_FAMILY_NAME = 'Curtain Wall'
#: Built in wall family name for basic wall
BASIC_WALL_FAMILY_NAME = 'Basic Wall'

#: List of all Built in wall family names
BUILTIN_WALL_TYPE_FAMILY_NAMES = [
    STACKED_WALL_FAMILY_NAME,
    CURTAIN_WALL_FAMILY_NAME,
    BASIC_WALL_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

def GetAllWallTypes(doc): 
    '''
    Gets all wall types in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Walls).WhereElementIsElementType()
    return collector

def GetWallTypesByClass(doc):
    '''
    This will return a filtered element collector of all wall types by class in the model
    
    It will therefore not return any in place wall types since revit treats those as families...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdb.WallType)

def BuildWallTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    Keys are built in wall family type names.

    :param collector: A filtered element collector containing wall types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: wall type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)

    :return: A dictionary containing key: built in wall type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            # todo : check WallKind Enum???
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortWallTypesByFamilyName(doc):
    '''
    Returns a dictionary of all wall types in the model where key is the build in wall family name, values are ids of associated wall types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: built in wall type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    # get all Wall Type Elements
    wts = GetWallTypesByClass(doc)
    # get all wall types including in place wall families
    wts_two = GetAllWallTypes(doc)
    usedWts = {}
    usedWts = BuildWallTypeDictionary(wts, usedWts)
    usedWts = BuildWallTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- stacked wall types -------------------------------------------------------

def GetAllStackedWallInstancesInModel(doc):
    '''
    Gets all stacked wall elements placed in model...ignores legend elements.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing wall instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StackedWalls).WhereElementIsNotElementType()

def GetAllStackedWallTypesInModel(doc):
    '''
    Gets all stacked wall element types used by instances placed in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stacked wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StackedWalls).WhereElementIsElementType()

def GetAllStackedWallTypeIdsInModel(doc):
    '''
    Gets all stacked wall element types available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stacked wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StackedWalls).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetUsedStackedWallTypeIds(doc):
    '''
    Returns all used stack wall type ids. 

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing used stacked wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllStackedWallTypeIdsInModel, 1)
    return ids

def GetUnusedStackedWallTypeIdsToPurge(doc):
    '''
    Gets all unused stacked wall type id's.
    
    This method can be used to safely delete unused wall types:
    In the case that no wall instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one wall type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing not used stacked wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllStackedWallTypeIdsInModel, 0)
    availableTypeCount = len(GetAllStackedWallTypeIdsInModel(doc).ToList())
    if len(ids) == availableTypeCount:
        ids.pop(0)
    return ids

# -------------------------------- in place wall types -------------------------------------------------------

def GetInPlaceWallFamilyInstances(doc):
    '''
    Returns all instances in place families of category wall in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing  in place wall instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Walls)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceWallTypeIdsInModel(doc):
    '''
    Gets all type ids off all available in place families of category wall.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Walls)
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetUsedInPlaceWallTypeIds(doc):
    '''
    Gets all used in place type ids in the model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing used in place wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceWallTypeIdsInModel, 1)
    return ids

def GetUnusedInPlaceWallTypeIds(doc):
    '''
    Gets all unused in place type ids in the model.

    Unused: Not one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused in place wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceWallTypeIdsInModel, 0)
    return ids

def GetUnusedInPlaceWallIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of in place wall families which can be safely deleted from the model.

    This method can be used to safely delete unused in place wall types. There is no requirement by Revit to have at least one\
        in place wall definition in the model.
    
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused in place wall types and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceWallTypeIds)
    return ids

# -------------------------------- curtain wall types -------------------------------------------------------

def GetAllCurtainWallTypeIdsInModel(doc):
    '''
    Gets type ids off all available curtain wall types in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    dic = SortWallTypesByFamilyName(doc)
    if(dic.has_key(CURTAIN_WALL_FAMILY_NAME)):
        ids = dic[CURTAIN_WALL_FAMILY_NAME]
    return ids

def GetAllCurtainWallInstancesInModel(doc, availableIds):
    '''
    Gets all curtain wall elements placed in model...ignores legend elements.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param availableIds: Filter: curtain wall type ids to check wall instances for.
    :type availableIds: list of Autodesk.Revit.DB.ElementId

    :return: List of wall instances
    :rtype: List of Autodesk.Revit.DB.Wall
    '''

    instances = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            instances.append(c)
    return instances

def GetPlacedCurtainWallTypeIdsInModel(doc, availableIds):
    '''
    Gets all used curtain wall types in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param availableIds: Filter: curtain wall type ids to check wall types for.
    :type availableIds: list of Autodesk.Revit.DB.ElementId

    :return: List of wall instances
    :rtype: List of Autodesk.Revit.DB.Wall
    '''

    instances = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            instances.append(c.GetTypeId())
    return instances

def GetUsedCurtainWallTypeIds(doc):
    '''
    Gets type ids off all used curtain wall types.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing used in curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''
    
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallTypeIdsInModel, 1)
    return ids

def GetUnUsedCurtainWallTypeIdsToPurge(doc):
    '''
    Gets type ids off all unused curtain wall types.

    This method can be used to safely delete unused curtain wall types. In the case that no curtain\
        wall instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one curtain wall type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused in curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallTypeIdsInModel, 0)
    availableTypeCount = len(GetAllCurtainWallTypeIdsInModel(doc).ToList())
    if len(ids) == availableTypeCount:
        ids.pop(0)
    return ids

# -------------------------------- basic wall types -------------------------------------------------------

def GetAllBasicWallTypeIdsInModel(doc):
    '''
    Gets type ids off all available basic wall types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing all basic wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    dic = SortWallTypesByFamilyName(doc)
    if(dic.has_key(BASIC_WALL_FAMILY_NAME)):
        ids = dic[BASIC_WALL_FAMILY_NAME]
    return ids

def GetAllBasicWallInstancesInModel(doc, availableIds):
    '''
    Gets all basic wall elements placed in model...ignores legend elements.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param availableIds:  Filter: curtain wall type ids to check wall instances for.
    :type availableIds: list of Autodesk.Revit.DB.ElementId

    :return: List of element ids representing all basic wall instances.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    instances = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            instances.append(c)
    return instances

def GetPlacedBasicWallTypeIdsInModel(doc, availableIds):
    '''
    Gets all basic wall types used in model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param availableIds:  Filter: basic wall type ids to check wall instances for.
    :type availableIds: list of Autodesk.Revit.DB.ElementId

    :return: List of element ids representing all basic wall types in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
    for c in col:
        if(c.GetTypeId() in availableIds):
            ids.append(c.GetTypeId())
    return ids

def GetUsedBasicWallTypeIds(doc):
    '''
    Gets type ids off all used basic wall types.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing all basic wall types in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllBasicWallTypeIdsInModel, 1)
    return ids

def GetUnUsedBasicWallTypeIdsToPurge(doc):
    '''
    Gets type ids off all unused basic wall types in model.

    This method can be used to safely delete unused basic wall types. In the case that no basic\
        wall instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one basic wall type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing all basic wall types not in use.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllBasicWallTypeIdsInModel, 0)
    # looks like a separate check is required whether any basic wall type is used in stacked wall type in model at this point
    # argh GetStackedWallMemberIds() is only available on wall element but not wallType. Why?
    availableTypeCount = len(GetAllBasicWallTypeIdsInModel(doc).ToList())
    if len(ids) == availableTypeCount:
        ids.pop(0)
    return ids

# ------------------------------------------------------- walls reporting --------------------------------------------------------------------

def GetWallReportData(doc, revitFilePath):
    '''
    Gets wall data to be written to report file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str

    :return: list of list of sheet properties.
    :rtype: list of list of str
    '''

    data = []
    wallTypes = GetAllWallTypes(doc)
    for wt in wallTypes:
        try:
            wallTypeName = str(rdb.Element.Name.GetValue(wt))
            cs = wt.GetCompoundStructure()
            if cs != None:
                csLayers = cs.GetLayers()
                print(len(csLayers))
                for csLayer in csLayers:
                    layerMat = rMat.GetMaterialById(doc, csLayer.MaterialId)
                    materialMark = com.GetElementMark(layerMat)
                    materialName = rMat.GetMaterialNameById(doc, csLayer.MaterialId)
                    layerFunction = str(csLayer.Function)
                    layerWidth = str(util.ConvertImperialToMetricMM(csLayer.Width)) # conversion from imperial to metric
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