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
from duHast.APISamples.Common import RevitCommonAPI as com

from duHast.APISamples.Walls import RevitWallUtility as rWallUtil
from duHast.src.duHast.APISamples.Walls import RevitCurtainWalls as rCurtainWall
from duHast.APISamples.Walls import RevitStackedWalls as rStackedWall


# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: Header used in reports
REPORT_WALLS_HEADER = ['HOSTFILE', 'WALLTYPEID', 'WALLTYPENAME', 'FUNCTION', 'LAYERWIDTH', 'LAYERMATERIALNAME', 'LAYERMATERIALMARK']

#: Built in wall family name for basic wall
BASIC_WALL_FAMILY_NAME = 'Basic Wall'

#: List of all Built in wall family names
BUILTIN_WALL_TYPE_FAMILY_NAMES = [
    rStackedWall.STACKED_WALL_FAMILY_NAME,
    rCurtainWall.CURTAIN_WALL_FAMILY_NAME,
    BASIC_WALL_FAMILY_NAME
]

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
    dic = rWallUtil.SortWallTypesByFamilyName(doc)
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