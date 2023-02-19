'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit building pads helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.APISamples import RevitCommonAPI as com
from duHast.Utilities import Result as res
from duHast.APISamples import RevitFamilyUtils as rFam
from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_BUILDING_PAD_HEADER = ['HOSTFILE', 'BUILDINGPADTYPEID', 'BUILDINGPADTYPENAME']
#: Built in family name for pad
BASIC_BUILDING_PAD_FAMILY_NAME = 'Pad'
#: List of all Built in pad family names
BUILTIN_BUILDING_PAD_TYPE_FAMILY_NAMES = [
    BASIC_BUILDING_PAD_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

def GetAllBuildingPadTypesByCategory(doc):
    '''
    Gets a filtered element collector of all BuildingPad types in the model.
    
    - Basic BuildingPad
    
    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_BuildingPad).WhereElementIsElementType()
    return collector

def GetBuildingPadTypesByClass(doc):
    '''
    Gets a filtered element collector of all building pad types in the model:

    - Basic BuildingPad
    
    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdb.BuildingPadType)

def BuildBuildingPadTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    Keys are built in building pad family type names.

    TODO: Use more generic code.

    :param collector: A filtered element collector containing building pad types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key:  building pad type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)

    :return: A dictionary containing key: built in building pad type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortBuildingPadTypesByFamilyName(doc):
    '''
    Returns a dictionary of all building pad types in the model where key is the build in wall family name, values are ids of associated wall types.

    TODO: Use more generic code.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: built in building pad type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    # get all building pad Type Elements
    wts = GetBuildingPadTypesByClass(doc)
    # get all pad types including in place pad families
    wts_two = GetAllBuildingPadTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildBuildingPadTypeDictionary(wts, usedWts)
    usedWts = BuildBuildingPadTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place BuildingPad types -------------------------------------------------------

def GetAllBuildingPadInstancesInModelByCategory(doc):
    '''
    Gets all building pad elements placed in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_BuildingPad).WhereElementIsNotElementType()
    
def GetAllBuildingPadInstancesInModelByClass(doc):
    '''
    Gets all building pad elements placed in model.

    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
   
    return rdb.FilteredElementCollector(doc).OfClass(rdb.BuildingPad).WhereElementIsNotElementType()

def GetAllBuildingPadTypeIdsInModelByCategory(doc):
    '''
    Gets all building pad element type ids available in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colCat = GetAllBuildingPadTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllBuildingPadTypeIdsInModelByClass(doc):
    '''
    Gets all building pad element type ids available in model.

    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A filtered element collector containing building pad type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colClass = GetBuildingPadTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetUsedBuildingPadTypeIds(doc):
    '''
    Gets all used building pad type ids.

    Filters by category.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing used building pad types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllBuildingPadTypeIdsInModelByCategory, 1)
    return ids

def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of ids. True if any id is not in unUsedTypeIds.

    TODO: check for more generic list comparison and remove this function.

    :param famTypeIds: List of family type ids to check.
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: Reference list of ids.
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId

    :return: True if any id from famTypeIds is not in unUsedTypeIds.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match
 
# doc   current document
def GetUnusedNonInPlaceBuildingPadTypeIdsToPurge(doc):
    '''
    Gets all unused building pad type id's.
    
    - Basic BuildingPad
    
    This method can be used to safely delete unused building pad types:
    In the case that no building pad instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one building pad type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing not used building pad types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllBuildingPadTypeIdsInModelByClass, 0)
    # make sure there is at least on BuildingPad type per system family left in model
    BuildingPadTypes = SortBuildingPadTypesByFamilyName(doc)
    for key, value in BuildingPadTypes.items():
        if(key in BUILTIN_BUILDING_PAD_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place BuildingPad types -------------------------------------------------------
# no such thing
