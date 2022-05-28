'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit MEP systems helper functions. 
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
from System.Collections.Generic import List

import sys

import RevitCommonAPI as com
import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Mechanical as rdbm
import Autodesk.Revit.DB.Electrical as rdbe
import Autodesk.Revit.DB.Plumbing as rdbp


clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_REVITMEPSYSTEMS_HEADER = ['HOSTFILE', 'RevitMEPSystemsTYPEID', 'RevitMEPSystemsTYPENAME']

# Duct types are split into three major families
#: Built in family name for oval ducting
DUCT_OVAL_FAMILY_NAME = 'Oval Duct'
#: Built in family name for round ducting
DUCT_ROUND_FAMILY_NAME = 'Round Duct'
#: Built in family name for rectangula ducting
DUCT_RECTANGULAR_FAMILY_NAME = 'Rectangular Duct'

#: List of all Built in ducting family names
BUILTIN_DUCT_TYPE_FAMILY_NAMES = [
    DUCT_OVAL_FAMILY_NAME,
    DUCT_ROUND_FAMILY_NAME,
    DUCT_RECTANGULAR_FAMILY_NAME
]

# flex duct types are split into two major families
#: Built in family name for rectangular flex ducting
FLEX_DUCT_REC_FAMILY_NAME = 'Flex Duct Rectangular'
#: Built in family name for round flex ducting
FLEX_DUCT_ROUND_FAMILY_NAME = 'Flex Duct Round'

#: List of all Built in flex ducting family names
BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES = [
    FLEX_DUCT_REC_FAMILY_NAME,
    FLEX_DUCT_ROUND_FAMILY_NAME
]

# conduits types are split into two major families
#: Built in family name for conduits with fittings
CONDUIT_WITHFITTING_FAMILY_NAME = 'Conduit with Fittings'
#: Built in family name for conduits without fittings
CONDUIT_WITHOUTFITTING_FAMILY_NAME = 'Conduit without Fittings'

#: List of all Built in conduit family names
BUILTIN_CONDUIT_TYPE_FAMILY_NAMES = [
    CONDUIT_WITHFITTING_FAMILY_NAME,
    CONDUIT_WITHOUTFITTING_FAMILY_NAME
]

# cable tray types are split into two major families
#: Built in family name for cable tray with fittings
CABLETRAY_WITHFITTING_FAMILY_NAME = 'Cable Tray with Fittings'
#: Built in family name for cable tray without fittings
CABLETRAY_WITHOUTFITTING_FAMILY_NAME = 'Cable Tray without Fittings'

#: List of all Built in cable tray family names
BUILTIN_CABLETRAY_TYPE_FAMILY_NAMES = [
    CABLETRAY_WITHFITTING_FAMILY_NAME,
    CABLETRAY_WITHOUTFITTING_FAMILY_NAME
]

# pipe types exist in one major families
#: Built in family name for pipes
PIPE_FAMILY_NAME = 'Pipe Types'

#: List of all Built in pipe family names
BUILTIN_PIPE_TYPE_FAMILY_NAMES = [
    PIPE_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

def MergeIntoUniquList(listSource, listMerge):
    '''
    Merges the second list into the first by adding elements from second list which are not already in first list.

    TODO: Consider more generic code!

    :param listSource: List to add unique values to.
    :type listSource: list var
    :param listMerge: List containing values.
    :type listMerge: list var

    :return: List of unique objects.
    :rtype: list var
    '''

    for i in listMerge:
        if (i not in listSource):
            listSource.append(i)
    return listSource

# --------------------------------------------- system utility functions ------------------

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbm.DuctType)

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbm.FlexDuctType)

def GetAllConduitTypesByCategory(doc):
    '''
    Gets a filtered element collector of all conduit types in the model.

    - with fittings
    - without fittings

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of conduit types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Conduit).WhereElementIsElementType()
    return collector

def GetConduitTypesByClass(doc):
    '''
    Gets a filtered element collector of all conduit types in the model.

    - with fittings
    - without fittings

    Will exclude in place families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of conduit types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.ConduitType)

def GetAllCableTrayTypesByCategory(doc):
    '''
    Gets a filtered element collector of all cable tray types in the model.

    - with fittings
    - without fittings

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of cable tray types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_CableTray).WhereElementIsElementType()
    return collector

def GetCableTrayTypesByClass(doc):
    '''
    Gets a filtered element collector of all cable tray types in the model.

    - with fittings
    - without fittings

    Will exclude in place families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of cable tray types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.CableTrayType)

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbp.PipeType)

# -------------------------------- none in place instances -------------------------------------------------------

# TODO check these actually work...

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
    
# doc   current model document
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

    return rdb.FilteredElementCollector(doc).OfClass(rdbm.DuctType).WhereElementIsNotElementType()

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

    return rdb.FilteredElementCollector(doc).OfClass(rdbm.FlexDuctType).WhereElementIsNotElementType()

def GetAllConduitInstancesByCategory(doc):
    '''
    Gets all conduit elements placed in model.

    TODO: check these actually work...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of conduit instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Conduit).WhereElementIsNotElementType()
    return collector

def GetConduitInstancesByClass(doc):
    '''
    Gets all conduit elements placed in model.

    Will exclude in place families.
    TODO: check these actually work...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of conduit instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.ConduitType).WhereElementIsNotElementType()

def GetAllCableTrayInstancesByCategory(doc):
    '''
    Gets all cable tray elements placed in model.

    TODO: check these actually work...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of cable tray instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_CableTray).WhereElementIsNotElementType()
    return collector

def GetCableTrayInstancesByClass(doc):
    '''
    Gets all cable tray elements placed in model.

    Will exclude in place families.
    TODO: check these actually work...

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of cable tray instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.CableTrayType).WhereElementIsNotElementType()

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbp.PipeType).WhereElementIsNotElementType()

# -------------------------------- MEP system types -------------------------------------------------------

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

def GetAllConduitTypeIdsInModelByCategory(doc):
    '''
    Gets all conduit type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllConduitTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllConduitTypeIdsInModelByClass(doc):
    '''
    Gets all conduit type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetConduitTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetAllCableTrayTypeIdsInModelByCategory(doc):
    '''
    Gets all cable tray type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllCableTrayTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllCableTrayTypeIdsInModelByClass(doc):
    '''
    Gets all cable tray type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colClass = GetCableTrayTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

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
    ids = com.GetIdsFromElementCollector (colCat)
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
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

def GetUsedDuctTypeIds(doc):
    '''
    Gets all used duct type ids available in model.

    Unused: at least instance of each of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllDuctTypeIdsInModelByCategory, 1)
    return ids

def GetUsedFlexDuctTypeIds(doc):
    '''
    Gets all used flex duct type ids available in model.

    Unused: at least instance of each of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllFlexDuctTypeIdsInModelByCategory, 1)
    return ids

def GetUsedConduitTypeIds(doc):
    '''
    Gets all used conduit type ids available in model.

    Unused: at least instance of each of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllConduitTypeIdsInModelByCategory, 1)
    return ids

# doc   current document
def GetUsedCableTrayTypeIds(doc):
    '''
    Gets all used cable tray type ids available in model.

    Unused: at least instance of each of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCableTrayTypeIdsInModelByCategory, 1)
    return ids

def GetUsedPipeTypeIds(doc):
    '''
    Gets all used pipe type ids available in model.

    Unused: at least instance of each of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllPipeTypeIdsInModelByCategory, 1)
    return ids

def GetUnUsedDuctTypeIds(doc):
    '''
    Gets all unused duct type ids available in model.

    Unused: not one instance of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllDuctTypeIdsInModelByCategory, 0)
    return ids

def GetUnUsedFlexDuctTypeIds(doc):
    '''
    Gets all unused flex duct type ids available in model.

    Unused: not one instance of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllFlexDuctTypeIdsInModelByCategory, 0)
    return ids

def GetUnUsedConduitTypeIds(doc):
    '''
    Gets all unused conduit type ids available in model.

    Unused: not one instance of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllConduitTypeIdsInModelByCategory, 0)
    return ids

def GetUnUsedCableTrayTypeIds(doc):
    '''
    Gets all unused cable tray type ids available in model.

    Unused: not one instance of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing cable tray types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCableTrayTypeIdsInModelByCategory, 0)
    return ids

# doc   current document
def GetUnUsedPipeTypeIds(doc):
    '''
    Gets all unused pipe type ids available in model.

    Unused: not one instance of these types is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing pipe types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllPipeTypeIdsInModelByCategory, 0)
    return ids


# -------------------------------- purge MEP system types -------------------------------------------------------

def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of element ids and returnds False if any element id in first list is not in the second list.
    
    Returns False if any symbols (types) of a family (first list) are in use in a model (second list).
    
    TODO: repetetive code...Consider generic function!

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

def BuildTypeDictionary(collector, dic):
    '''
    Returns the dictionary passt in with keys and or values added retrieved from collector passt in.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param collector: A filtered element collector containing railing type elments of family symbols
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: dictionary containing key: railing type family name, value: list of ids
    :type dic: Dictionary {str:[Autodesk.Revit.DB.ElementId]}

    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            # todo : check WallKind Enum???
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortTypesByFamilyName(doc, typeGetter):
    '''
    Returns a dictionary where key is the family name and values are ids of types belonging to that family.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeGetter: function returning element types
    :type typeGetter: func(doc) -> Autodesk.Revit.DB.FilteredElementCollector

    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    '''

    # get all Wall Type Elements
    wts = typeGetter(doc)
    usedWts = {}
    usedWts = BuildTypeDictionary(wts, usedWts)
    return usedWts

def GetUnUsedMEPSystemTypeIdsToPurge(doc, allTypeIDGetter, allTypesGetter, builtInFamilyTypeNames):
    '''
    Gets the ids of unsued MEP system types. 
    
    In the case that no mep system instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one mep system type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param allTypeIDGetter: Function getting all available system type ids as a list.
    :type allTypeIDGetter: func(doc) -> List Autodesk.Revit.ED.ElementId
    :param allTypesGetter: Function getting all available system types as a collector.
    :type allTypesGetter: func(doc) -> Autodesk.Revit.DB.FilteredElementCollector
    :param builtInFamilyTypeNames: List containing alll available major type names.
    :type builtInFamilyTypeNames: List str

    :return: A list of ids representing mep system types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, allTypeIDGetter, 0)
    # make sure there is at least on Stair type per system family left in model
    types = SortTypesByFamilyName(doc, allTypesGetter)
    for key, value in types.items():
        if(key in builtInFamilyTypeNames ):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids

def GetUnUsedDuctTypeIdsToPurge(doc):
    '''
    Gets all unused in duct type ids. 

    This method can be used to safely delete unused duct types:
    In the case that no duct instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one duct type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc,GetAllDuctTypeIdsInModelByCategory, GetAllDuctTypesByCategory, BUILTIN_DUCT_TYPE_FAMILY_NAMES)
    return ids

def GetUnUsedFlexDuctTypeIdsToPurge(doc):
    '''
    Gets all unused in flex duct type ids. 

    This method can be used to safely delete unused flex duct types:
    In the case that no flex duct instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one flex duct type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc,GetAllFlexDuctTypeIdsInModelByCategory, GetAllFlexDuctTypesByCategory, BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES)
    return ids

# doc   current document
def GetUnUsedConduitTypeIdsToPurge(doc):
    ''' returns all unused in conduit type ids. Note there are two major types:
    - Conduit with Fittings
    - Conduit without Fittings'''
    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllConduitTypeIdsInModelByCategory, GetAllConduitTypesByCategory, BUILTIN_CONDUIT_TYPE_FAMILY_NAMES)
    return ids

# doc   current document
def GetUnUsedCableTrayTypeIdsToPurge(doc):
    ''' returns all unused in cable tray type ids. Note there are two major types:
    - Cable Tray with Fittings
    - Cable Tray without Fittings'''
    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllCableTrayTypeIdsInModelByCategory, GetAllCableTrayTypesByCategory, BUILTIN_CABLETRAY_TYPE_FAMILY_NAMES)
    return ids

# doc   current document
def GetUnUsedPipeTypeIdsToPurge(doc):
    ''' returns all unused in pipe type ids.'''
    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllPipeTypeIdsInModelByCategory, GetAllPipeTypesByCategory, BUILTIN_PIPE_TYPE_FAMILY_NAMES)
    return ids


# -------------------------------- loaded families which can be used in system types --------------------------------

'''properties of system types which can use symbols: (note: RoutingPreferenceManager may contain multiple rules per connection type!)
Cross
Elbow
MultiShapeTransition
Tap
Tee
Transition
Union
'''
# loadable family categories for duct related elements
CATS_LOADABLE_DUCSTS = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_DuctAccessory,
    rdb.BuiltInCategory.OST_DuctTerminal,
    rdb.BuiltInCategory.OST_DuctFitting
])

# loadable family categories for cable tray related elements
CATS_LOADABLE_CABLETRAYS = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_CableTrayFitting
])

# loadable family categories for conduit related elements
CATS_LOADABLE_CONDUITS = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_ConduitFitting
])

# loadable family categories for pipe related elements
CATS_LOADABLE_PIPES = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_PipeAccessory,
    rdb.BuiltInCategory.OST_PipeFitting
])

ROUTING_PREF_RULE_GROUP_TYPES = [
  rdb.RoutingPreferenceRuleGroupType.Segments,
  rdb.RoutingPreferenceRuleGroupType.Elbows,
  rdb.RoutingPreferenceRuleGroupType.Junctions,
  rdb.RoutingPreferenceRuleGroupType.Crosses,
  rdb.RoutingPreferenceRuleGroupType.Transitions,
  rdb.RoutingPreferenceRuleGroupType.Unions,
  rdb.RoutingPreferenceRuleGroupType.MechanicalJoints,
  rdb.RoutingPreferenceRuleGroupType.TransitionsRectangularToRound,
  rdb.RoutingPreferenceRuleGroupType.TransitionsRectangularToOval,
  rdb.RoutingPreferenceRuleGroupType.TransitionsOvalToRound,
  rdb.RoutingPreferenceRuleGroupType.Caps
]

# doc   current document
# systemTypeId      MEP systemt type id (pipe, conduit, duct, cable tray)
def GetUniqueIdsOfUsedSymbolsFromSystemTypeId(doc, systemTypeId):
    '''returns list of unique symobol ids used in system type properties:
    - Cross
    - Elbow
    - MultiShapeTransition
    - Tap
    - Tee
    - Transition
    - Union
    '''
    ids = []
    el = doc.GetElement(systemTypeId)
    try:
        unfilteredElements = [el.Cross, el.Elbow, el.MultiShapeTransition, el.Tap, el.Tee, el.Transition, el.Union]
        for unfilteredel in unfilteredElements:
            if (unfilteredel != None):
                if (unfilteredel.Id != rdb.ElementId.InvalidElementId and unfilteredel.Id not in ids):
                    ids.append(unfilteredel.Id)
        #check if there is a RoutingPreferenceManager object...it may have some more symbols in its rules
        if(el.RoutingPreferenceManager != None):
            # routing manager got a list RoutingReferencerule objects
            # each of those got a 	MEPPartId property which is what we are after
            rpm = el.RoutingPreferenceManager
            for group in ROUTING_PREF_RULE_GROUP_TYPES:
                # loop over RoutingPreferenceRuleGroupTypes!
                numberOfRules = rpm.GetNumberOfRules(group)
                for i in range(numberOfRules):
                    rule = rpm.GetRule(group, i)
                    if rule.MEPPartId not in ids:
                        ids.append(rule.MEPPartId)
            
            
    except Exception as ex:
        print('System type get used symbol ids threw exception: '+ str(ex))
    return ids

# doc   current document
# systemTypeId      list of MEP systemt type id (pipe, conduit, duct, cable tray)
def GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, systemTypeIds):
    '''returns list of unique symobol ids used in system type properties:
    - Cross
    - Elbow
    - MultiShapeTransition
    - Tap
    - Tee
    - Transition
    - Union
    '''
    ids = []
    for systemTypeId in systemTypeIds:
        idsUnfiltered = GetUniqueIdsOfUsedSymbolsFromSystemTypeId(doc, systemTypeId)
        ids = MergeIntoUniquList(ids, idsUnfiltered)
    return ids

# --------------------------------------- symbols used in MEP system types -------------------------------

# doc   current document
def GetSymbolIdsUsedInDuctTypes(doc):
    '''returns list of unique symobol ids used in system type properties of duct types'''
    ids = []
    tyeIds = GetAllDuctTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids

# doc   current document
def GetSymbolIdsUsedInFlexDuctTypes(doc):
    '''returns list of unique symobol ids used in system type properties of flex duct types'''
    ids = []
    tyeIds = GetAllFlexDuctTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids

# doc   current document
def GetSymbolIdsUsedInConduitTypes(doc):
    '''returns list of unique symobol ids used in system type properties of conduit types'''
    ids = []
    tyeIds = GetAllConduitTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids

# doc   current document
def GetSymbolIdsUsedInCableTrayTypes(doc):
    '''returns list of unique symobol ids used in system type properties of cable tray types'''
    ids = []
    tyeIds = GetAllCableTrayTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids

# doc   current document
def GetSymbolIdsUsedInPipeTypes(doc):
    '''returns list of unique symobol ids used in system type properties of pipe types'''
    ids = []
    tyeIds = GetAllPipeTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids

# --------------------------------------- symbols available in model -------------------------------

# doc   current document
# catgeoryList      built incategories belonging to an MEP system type
# systemTypeName       used in exception message to identify the mep system
def GetSymbolIdsForMEPSystemTypes(doc, catgeoryList, systemTypeName):
    '''returns list of symbol ids used in system types'''
    ids = []
    try:
        multiCatFilter = rdb.ElementMulticategoryFilter(catgeoryList)
        col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(multiCatFilter)
        ids = com.GetIdsFromElementCollector (col)
    except Exception as ex:
        print (systemTypeName+ ' threw exception: ' + str(ex))
    return ids

# doc   current document
def GetSymbolIdsForDuctTypesInModel(doc):
    '''returns list of symobol ids of the following categories:
    BuiltInCategory.OST_DuctAccessory,
    BuiltInCategory.OST_DuctTerminal,
    BuiltInCategory.OST_DuctFitting
    '''
    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_DUCSTS, 'GetSymbolIdsForDuctTypes')
    return ids

# doc   current document
def GetSymbolIdsForFlexDuctTypesInModel(doc):
    '''returns list of symobol ids of the following categories:
    BuiltInCategory.OST_DuctAccessory,
    BuiltInCategory.OST_DuctTerminal,
    BuiltInCategory.OST_DuctFitting
    (same as duct)'''
    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_DUCSTS, 'GetSymbolIdsForDuctTypes')
    return ids

# doc   current document
def GetSymbolIdsForCableTrayTypesInModel(doc):
    '''returns list of symobol ids of the following categories:
    BuiltInCategory.OST_CableTrayFitting
    '''
    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_CABLETRAYS, 'GetSymbolIdsForCableTrayTypes')
    return ids

# doc   current document
def GetSymbolIdsForConduitTypesInModel(doc):
    '''returns list of symobol ids of the following categories:
    BuiltInCategory.OST_ConduitFitting
    '''
    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_CONDUITS, 'GetSymbolIdsForConduitTypes')
    return ids

# doc   current document
def GetSymbolIdsForPipeTypesInModel(doc):
    '''returns list of symobol ids of the following categories:
    BuiltInCategory.OST_PipeAccessory,
    BuiltInCategory.OST_PipeFitting
    '''
    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_PIPES, 'GetSymbolIdsForPipeTypes')
    return ids

# -------------------------------- purge loaded families which can be used in system types --------------------------------

# doc   current document
def GetUsedDuctAndFlexDuctSymbolIds(doc):
    ''' returns all used duct symbol ids of categories
    BuiltInCategory.OST_DuctAccessory,
    BuiltInCategory.OST_DuctTerminal,
    BuiltInCategory.OST_DuctFitting
    '''
    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForDuctTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInDuctTypes(doc)
    idsUsedInFlexTypes = GetSymbolIdsUsedInFlexDuctTypes(doc)
    ids = MergeIntoUniquList(ids, idsInModel)
    ids = MergeIntoUniquList(ids, idsUsedInTypes)
    ids = MergeIntoUniquList(ids, idsUsedInFlexTypes)
    return ids

# doc   current document
def GetUnUsedDuctAndFlexDuctSymbolIds(doc):
    ''' returns all unused duct symbol ids of categories
    BuiltInCategory.OST_DuctAccessory,
    BuiltInCategory.OST_DuctTerminal,
    BuiltInCategory.OST_DuctFitting
    '''
    ids = []
    idsUsed = GetUsedDuctAndFlexDuctSymbolIds(doc)
    idsAvailable = GetSymbolIdsForDuctTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedDuctAndFlexDuctSymbolIdsForPurge(doc):
    '''get all un used duct symbol ids of categories
    BuiltInCategory.OST_DuctAccessory,
    BuiltInCategory.OST_DuctTerminal,
    BuiltInCategory.OST_DuctFitting
    '''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedDuctAndFlexDuctSymbolIds)
    return ids

# doc   current document
def GetUsedCableTraySymbolIds(doc):
    ''' returns all used duct symbol ids of categories
    BuiltInCategory.OST_CableTrayFitting
    '''
    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForCableTrayTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInCableTrayTypes(doc)
    ids = MergeIntoUniquList(ids, idsInModel)
    ids = MergeIntoUniquList(ids, idsUsedInTypes)
    return ids

# doc   current document
def GetUnUsedCableTraySymbolIds(doc):
    ''' returns all unused duct symbol ids of categories
    BuiltInCategory.OST_CableTrayFitting
    '''
    ids = []
    idsUsed = GetUsedCableTraySymbolIds(doc)
    idsAvailable = GetSymbolIdsForCableTrayTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedCableTraySymbolIdsForPurge(doc):
    '''get all un used duct symbol ids of categories
    BuiltInCategory.OST_CableTrayFitting
    '''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedCableTraySymbolIds)
    return ids

# doc   current document
def GetUsedConduitSymbolIds(doc):
    ''' returns all used conduit symbol ids of categories
    BuiltInCategory.OST_ConduitFitting
    '''
    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForConduitTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInConduitTypes(doc)
    ids = MergeIntoUniquList(ids, idsInModel)
    ids = MergeIntoUniquList(ids, idsUsedInTypes)
    return ids

# doc   current document
def GetUnUsedConduitSymbolIds(doc):
    ''' returns all unused conduit symbol ids of categories
    BuiltInCategory.OST_ConduitFitting
    '''
    ids = []
    idsUsed = GetUsedConduitSymbolIds(doc)
    idsAvailable = GetSymbolIdsForConduitTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedConduitSymbolIdsForPurge(doc):
    '''get all un used conduit symbol ids of categories
    BuiltInCategory.OST_ConduitFitting
    '''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedConduitSymbolIds)
    return ids

# doc   current document
def GetUsedPipeSymbolIds(doc):
    ''' returns all used pipe symbol ids of categories
    BuiltInCategory.OST_PipeAccessory,
    BuiltInCategory.OST_PipeFitting
    '''
    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForPipeTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInPipeTypes(doc)
    ids = MergeIntoUniquList(ids, idsInModel)
    ids = MergeIntoUniquList(ids, idsUsedInTypes)
    return ids

# doc   current document
def GetUnUsedPipeSymbolIds(doc):
    ''' returns all unused pipe symbol ids of categories
    BuiltInCategory.OST_PipeAccessory,
    BuiltInCategory.OST_PipeFitting
    '''
    ids = []
    idsUsed = GetUsedPipeSymbolIds(doc)
    idsAvailable = GetSymbolIdsForPipeTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedPipeSymbolIdsForPurge(doc):
    '''get all un used pipe symbol ids of categories
    BuiltInCategory.OST_PipeAccessory,
    BuiltInCategory.OST_PipeFitting
    '''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedPipeSymbolIds)
    return ids
