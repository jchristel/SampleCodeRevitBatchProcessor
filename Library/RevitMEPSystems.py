'''
This module contains a number of helper functions relating to Revit MEP systems. 
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
# header used in reports
REPORT_REVITMEPSYSTEMS_HEADER = ['HOSTFILE', 'RevitMEPSystemsTYPEID', 'RevitMEPSystemsTYPENAME']

# duct types are split into three major families
DUCT_OVAL_FAMILY_NAME = 'Oval Duct'
DUCT_ROUND_FAMILY_NAME = 'Round Duct'
DUCT_RECTANGULAR_FAMILY_NAME = 'Rectangular Duct'

# duct major types collection
BUILTIN_DUCT_TYPE_FAMILY_NAMES = [
    DUCT_OVAL_FAMILY_NAME,
    DUCT_ROUND_FAMILY_NAME,
    DUCT_RECTANGULAR_FAMILY_NAME
]

# flex duct types are split into three major families
FLEX_DUCT_REC_FAMILY_NAME = 'Flex Duct Rectangular'
FLEX_DUCT_ROUND_FAMILY_NAME = 'Flex Duct Round'

# flex duct major types collection
BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES = [
    FLEX_DUCT_REC_FAMILY_NAME,
    FLEX_DUCT_ROUND_FAMILY_NAME
]

# conduits types are split into two major families
CONDUIT_WITHFITTING_FAMILY_NAME = 'Conduit with Fittings'
CONDUIT_WITHOUTFITTING_FAMILY_NAME = 'Conduit without Fittings'

# conduit major types collection
BUILTIN_CONDUIT_TYPE_FAMILY_NAMES = [
    CONDUIT_WITHFITTING_FAMILY_NAME,
    CONDUIT_WITHOUTFITTING_FAMILY_NAME
]

# cable tray types are split into two major families
CABLETRAY_WITHFITTING_FAMILY_NAME = 'Cable Tray with Fittings'
CABLETRAY_WITHOUTFITTING_FAMILY_NAME = 'Cable Tray without Fittings'

# cable tray major types collection
BUILTIN_CABLETRAY_TYPE_FAMILY_NAMES = [
    CABLETRAY_WITHFITTING_FAMILY_NAME,
    CABLETRAY_WITHOUTFITTING_FAMILY_NAME
]

# pipe types exist in one major families
PIPE_FAMILY_NAME = 'Pipe Types'

# pipes major types collection
BUILTIN_PIPE_TYPE_FAMILY_NAMES = [
    PIPE_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

# listSource    list to be added to
# listMerge     list containing new values to be added to listSource
def MergeIntoUniquList(listSource, listMerge):
    '''merges the second list into the first by adding elements from second list which are not already in first list'''
    for i in listMerge:
        if (i not in listSource):
            listSource.append(i)
    return listSource

# --------------------------------------------- system utility functions ------------------

# doc:   current model document
def GetAllDuctTypesByCategory(doc):
    ''' this will return a filtered element collector of all duct types in the model'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_DuctCurves).WhereElementIsElementType()
    return collector

# doc   current model document
def GetDuctTypesByClass(doc):
    ''' this will return a filtered element collector of all duct types in the model'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbm.DuctType)

# doc:   current model document
def GetAllFlexDuctTypesByCategory(doc):
    ''' this will return a filtered element collector of all flex duct types in the model'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_FlexDuctCurves).WhereElementIsElementType()
    return collector

# doc   current model document
def GetFlexDuctTypesByClass(doc):
    ''' this will return a filtered element collector of all flex duct types in the model'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbm.FlexDuctType)

# doc:   current model document
def GetAllConduitTypesByCategory(doc):
    ''' this will return a filtered element collector of all conduit types in the model'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Conduit).WhereElementIsElementType()
    return collector

# doc   current model document
def GetConduitTypesByClass(doc):
    ''' this will return a filtered element collector of all conduit types in the model'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.ConduitType)

# doc:   current model document
def GetAllCableTrayTypesByCategory(doc):
    ''' this will return a filtered element collector of all cable tray types in the model'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_CableTray).WhereElementIsElementType()
    return collector

# doc   current model document
def GetCableTrayTypesByClass(doc):
    ''' this will return a filtered element collector of all cable tray types in the model'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.CableTrayType)

# doc:   current model document
def GetAllPipeTypesByCategory(doc):
    ''' this will return a filtered element collector of all pipe types in the model'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_PipeCurves).WhereElementIsElementType()
    return collector

# doc   current model document
def GetPipeTypesByClass(doc):
    ''' this will return a filtered element collector of all pipe types in the model'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbp.PipeType)

# -------------------------------- none in place instances -------------------------------------------------------

# TODO check these actually work...

# doc   current model document
def GetAllDuctInstancesInModelByCategory(doc):
    ''' returns all Duct elements placed in model by category...'''
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllDuctInstancesInModelByClass(doc):
    ''' returns all duct elements placed in model by class...ignores in place'''
    return rdb.FilteredElementCollector(doc).OfClass(rdbm.DuctType).WhereElementIsNotElementType()

# doc   current model document
def GetAllFlexDuctInstancesInModelByCategory(doc):
    ''' returns all flex flex Duct elements placed in model by category...'''
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_FlexDuctCurves).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllFlexDuctInstancesInModelByClass(doc):
    ''' returns all flex duct elements placed in model by class...ignores in place'''
    return rdb.FilteredElementCollector(doc).OfClass(rdbm.FlexDuctType).WhereElementIsNotElementType()

# doc:   current model document
def GetAllConduitInstancesByCategory(doc):
    ''' this will return a filtered element collector of all conduit instances in the model by category'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Conduit).WhereElementIsNotElementType()
    return collector

# doc   current model document
def GetConduitInstancesByClass(doc):
    ''' this will return a filtered element collector of all conduit instances in the model by class'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.ConduitType).WhereElementIsNotElementType()

# doc:   current model document
def GetAllCableTrayInstancesByCategory(doc):
    ''' this will return a filtered element collector of all cable tray instances in the model by category'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_CableTray).WhereElementIsNotElementType()
    return collector

# doc   current model document
def GetCableTrayInstancesByClass(doc):
    ''' this will return a filtered element collector of all cable tray instances in the model by class'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbe.CableTrayType).WhereElementIsNotElementType()

# doc:   current model document
def GetAllPipeInstancesByCategory(doc):
    ''' this will return a filtered element collector of all pipe instances in the model by category'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType()
    return collector

# doc   current model document
def GetPipeInstancesByClass(doc):
    ''' this will return a filtered element collector of all pipe instances in the model by class'''
    return  rdb.FilteredElementCollector(doc).OfClass(rdbp.PipeType).WhereElementIsNotElementType()

# -------------------------------- MEP system types -------------------------------------------------------

# doc   current model document
def GetAllDuctTypeIdsInModelByCategory(doc):
    ''' returns all Duct element types available placed in model '''
    ids = []
    colCat = GetAllDuctTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllDuctTypeIdsInModelByClass(doc):
    ''' returns all Duct element types available placed in model '''
    ids = []
    colClass = GetDuctTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

# doc   current model document
def GetAllFlexDuctTypeIdsInModelByCategory(doc):
    ''' returns all flex Duct element types available placed in model '''
    ids = []
    colCat = GetAllFlexDuctTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllFlexDuctTypeIdsInModelByClass(doc):
    ''' returns all flex Duct element types available placed in model '''
    ids = []
    colClass = GetFlexDuctTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

# doc   current model document
def GetAllConduitTypeIdsInModelByCategory(doc):
    ''' returns all conduit element types available placed in model '''
    ids = []
    colCat = GetAllConduitTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllConduitTypeIdsInModelByClass(doc):
    ''' returns all conduit element types available placed in model '''
    ids = []
    colClass = GetConduitTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllCableTrayTypeIdsInModelByCategory(doc):
    ''' returns all cable tray element types available placed in model '''
    ids = []
    colCat = GetAllCableTrayTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllCableTrayTypeIdsInModelByClass(doc):
    ''' returns all cable tray element types available placed in model '''
    ids = []
    colClass = GetCableTrayTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current model document
def GetAllPipeTypeIdsInModelByCategory(doc):
    ''' returns all pipe element types available placed in model '''
    ids = []
    colCat = GetAllPipeTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllPipeTypeIdsInModelByClass(doc):
    ''' returns all pipe element types available placed in model '''
    ids = []
    colClass = GetPipeTypesByClass(doc)
    ids = com.GetIdsFromElementCollector (colClass)
    return ids

# doc   current document
def GetUsedDuctTypeIds(doc):
    ''' returns all used in duct type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllDuctTypeIdsInModelByCategory, 1)
    return ids

# doc   current document
def GetUsedFlexDuctTypeIds(doc):
    ''' returns all used in flex duct type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllFlexDuctTypeIdsInModelByCategory, 1)
    return ids

# doc   current document
def GetUsedConduitTypeIds(doc):
    ''' returns all used in conduit type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllConduitTypeIdsInModelByCategory, 1)
    return ids

# doc   current document
def GetUsedCableTrayTypeIds(doc):
    ''' returns all used in cable tray type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCableTrayTypeIdsInModelByCategory, 1)
    return ids

# doc   current document
def GetUsedPipeTypeIds(doc):
    ''' returns all used in pipe type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllPipeTypeIdsInModelByCategory, 1)
    return ids

# doc   current document
def GetUnUsedDuctTypeIds(doc):
    ''' returns all unused in duct type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllDuctTypeIdsInModelByCategory, 0)
    return ids

# doc   current document
def GetUnUsedFlexDuctTypeIds(doc):
    ''' returns all unused in flex duct type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllFlexDuctTypeIdsInModelByCategory, 0)
    return ids

# doc   current document
def GetUnUsedConduitTypeIds(doc):
    ''' returns all unused in conduit type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllConduitTypeIdsInModelByCategory, 0)
    return ids

# doc   current document
def GetUnUsedCableTrayTypeIds(doc):
    ''' returns all unused in cable tray type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCableTrayTypeIdsInModelByCategory, 0)
    return ids

# doc   current document
def GetUnUsedPipeTypeIds(doc):
    ''' returns all unused in pipe type ids '''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllPipeTypeIdsInModelByCategory, 0)
    return ids


# -------------------------------- purge MEP system types -------------------------------------------------------

# famTypeIds        symbol(type) ids of a family
# usedTypeIds       symbol(type) ids in use in a project
def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    ''' returns false if any symbols (types) of a family are in use in a model'''
    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match

# collector   fltered element collector containing system type elments 
# dic         dictionary containing key: system type family name, value: list of ids
def BuildTypeDictionary(collector, dic):
    '''returns the dictioanry passt in with keys and or values added retrieved from collector passt in'''
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            # todo : check WallKind Enum???
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortTypesByFamilyName(doc, typeGetter):
    # get all Wall Type Elements
    wts = typeGetter(doc)
    usedWts = {}
    usedWts = BuildTypeDictionary(wts, usedWts)
    return usedWts

# doc                   current model document
# allTypeIDGetter       gets all available system type ids as a collector
# allTypesGetter        gets all available system types as a collector
# builtInFamilyTypeNames    list containing alll available major type(families?) names
def GetUnUsedMEPSystemTypeIdsToPurge(doc, allTypeIDGetter, allTypesGetter, builtInFamilyTypeNames):
    '''returns ids of unsued system types. Takes into accounts whether they belong to a major category and how many are left
    (leaves on behind) since the last one cannot be purged'''
    ids = com.GetUsedUnusedTypeIds(doc, allTypeIDGetter, 0)
    # make sure there is at least on Stair type per system family left in model
    types = SortTypesByFamilyName(doc, allTypesGetter)
    for key, value in types.items():
        if(key in builtInFamilyTypeNames ):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


# doc   current document
def GetUnUsedDuctTypeIdsToPurge(doc):
    ''' returns all unused in duct type ids. Note there are three major types:
    - Rectangular Duct
    - Round Duct
    - Oval Duct'''
    ids = GetUnUsedMEPSystemTypeIdsToPurge(doc,GetAllDuctTypeIdsInModelByCategory, GetAllDuctTypesByCategory, BUILTIN_DUCT_TYPE_FAMILY_NAMES)
    return ids

# doc   current document
def GetUnUsedFlexDuctTypeIdsToPurge(doc):
    ''' returns all unused in flex duct type ids. Note there are two major types:
    - Rectangular flex Duct
    - Round flex Duct'''
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
