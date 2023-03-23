'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit curtain walls helper functions.
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


from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_CURTAINWALL_ELEMENTS_HEADER = ['HOSTFILE', 'CURTAINWALL_ELEMENT_TYPEID', 'ReplaceMeTYPENAME']

#: Built in family name for empty system panel
CURTAINWALL_PANEL_EMPTY_FAMILY_NAME = 'Empty System Panel'
#: Built in family name for empty system panel
CURTAINWALL_PANEL_SYSTEM_FAMILY_NAME = 'Empty System Panel'
#: Built in family name for V-shaped mullion
CURTAINWALL_MULLION_V_FAMILY_NAME = 'V Corner Mullion'
#: Built in family name for circular mullion
CURTAINWALL_MULLION_CIRCULAR_FAMILY_NAME = 'Circular Mullion'
#: Built in family name for quad corner mullion
CURTAINWALL_MULLION_QUAD_FAMILY_NAME = 'Quad Corner Mullion'
#: Built in family name for L-shaped corner mullion
CURTAINWALL_MULLION_L_FAMILY_NAME = 'L Corner Mullion'
#: Built in family name for rectangular mullion
CURTAINWALL_MULLION_RECT_FAMILY_NAME = 'Rectangular Mullion'
#: Built in family name for trapezoid corner mullion
CURTAINWALL_MULLION_TRAPEZ_FAMILY_NAME = 'Trapezoid Corner Mullion'

BUILTIN_TYPE_FAMILY_NAMES = [
    CURTAINWALL_PANEL_EMPTY_FAMILY_NAME,
    CURTAINWALL_PANEL_SYSTEM_FAMILY_NAME,
    CURTAINWALL_MULLION_V_FAMILY_NAME,
    CURTAINWALL_MULLION_CIRCULAR_FAMILY_NAME,
    CURTAINWALL_MULLION_QUAD_FAMILY_NAME,
    CURTAINWALL_MULLION_L_FAMILY_NAME,
    CURTAINWALL_MULLION_RECT_FAMILY_NAME,
    CURTAINWALL_MULLION_TRAPEZ_FAMILY_NAME
]

#: category filter for all element filters by category
CURTAINWALL_ELEMENTS_CATEGORY_FILTER = List[rdb.BuiltInCategory] ([
        rdb.BuiltInCategory.OST_CurtainWallPanels,
        rdb.BuiltInCategory.OST_CurtainWallMullions
    ])


# --------------------------------------------- utility functions ------------------

def GetAllCurtainWallElementTypesByCategory(doc):
    '''
    Gets a filtered element collector of all curtain wall element types in the model:

    Filters by multiple categories.

    - curtain wall panels
    - curtain wall mullions
    - in place family symbols!
    

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing curtain wall element types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    multiCatFilter = rdb.ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORY_FILTER )
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    return collector

def BuildCurtainWallElementTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    Keys are built in curtain wall element type names.
    TODO: this code repeats across a number of modules. Use generic instead!

    :param collector: A filtered element collector containing curtain wall element types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: curtain wall element type name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)

    :return: A dictionary containing key: built in curtain wall element type  name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortCurtainWallElementTypesByFamilyName(doc):
    '''
    Returns a dictionary containing all curtain wall element types in the model.

    Key values are as per BUILTIN_TYPE_FAMILY_NAMES.
    TODO: This code repeats across a number of modules. Use generic instead!
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: curtain wall element type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    '''

    # get all CurtainWallElement types including in place wall families
    wts_two = GetAllCurtainWallElementTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildCurtainWallElementTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place or loadable Curtain Wall Element types -------------------------------------------------------

def GetCurtainWallElementInstancesInModelByCategory(doc):
    '''
    Gets all CurtainWallElement elements instances placed in model.

    Includes:

    - curtain wall panels
    - curtain wall mullions

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing curtain wall element types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    multiCatFilter = rdb.ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORY_FILTER )
    return rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType()

def GetAllCurtainWallElementTypeIdsInModelByCategory(doc):
    '''
    Gets all Curtain Wall Element element type ids available in model.

    Includes:

    - curtain wall panels
    - curtain wall mullions
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    colCat = GetAllCurtainWallElementTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllCurtainWallElementTypesByCategoryExclInPlace(doc):
    '''
    Gets all Curtain Wall Element element type available in model. Excludes in place family symbols.

    Includes:

    - curtain wall panels
    - curtain wall mullions
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementType
    '''

    collector = GetAllCurtainWallElementTypesByCategory(doc)
    elements=[]
    for c in collector:
        if(c.GetType() != rdb.FamilySymbol):
            elements.append(c)
    return elements

def GetAllCurtainWallElementTypeIdsByCategoryExclSymbols(doc):
    '''
    Gets all Curtain Wall Element element type ids available in model. Excludes in place family symbols.

    Includes:

    - curtain wall panels
    - curtain wall mullions
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    collector = GetAllCurtainWallElementTypesByCategory(doc)
    ids=[]
    for c in collector:
        if(c.GetType() != rdb.FamilySymbol):
            ids.append(c.Id)
    return ids

def GetUsedCurtainWallElementTypeIds(doc):
    '''
    Gets all used Curtain Wall Element element type ids available in model.

    Used: at least one instance of this type is placed in the model.
    Includes:

    - curtain wall panels
    - curtain wall mullions
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallElementTypeIdsInModelByCategory, 1)
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
 
def GetUnusedNonSymbolCurtainWallElementTypeIdsToPurge(doc):
    '''
    Gets all unused Curtain Wall Element element type ids which can be safely deleted from the model.

    This method can be used to safely delete unused in curtain wall element types. There is no requirement by Revit to have at least one\
        curtain wall element definition in the model.
    
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused in curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallElementTypeIdsByCategoryExclSymbols, 0)
    # unlike other element types, here I do NOT make sure there is at least on curtain wall element type per system family left in model!!
    return ids


# -------------------------------- loadable Curtain Wall Element types -------------------------------------------------------

def GetAllCurtainWallNonSharedSymbolIdsByCategory(doc):
    '''
    Gets a list of all loadable, non shared, family symbols (types) in the model of categories:

    - curtain wall panels
    - curtain wall mullions
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    multiCatFilter = rdb.ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORY_FILTER )
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    for c in collector:
        if(c.GetType() == rdb.FamilySymbol):
            fam = c.Family
            pValue = rParaGet.get_built_in_parameter_value(fam, rdb.BuiltInParameter.FAMILY_SHARED)
            if(pValue != None and  pValue == 'No' and c.Id not in ids):
                ids.append(c.Id)
    return ids

def GetUsedCurtainWallSymbolIds(doc):
    '''
    Gets a list of all used loadable, non shared, family symbols (types) in the model of categories:

    - curtain wall panels
    - curtain wall mullions

    Used: at least one family instance of this symbol (type) is placed in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallNonSharedSymbolIdsByCategory, 1)
    return ids

def GetUnusedCurtainWallSymbolIds(doc):
    '''
    Gets a list of all used loadable, non shared, family symbols (types) in the model of categories:

    - curtain wall panels
    - curtain wall mullions

    Unused: Not one family instance of this symbol (type) is placed in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCurtainWallNonSharedSymbolIdsByCategory, 0)
    return ids

# doc   current document
def GetUnusedICurtainWallSymbolIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of curtain wall element families which can be safely deleted from the model.

    This method can be used to safely delete unused curtain wall element types. There is no requirement by Revit to have at least one\
        in place wall definition in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused curtain wall element symbols (types) and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedCurtainWallSymbolIds)
    return ids
