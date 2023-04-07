'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit flex ducts.
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
import Autodesk.Revit.DB.Mechanical as rdbM

from duHast.APISamples.MEP_Systems.Utility.SymbolsInSystemTypes import GetSymbolIdsForMEPSystemTypes, GetUniqueIdsOfUsedSymbolsFromSystemTypeIds
from duHast.APISamples.MEP_Systems.Utility.RevitMEPSystemCategories import CATS_LOADABLE_DUCTS
from duHast.APISamples.Common import RevitCommonAPI as com


def GetAllFlexDuctTypesByCategory(doc):
    '''
    Gets a filtered element collector of all flex duct types in the model.
    - round
    - rectangular
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_FlexDuctCurves).WhereElementIsElementType()
    return collector


def GetFlexDuctTypesByClass(doc):
    '''
    Gets a filtered element collector of all flex duct types in the model.
    - round
    - rectangular
    Will exclude in place families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbM.FlexDuctType)

def GetAllFlexDuctInstancesInModelByCategory(doc):
    '''
    Gets all flex duct elements placed in model.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_FlexDuctCurves).WhereElementIsNotElementType()

def GetAllFlexDuctInstancesInModelByClass(doc):
    '''
    Gets all flex duct elements placed in model.
    Will exclude in place families.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdbM.FlexDuctType).WhereElementIsNotElementType()

def GetAllFlexDuctTypeIdsInModelByCategory(doc):
    '''
    Gets all flex duct type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllFlexDuctTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids


def GetAllFlexDuctTypeIdsInModelByClass(doc):
    '''
    Gets all flex duct type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetFlexDuctTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids


def GetSymbolIdsUsedInFlexDuctTypes(doc):
    '''
    Gets a list of unique symbol ids used in system type properties of flex duct types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unique ids representing family symbols used in flex duct systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    tyeIds = GetAllFlexDuctTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids


def GetSymbolIdsForFlexDuctTypesInModel(doc):
    '''
    Gets list of symbol ids of the following categories:
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    TODO: flex duct and duct do not differentiate in terms of filtering...one function will get both
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_DUCTS, 'GetSymbolIdsForDuctTypes')
    return ids