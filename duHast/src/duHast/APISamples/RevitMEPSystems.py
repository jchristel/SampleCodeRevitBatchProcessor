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

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Mechanical as rdbM
import Autodesk.Revit.DB.Electrical as rdbE
import Autodesk.Revit.DB.Plumbing as rdbP

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_REVIT_MEP_SYSTEMS_HEADER = ['HOSTFILE', 'RevitMEPSystemsTYPEID', 'RevitMEPSystemsTYPENAME']

# Duct types are split into three major families
#: Built in family name for oval ducting
DUCT_OVAL_FAMILY_NAME = 'Oval Duct'
#: Built in family name for round ducting
DUCT_ROUND_FAMILY_NAME = 'Round Duct'
#: Built in family name for rectangular ducting
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
CONDUIT_WITH_FITTING_FAMILY_NAME = 'Conduit with Fittings'
#: Built in family name for conduits without fittings
CONDUIT_WITHOUT_FITTING_FAMILY_NAME = 'Conduit without Fittings'

#: List of all Built in conduit family names
BUILTIN_CONDUIT_TYPE_FAMILY_NAMES = [
    CONDUIT_WITH_FITTING_FAMILY_NAME,
    CONDUIT_WITHOUT_FITTING_FAMILY_NAME
]

# cable tray types are split into two major families
#: Built in family name for cable tray with fittings
CABLE_TRAY_WITH_FITTING_FAMILY_NAME = 'Cable Tray with Fittings'
#: Built in family name for cable tray without fittings
CABLET_RAY_WITHOUT_FITTING_FAMILY_NAME = 'Cable Tray without Fittings'

#: List of all Built in cable tray family names
BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES = [
    CABLE_TRAY_WITH_FITTING_FAMILY_NAME,
    CABLET_RAY_WITHOUT_FITTING_FAMILY_NAME
]

# pipe types exist in one major families
#: Built in family name for pipes
PIPE_FAMILY_NAME = 'Pipe Types'

#: List of all Built in pipe family names
BUILTIN_PIPE_TYPE_FAMILY_NAMES = [
    PIPE_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

def MergeIntoUniqueList(listSource, listMerge):
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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbM.DuctType)

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbE.ConduitType)

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbE.CableTrayType)

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

    return rdb.FilteredElementCollector(doc).OfClass(rdbM.DuctType).WhereElementIsNotElementType()

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbE.ConduitType).WhereElementIsNotElementType()

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

    return  rdb.FilteredElementCollector(doc).OfClass(rdbE.CableTrayType).WhereElementIsNotElementType()

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
    Compares two lists of element ids and returns False if any element id in first list is not in the second list.
    
    Returns False if any symbols (types) of a family (first list) are in use in a model (second list).
    
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

def BuildTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    TODO: similar function exists in Walls module. Consider more generic function.

    :param collector: A filtered element collector containing railing type elements of family symbols
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
    Gets the ids of unused MEP system types. 
    
    In the case that no mep system instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one mep system type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param allTypeIDGetter: Function getting all available system type ids as a list.
    :type allTypeIDGetter: func(doc) -> List Autodesk.Revit.ED.ElementId
    :param allTypesGetter: Function getting all available system types as a collector.
    :type allTypesGetter: func(doc) -> Autodesk.Revit.DB.FilteredElementCollector
    :param builtInFamilyTypeNames: List containing all available major type names.
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
    Gets all unused duct type ids. 

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
    Gets all unused flex duct type ids. 

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

def GetUnUsedConduitTypeIdsToPurge(doc):
    '''
    Gets all unused conduit type ids. 

    This method can be used to safely delete unused conduit types:
    In the case that no conduit instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one conduit type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllConduitTypeIdsInModelByCategory, GetAllConduitTypesByCategory, BUILTIN_CONDUIT_TYPE_FAMILY_NAMES)
    return ids

def GetUnUsedCableTrayTypeIdsToPurge(doc):
    '''
    Gets all unused cable tray type ids. 

    This method can be used to safely delete unused cable tray types:
    In the case that no cable tray instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one cable tray type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllCableTrayTypeIdsInModelByCategory, GetAllCableTrayTypesByCategory, BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES)
    return ids

def GetUnUsedPipeTypeIdsToPurge(doc):
    '''
    Gets all unused pipe type ids. 

    This method can be used to safely delete unused pipe types:
    In the case that no pipe instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one pipe type definition to be in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc, GetAllPipeTypeIdsInModelByCategory, GetAllPipeTypesByCategory, BUILTIN_PIPE_TYPE_FAMILY_NAMES)
    return ids


# -------------------------------- loaded families which can be used in system types --------------------------------

'''
Properties of system types which can use symbols: (note: RoutingPreferenceManager may contain multiple rules per connection type!)

- Cross
- Elbow
- MultiShapeTransition
- Tap
- Tee
- Transition
- Union

'''

#: List of loadable built in family categories for duct related elements.
CATS_LOADABLE_DUCTS = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_DuctAccessory,
    rdb.BuiltInCategory.OST_DuctTerminal,
    rdb.BuiltInCategory.OST_DuctFitting
])

#: List of loadable built in family categories for cable tray related elements.
CATS_LOADABLE_CABLE_TRAYS = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_CableTrayFitting
])

#: List of loadable built in family categories for conduit related elements.
CATS_LOADABLE_CONDUITS = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_ConduitFitting
])

#: List of loadable built in family categories for pipe related elements.
CATS_LOADABLE_PIPES = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_PipeAccessory,
    rdb.BuiltInCategory.OST_PipeFitting
])

#: List of routing reference rule group types
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

def GetUniqueIdsOfUsedSymbolsFromSystemTypeId(doc, systemTypeId):
    '''
    Gets list of unique symbol ids used in a single system type property.

    List can be empty if an exception during processing occurred.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param systemTypeId: MEP system type id (pipe, conduit, duct, cable tray)
    :type systemTypeId: Autodesk.Revit.DB.ElementId

    :return: List of unique ids representing family symbols used in a system.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''
    
    ids = []
    el = doc.GetElement(systemTypeId)
    try:
        unfilteredElements = [el.Cross, el.Elbow, el.MultiShapeTransition, el.Tap, el.Tee, el.Transition, el.Union]
        for unfilteredElement in unfilteredElements:
            if (unfilteredElement != None):
                if (unfilteredElement.Id != rdb.ElementId.InvalidElementId and unfilteredElement.Id not in ids):
                    ids.append(unfilteredElement.Id)
        #check if there is a RoutingPreferenceManager object...it may have some more symbols in its rules
        if(el.RoutingPreferenceManager != None):
            # routing manager got a list RoutingReferenceRule objects
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

def GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, systemTypeIds):
    '''
    Gets a list of unique symbol ids used in these MEP system type properties:

    - Cross
    - Elbow
    - MultiShapeTransition
    - Tap
    - Tee
    - Transition
    - Union

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param systemTypeIds: List of MEP system type id belonging to pipe, conduit, duct or cable tray.
    :type systemTypeIds: List Autodesk.Revit.DB.ElementId

    :return: List of unique ids representing family symbols used in mep systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for systemTypeId in systemTypeIds:
        idsUnfiltered = GetUniqueIdsOfUsedSymbolsFromSystemTypeId(doc, systemTypeId)
        ids = MergeIntoUniqueList(ids, idsUnfiltered)
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

def GetSymbolIdsUsedInConduitTypes(doc):
    '''
    Gets a list of unique symbol ids used in system type properties of conduit types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of unique ids representing family symbols used in conduit systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    tyeIds = GetAllConduitTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
    return ids

def GetSymbolIdsUsedInCableTrayTypes(doc):
    '''
    Gets a list of unique symbol ids used in system type properties of cable tray types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of unique ids representing family symbols used in cable tray systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    tyeIds = GetAllCableTrayTypeIdsInModelByCategory(doc)
    ids = GetUniqueIdsOfUsedSymbolsFromSystemTypeIds(doc, tyeIds)
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

# --------------------------------------- symbols available in model -------------------------------

def GetSymbolIdsForMEPSystemTypes(doc, categoryList, systemTypeName):
    '''
    Gets list of symbol ids belonging to provided categories loaded in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param categoryList: List of built in categories to filter symbols by.
    :type categoryList: list Autodesk.Revit.DB.BuiltInCategory
    :param systemTypeName: Used in exception message to identify the mep system
    :type systemTypeName: str

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    try:
        multiCatFilter = rdb.ElementMulticategoryFilter(categoryList)
        col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(multiCatFilter)
        ids = com.GetIdsFromElementCollector (col)
    except Exception as ex:
        print (systemTypeName+ ' threw exception: ' + str(ex))
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

def GetSymbolIdsForCableTrayTypesInModel(doc):
    '''
    Gets list of symbol ids of the following categories:
    
    - BuiltInCategory.OST_CableTrayFitting
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_CABLE_TRAYS, 'GetSymbolIdsForCableTrayTypes')
    return ids

def GetSymbolIdsForConduitTypesInModel(doc):
    '''
    Gets list of symbol ids of the following categories:
    
    - BuiltInCategory.OST_ConduitFitting
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = GetSymbolIdsForMEPSystemTypes(doc, CATS_LOADABLE_CONDUITS, 'GetSymbolIdsForConduitTypes')
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

# -------------------------------- purge loaded families which can be used in system types --------------------------------

def GetUsedDuctAndFlexDuctSymbolIds(doc):
    '''
    Gets all used duct and flex duct symbol ids of categories
    
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting

    Used: at least instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForDuctTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInDuctTypes(doc)
    idsUsedInFlexTypes = GetSymbolIdsUsedInFlexDuctTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    ids = MergeIntoUniqueList(ids, idsUsedInFlexTypes)
    return ids

def GetUnUsedDuctAndFlexDuctSymbolIds(doc):
    '''
    Gets all unused duct and flex duct symbol ids of categories
    
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting

    Unused: not one instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = GetUsedDuctAndFlexDuctSymbolIds(doc)
    idsAvailable = GetSymbolIdsForDuctTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

def GetUnUsedDuctAndFlexDuctSymbolIdsForPurge(doc):
    '''
    Gets all unused duct and flex duct symbol ids of categories
    
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting

    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused duct symbols and families from the model.
   
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedDuctAndFlexDuctSymbolIds)
    return ids

def GetUsedCableTraySymbolIds(doc):
    '''
    Gets all used cable tray symbol ids of categories
    
    - BuiltInCategory.OST_CableTrayFitting
   
    Used: at least instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''
    
    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForCableTrayTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInCableTrayTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    return ids

def GetUnUsedCableTraySymbolIds(doc):
    '''
    Gets all unused cable tray symbol ids of categories
    
    - BuiltInCategory.OST_CableTrayFitting

    Unused: not one instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = GetUsedCableTraySymbolIds(doc)
    idsAvailable = GetSymbolIdsForCableTrayTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

def GetUnUsedCableTraySymbolIdsForPurge(doc):
    '''
    Gets all unused cable tray symbol ids of categories
    
    - BuiltInCategory.OST_CableTrayFitting

    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused cable tray symbols and families from the model.
   
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''
   
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedCableTraySymbolIds)
    return ids

def GetUsedConduitSymbolIds(doc):
    '''
    Gets all used conduit symbol ids of categories
    
    - BuiltInCategory.OST_ConduitFitting
   
    Used: at least instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForConduitTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInConduitTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    return ids

def GetUnUsedConduitSymbolIds(doc):
    '''
    Gets all unused conduit symbol ids of categories
    
    - BuiltInCategory.OST_ConduitFitting

    Unused: not one instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = GetUsedConduitSymbolIds(doc)
    idsAvailable = GetSymbolIdsForConduitTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

def GetUnUsedConduitSymbolIdsForPurge(doc):
    '''
    Gets all unused conduit symbol ids of categories
    
    - BuiltInCategory.OST_ConduitFitting

    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused conduit symbols and families from the model.
   
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedConduitSymbolIds)
    return ids

def GetUsedPipeSymbolIds(doc):
    '''
    Gets all used pipe symbol ids of categories
    
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting
   
    Used: at least instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsInModel = com.GetUsedUnusedTypeIds(doc, GetSymbolIdsForPipeTypesInModel, 1)
    idsUsedInTypes = GetSymbolIdsUsedInPipeTypes(doc)
    ids = MergeIntoUniqueList(ids, idsInModel)
    ids = MergeIntoUniqueList(ids, idsUsedInTypes)
    return ids

def GetUnUsedPipeSymbolIds(doc):
    '''
    Gets all unused pipe symbol ids of categories
    
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting

    Unused: not one instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = GetUsedPipeSymbolIds(doc)
    idsAvailable = GetSymbolIdsForPipeTypesInModel(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

def GetUnUsedPipeSymbolIdsForPurge(doc):
    '''
    Gets all unused pipe symbol ids of categories
    
    - BuiltInCategory.OST_PipeAccessory,
    - BuiltInCategory.OST_PipeFitting

    Unused: not one instance per symbol is placed in the model.
    This method can be used to safely delete unused pipe symbols and families from the model.
   
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedPipeSymbolIds)
    return ids
