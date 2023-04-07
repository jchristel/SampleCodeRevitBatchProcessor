'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit ducts.
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
# 

import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Mechanical as rdbM

from duHast.APISamples.MEP_Systems.Utility.SymbolsInSystemTypes import GetSymbolIdsForMEPSystemTypes, GetUniqueIdsOfUsedSymbolsFromSystemTypeIds
from duHast.APISamples.MEP_Systems.Utility.RevitMEPSystemCategories import CATS_LOADABLE_DUCTS
from duHast.APISamples.Common import RevitCommonAPI as com


def GetAllDuctTypesByCategory(doc):
    '''
    Gets a filtered element collector of all duct types in the model.
    - round
    - oval
    - rectangular
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of duct types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_DuctCurves).WhereElementIsElementType()
    return collector


def GetDuctTypesByClass(doc):
    '''
    Gets a filtered element collector of all duct types in the model.
    - round
    - oval
    - rectangular
    Will exclude in place families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of duct types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbM.DuctType)

def GetAllDuctInstancesInModelByCategory(doc):
    '''
    Gets all duct elements placed in model.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of duct instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType()

def GetAllDuctInstancesInModelByClass(doc):
    '''
    Gets all duct elements placed in model.
    Will exclude in place families.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of duct instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdbM.DuctType).WhereElementIsNotElementType()

def GetAllDuctTypeIdsInModelByCategory(doc):
    '''
    Gets all duct type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllDuctTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids


def GetAllDuctTypeIdsInModelByClass(doc):
    '''
    Gets all duct type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetDuctTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids


# --------------------------------------- symbols used in MEP system types -------------------------------

def GetSymbolIdsUsedInDuctTypes(doc):
    '''
    Gets a list of unique symbol ids used in system type properties of duct types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unique ids representing family symbols used in duct systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    tyeIds = GetAllDuctTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids


def GetSymbolIdsForDuctTypesInModel(doc):
    '''
    Gets list of symbol ids of the following categories:
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_DUCTS, 'GetSymbolIdsForDuctTypes')
    return ids