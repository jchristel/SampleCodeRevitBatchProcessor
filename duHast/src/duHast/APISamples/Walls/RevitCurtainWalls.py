'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit curtain walls utility functions. 
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

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Walls.Utility import RevitWallsTypeSorting  as rWallTypeSort

#: Built in wall family name for curtain wall
CURTAIN_WALL_FAMILY_NAME = 'Curtain Wall'

def GetAllCurtainWallTypeIdsInModel(doc):
    '''
    Gets type ids off all available curtain wall types in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    dic = rWallTypeSort.SortWallTypesByFamilyName(doc)
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