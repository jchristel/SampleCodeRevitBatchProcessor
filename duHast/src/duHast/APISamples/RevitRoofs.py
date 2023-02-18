'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit roofs. 
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
REPORT_ROOFS_HEADER = ['HOSTFILE', 'ROOFTYPEID', 'ROOFTYPENAME']

#: Built in roof family name for basic roof
BASIC_ROOF_FAMILY_NAME = 'Basic Roof'
#: Built in roof family name for sloped glazing
SLOPED_GLAZING_FAMILY_NAME = 'Sloped Glazing'
#: List of all Built in roof family names
BUILTIN_ROOF_TYPE_FAMILY_NAMES = [
    BASIC_ROOF_FAMILY_NAME,
    SLOPED_GLAZING_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

def GetAllRoofTypesByCategory(doc):
    '''
    Gets a filtered element collector of all roof types in the model.

    - Basic Roof
    - In place families or loaded families
    - sloped glazing

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Roofs).WhereElementIsElementType()
    return collector

def GetRoofTypesByClass(doc):
    '''
    Gets a filtered element collector of all Roof types in the model:

    - Basic Roof
    - sloped glazing

    Since this is based of class roof it will therefore not return any in place family types!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdb.RoofType)

def BuildRoofTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param collector: A filtered element collector containing roof type elements of family symbols
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: dictionary containing key: roof type family name, value: list of ids
    :type dic: Dictionary {str:[Autodesk.Revit.DB.ElementId]}

    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortRoofTypesByFamilyName(doc):
    '''
    Returns a dictionary where key is the family name and values are ids of types belonging to that family.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    # get all Roof Type Elements
    rts = GetRoofTypesByClass(doc)
    # get all roof types including in place roof families
    rts_two = GetAllRoofTypesByCategory(doc)
    usedRts = {}
    usedRts = BuildRoofTypeDictionary(rts, usedRts)
    usedRts = BuildRoofTypeDictionary(rts_two, usedRts)
    return usedRts

# -------------------------------- none in place Roof types -------------------------------------------------------

def GetAllRoofInstancesInModelByCategory(doc):
    '''
    Gets all Roof elements placed in model...ignores in place families (to be confirmed!)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Roofs).WhereElementIsNotElementType()

def GetAllRoofInstancesInModelByClass(doc):
    '''
    Gets all Roof elements placed in model...ignores roof soffits(???)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.Roof).WhereElementIsNotElementType()

def GetAllRoofTypeIdsInModelByCategory(doc):
    '''
    Gets all Roof element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllRoofTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllRoofTypeIdsInModelByClass(doc):
    '''
    Gets all Roof element type ids available in model.

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetRoofTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

def GetUsedRoofTypeIds(doc):
    '''
    Gets all used in Roof type ids in the model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllRoofTypeIdsInModelByCategory, 1)
    return ids

def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    
    Returns False if any symbols (types) of a family (first lists) are in use in a model (second list).
    
    TODO: repetitive code...Consider generic function!

    :param famTypeIds: List of family symbols (types).
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: List of unused family symbols (types)
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId

    :return: True if all ids in first list are also in second list, otherwise False.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match
 
def GetUnusedNonInPlaceRoofTypeIdsToPurge(doc):
    '''
    Gets all unused Roof type ids in the model.

    This method can be used to safely delete unused roof types. In the case that no roof\
        instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one roof type definition to be in the model.

    Unused: Not one instance of this type is placed in the model.

    - Roof Soffit
    - Compound Roof
    - Basic Roof

    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRoofTypeIdsInModelByClass, 0)
    # make sure there is at least on Roof type per system family left in model
    RoofTypes = SortRoofTypesByFamilyName(doc)
    for key, value in RoofTypes.items():
        if(key in BUILTIN_ROOF_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place Roof types -------------------------------------------------------

def GetInPlaceRoofFamilyInstances(doc):
    '''
    Gets all instances of in place families of category roof in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof family instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Roofs)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceRoofTypeIdsInModel(doc):
    '''
    Gets type ids off all available in place families of category roof in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Roofs)
    return ids

def GetUsedInPlaceRoofTypeIds(doc):
    '''
    Gets all used in place roof type ids in the model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRoofTypeIdsInModel, 1)
    return ids

def GetUnusedInPlaceRoofTypeIds(doc):
    '''
    Gets all unused in place roof type ids in the model.

    Unused: Not one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRoofTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceRoofIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use of a family) of in place Roof families which can be purged.
    
    This method can be used to safely delete unused in place roof types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceRoofTypeIds)
    return ids
