'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit floors helper functions.
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

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_FLOORS_HEADER = ['HOSTFILE', 'FLOORTYPEID', 'FLOORTYPENAME']

#: Built in family name for standard floor
FLOOR_FAMILY_NAME = 'Floor'
#: Built in family name for a foundation slab
FOUNDATION_SLAB_FAMILY_NAME = 'Foundation Slab'

#: List of all Built in floor family names
BUILTIN_FLOOR_TYPE_FAMILY_NAMES = [
    FLOOR_FAMILY_NAME,
    FOUNDATION_SLAB_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

# doc:   current model document
def GetAllFloorTypesByCategory(doc):
    '''
    Function returning a filtered element collector of all floor types in the model.

    This uses builtinCategory as filter. Return types includes:
    - Floor
    - In place families or loaded families

    It will therefore not return any foundation slab types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Floors).WhereElementIsElementType()
    return collector

# doc   current model document
def GetFloorTypesByClass(doc):
    '''
    Function returning a filtered element collector of all floor types in the model.

    - Floor
    - Foundation Slab

    it will therefore not return any in place family types ...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    return  rdb.FilteredElementCollector(doc).OfClass(rdb.FloorType)

def BuildFloorTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    Keys are built in floor family type names.
    TODO: This code repeats across a number of modules. Use generic instead!

    :param collector: A filtered element collector containing floor types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: floor type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)

    :return: A dictionary containing key: built in floor type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortFloorTypesByFamilyName(doc):
    '''
    Returns a dictionary containing all floor types in the model.

    Key values are as per BUILTIN_FLOOR_TYPE_FAMILY_NAMES.
    TODO: This code repeats across a number of modules. Use generic instead!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: floor type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    '''

    # get all floor Type Elements
    wts = GetFloorTypesByClass(doc)
    # get all floor types including in place floor families
    wts_two = GetAllFloorTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildFloorTypeDictionary(wts, usedWts)
    usedWts = BuildFloorTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Floor types -------------------------------------------------------

def GetAllFloorInstancesInModelByCategory(doc):
    '''
    Gets all floor elements placed in model...ignores in foundation slabs.

    Filters by builtin category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Floors).WhereElementIsNotElementType()

def GetAllFloorInstancesInModelByClass(doc):
    '''
    Gets all floor elements placed in model...ignores in place families of category floor.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.Floor).WhereElementIsNotElementType()

def GetAllFloorTypeIdsInModelByCategory(doc):
    '''
    Returns all Floor element types available in model.

    Filters by builtin category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colCat = GetAllFloorTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllFloorTypeIdsInModelByClass(doc):
    '''
    Returns all Floor element types available in model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colClass = GetFloorTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

def GetUsedFloorTypeIds(doc):
    '''
    Returns all used in Floor type ids.

    Filters by builtin category.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing not used floor types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllFloorTypeIdsInModelByCategory, 1)
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
 
def GetUnusedNonInPlaceFloorTypeIdsToPurge(doc):
    '''
    Gets all unused floor type id's.
    
    This method can be used to safely delete unused wall types:
    In the case that no wall instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one wall type definition to be in the model.

    Filters by class:

    - Floor
    - foundation slab

    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing not used floor types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllFloorTypeIdsInModelByClass, 0)
    # make sure there is at least on Floor type per system family left in model
    floorTypes = SortFloorTypesByFamilyName(doc)
    for key, value in floorTypes.items():
        if(key in BUILTIN_FLOOR_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place Floor types -------------------------------------------------------

def GetInPlaceFloorFamilyInstances(doc):
    '''
    Gets all instances of in place families of category floor.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor family instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Floors)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceFloorTypeIdsInModel(doc):
    '''
    Gets type ids off all available in place families symbols (types) of category floor.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place floor symbols (types).
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Floors)
    return ids

def GetUsedInPlaceFloorTypeIds(doc):
    '''
    Gets all used in place family symbol (type) ids.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place floor symbols (types).
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceFloorTypeIdsInModel, 1)
    return ids

def GetUnusedInPlaceFloorTypeIds(doc):
    '''
    Gets all used in place family symbol (type) ids.

    Unused: Not one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place floor symbols (types).
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceFloorTypeIdsInModel, 0)
    return ids

def GetUnusedInPlaceFloorIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of in place floor families which can be safely deleted from the model.

    This method can be used to safely delete unused in place floor types. There is no requirement by Revit to have at least one\
        in place wall definition in the model.
    
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused in place floor types and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceFloorTypeIds)
    return ids
