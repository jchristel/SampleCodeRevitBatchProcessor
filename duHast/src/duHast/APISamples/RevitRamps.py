'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit ramps.
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



# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_RAMPS_HEADER = ['HOSTFILE', 'RAMPTYPEID', 'RAMPTYPENAME']


#: Built in ramp family name for ramp
BASIC_RAMP_FAMILY_NAME = 'Ramp'
#: List of all built in ramp family names
BUILTIN_RAMP_TYPE_FAMILY_NAMES = [
    BASIC_RAMP_FAMILY_NAME,
]

# --------------------------------------------- utility functions ------------------

def GetAllRampTypesByCategory(doc):
    '''
    Gets a filtered element collector of all Ramp types in the model.

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector containing ramp types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Ramps).WhereElementIsElementType()
    return collector

def BuildRampTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param collector: A filtered element collector containing ramp type elements of family symbols representing in place families
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: dictionary containing key: ramp type family name, value: list of ids
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

def SortRampTypesByFamilyName(doc):
    '''
    Returns a dictionary where key is the family name and values are ids of types belonging to that family.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    # get all ramp types including in place ramp families
    wts_two = GetAllRampTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildRampTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Ramp types -------------------------------------------------------

def GetAllRampInstancesInModelByCategory(doc):
    '''
    Gets all ramp elements placed in model...ignores in place families (to be confirmed!)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ramp instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Ramps).WhereElementIsNotElementType()

def GetAllRampTypeIdsInModelByCategory(doc):
    '''
    Gets all ramp element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of ramp types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllRampTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetUsedRampTypeIds(doc):
    '''
    Gets all used ramp element type ids available in model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of ramp types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllRampTypeIdsInModelByCategory, 1, 4)
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
 
def GetUnusedNonInPlaceRampTypeIdsToPurge(doc):
    '''
    Gets all unused ramp type ids in the model.

    This method can be used to safely delete unused ramp types. In the case that no ramp\
        instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one ramp type definition to be in the model.

    Unused: Not one instance of this type is placed in the model.

    - Ramp

    It will therefore not return any in place family types. (No such thing in Revit?)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRampTypeIdsInModelByCategory, 0, 4)
    # make sure there is at least on Ramp type per system family left in model
    RampTypes = SortRampTypesByFamilyName(doc)
    for key, value in RampTypes.items():
        if(key in BUILTIN_RAMP_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids

# -------------------------------- In place Ramp types -------------------------------------------------------
# no such thing in Revit!!
