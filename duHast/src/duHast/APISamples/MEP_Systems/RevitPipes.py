'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit pipes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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
import Autodesk.Revit.DB.Plumbing as rdbP

from duHast.APISamples.MEP_Systems.Utility.SymbolsInSystemTypes import GetSymbolIdsForMEPSystemTypes, GetUniqueIdsOfUsedSymbolsFromSystemTypeIds
from duHast.APISamples.MEP_Systems.Utility.RevitMEPSystemCategories import CATS_LOADABLE_PIPES
from  duHast.APISamples.Common import RevitCommonAPI as com


def GetAllPipeTypesByCategory(doc):
    '''
    Gets a filtered element collector of all pipe types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of pipe tray types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_PipeCurves).WhereElementIsElementType()
    return collector


def GetPipeTypesByClass(doc):
    '''
    Gets a filtered element collector of all pipe types in the model.
    Will exclude in place families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of pipe tray types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbP.PipeType)

def GetAllPipeInstancesByCategory(doc):
    '''
    Gets all pipe elements placed in model.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of pipe instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType()
    return collector


def GetPipeInstancesByClass(doc):
    '''
    Gets all pipe elements placed in model.
    Will exclude in place families.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of pipe instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbP.PipeType).WhereElementIsNotElementType()

def GetAllPipeTypeIdsInModelByCategory(doc):
    '''
    Gets all pipe type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllPipeTypesByCategory(doc)
    ids = com.get_ids_from_element_collector (colCat)
    return ids


def GetAllPipeTypeIdsInModelByClass(doc):
    '''
    Gets all pipe type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetPipeTypesByClass(doc)
    ids = com.get_ids_from_element_collector (colClass)
    return ids


def GetSymbolIdsUsedInPipeTypes(doc):
    '''
    Gets a list of unique symbol ids used in system type properties of pipe types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unique ids representing family symbols used in pipe systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    tyeIds = GetAllPipeTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids


def GetSymbolIdsForPipeTypesInModel(doc):
    '''
    Gets list of symbol ids of the following categories:
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_PIPES, 'GetSymbolIdsForPipeTypes')
    return ids