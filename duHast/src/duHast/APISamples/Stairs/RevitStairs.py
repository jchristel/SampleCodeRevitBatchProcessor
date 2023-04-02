'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit stairs. 
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
import System

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Family import RevitFamilyUtils as rFam
from duHast.APISamples.Stairs.Utility import RevitStairsFilter as rStairsFilter

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA


def GetAllStairTypesByCategory(doc):
    '''
    Gets a filtered element collector of all Stair types in the model.

    Return includes:
    - Stair
    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair
    - In place families or loaded families
   
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rStairsFilter._get_all_stair_types_by_category(doc)
    return collector

def GetStairTypesByClass(doc):
    '''
    Gets a filtered element collector of all Stair types in the model.

    Return includes:

    - Assembled Stair
    - Precast Stair
    - Cast-In-Place Stair

    It will not return any in place family or Stair types! These are internally treated as Families or Family Symbols class objects.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rStairsFilter._get_stair_types_by_class(doc)
    return  collector

# -------------------------------- none in place Stair types -------------------------------------------------------

def GetAllStairInstancesInModelByCategory(doc):
    '''
    Gets a filtered element collector of all Stair elements placed in model.

    TODO: Confirm it  ignores in place families?

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing stair instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType()
    
def GetAllStairInstancesInModelByClass(doc):
    '''
    Gets a filtered element collection all Stair elements placed in model...
    
    TODO: Confirm it ignores Stair soffits.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A filtered element collector containing stair instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.Stairs).WhereElementIsNotElementType()

def GetAllStairTypeIdsInModelByCategory(doc):
    '''
    Gets all Stair element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllStairTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllStairTypeIdsInModelByClass(doc):
    '''
    Gets all Stair element type ids available in model.

    Ignores in place families of category stair.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetStairTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# -------------------------------- In place Stair types -------------------------------------------------------

def GetInPlaceStairFamilyInstances(doc):
    '''
    Gets all instances in place families of category stair.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing in place stair family instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Stairs)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceStairTypeIdsInModel(doc):
    '''
    Gets all type ids off all available in place families of category stair.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Stairs)
    return ids