'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit stair path elements. 
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
import Autodesk.Revit.DB.Architecture as rdbA

from duHast.APISamples.Common import RevitCommonAPI as com

def GetStairPathTypesByClass(doc):
    '''
    Gets a filtered element collector of all Stair path types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing stair path types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsPathType)


def GetAllStairPathTypeIdsInModelByClass(doc):
    '''
    Gets all Stair path element type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing stair path types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetStairPathTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids


def GetAllStairPathElementsInModel(doc):
    '''
    Gets a filtered element collector of all Stair path elements in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing stair path elements.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StairsPaths).WhereElementIsNotElementType()