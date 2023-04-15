'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit railings. 
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

import clr
import System

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Family import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA

from duHast.APISamples.Railings.Utility.RevitRailingCategories import RAILING_CATEGORY_FILTER
from duHast.APISamples.Railings.Utility import RevitRailingsFilter as rRailFilter

# --------------------------------------------- utility functions ------------------

def GetAllRailingTypesByCategory(doc):
    '''
    Gets a filtered element collector of all Railing types in the model.

    Collector will include types of:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - In place families or loaded families

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing related types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    
    collector = rRailFilter._get_all_railing_types_by_category(doc)
    return collector

def GetAllRailingTypesByCategoryExclInPlace(doc):
    '''
    Gets a filtered element collector of all Railing types in the model.

    Collector will include types of:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - loaded families

    Will exclude any inplace families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list railing related types
    :rtype: list of types
    '''

    multiCatFilter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    elements=[]
    for c in collector:
        if(c.GetType() != rdb.FamilySymbol):
            elements.append(c)
    return elements

def GetRailingTypesByClass(doc):
    '''
    Gets a filtered element collector of all Railing types in the model:
    
    Collector will include types of:
    - Railing

    It will therefore not return any top rail or hand rail or in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rRailFilter._get_railing_types_by_class(doc)
    return collector

# -------------------------------- none in place Railing types -------------------------------------------------------

def GetAllRailingInstancesInModelByCategory(doc):
    '''
    Gets all Railing elements placed in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    multiCatFilter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    return rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType()

def GetAllRailingInstancesInModelByClass(doc):
    '''
    Gets all Railing elements placed in model. Ignores any in place families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.Railing).WhereElementIsNotElementType()

def GetAllRailingTypeIdsInModelByCategory(doc):
    '''
    Gets all railing element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''
    
    ids = []
    colCat = GetAllRailingTypesByCategory(doc)
    ids = com.get_ids_from_element_collector (colCat)
    return ids

def GetAllRailingTypeIdsInModelByClass(doc):
    '''
    Gets all railing element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetRailingTypesByClass(doc)
    ids = com.get_ids_from_element_collector(colClass)
    return ids

def GetAllRailingTypeIdsInModelByClassAndCategory(doc):
    '''
    Gets all Railing element types available in model excluding in place types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetRailingTypesByClass(doc)
    idsClass = com.get_ids_from_element_collector(colClass)
    colCat = GetAllRailingTypesByCategoryExclInPlace(doc)
    idsCat = com.get_ids_from_element_collector(colCat)
    for idClass in idsClass:
        if (idClass not in ids):
            ids.append (idClass)
    for idCat in idsCat:
        if( idCat not in ids):
            ids.append(idCat)
    return ids

# -------------------------------- In place Railing types -------------------------------------------------------

def GetInPlaceRailingFamilyInstances(doc):
    '''
    Gets all instances of in place families of category Railing in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    filter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceRailingTypeIdsInModel(doc):
    '''
    Gets type ids off all available in place families of category Railing.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for cat in RAILING_CATEGORY_FILTER: 
        idsByCat = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, cat)
        if(len(idsByCat) > 0):
            ids = ids + idsByCat
    return ids