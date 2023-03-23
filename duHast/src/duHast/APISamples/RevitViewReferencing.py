'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view referencing. 
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
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
import System
from System.Collections.Generic import List

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitFamilyUtils as rFamU
from duHast.APISamples import RevitViews as rView

# import Autodesk
import Autodesk.Revit.DB as rdb

# ------------------------ deprecated -----------------------
# the following element collectors dont seem to return any types ...

# doc:   current model document
def Deprecated_GetAllCallOutTypesByCategory(doc):
    ''' this will return an EMPTY filtered element collector of all call out types in the model in Revit 2019'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Callouts).WhereElementIsElementType()
    return collector

# doc:   current model document
def Deprecated_GetAllReferenceViewTypesByCategory(doc):
    '''this will return an EMPTY filtered element collector of all reference view types in the model in Revit 2019'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_ReferenceViewer).WhereElementIsElementType()
    return collector
 
# doc:   current model document
def Deprecated_GetAllCallOutTypeIdsByCategory(doc):
    ''' this will return an EMPTY filtered element collector of all call out type ids in the model'''
    collector = Deprecated_GetAllCallOutTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# doc:   current model document
def Deprecated_GetAllReferenceViewTypeIdsByCategory(doc):
    ''' this will return an EMPTY filtered element collector of all reference view types in the model'''
    collector = Deprecated_GetAllReferenceViewTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# ---------------------- utility -----------------------

def GetAllCallOutHeadsByCategory(doc):
    '''
    Gets a filtered element collector of all callOut Head symbol (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing call out head symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_CalloutHeads).WhereElementIsElementType()
    return collector

def GetAllElevationHeadsByCategory(doc):
    '''
    Gets a filtered element collector of all elevation symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing elevation symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_ElevationMarks).WhereElementIsElementType()
    return collector

def GetAllSectionHeadsByCategory(doc):
    '''
    Gets a filtered element collector of all section symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing section symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_SectionHeads).WhereElementIsElementType()
    return collector

def GetAllViewContinuationMarkersByCategory(doc):
    '''
    Gets a filtered element collector of all view continuation symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing Continuation Marker symbols.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_ReferenceViewerSymbol)
    return collector

def GetAllReferenceViewElementsByCategory(doc):
    '''
    Gets filtered element collector of all reference view elements in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing reference view elements.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_ReferenceViewer)
    return collector

# ---------------------- view ref types  -----------------------

#: contains the builtin parameter definitions for Call out type ids, section type ids, elevation type ids
VIEW_REFERENCE_PARAMETER_DEF_NAMES = [
    rdb.BuiltInParameter.ELEVATN_TAG,
    rdb.BuiltInParameter.CALLOUT_TAG,
    rdb.BuiltInParameter.SECTION_TAG
]

#: contains the builtin parameter definitions for call out symbol tag ids, section symbol tag ids, elevation symbol tag ids
VIEW_TAG_SYMBOL_PARAMETER_DEF = [
    rdb.BuiltInParameter.CALLOUT_ATTR_HEAD_TAG,
    rdb.BuiltInParameter.ELEV_SYMBOL_ID,
    rdb.BuiltInParameter.SECTION_ATTR_HEAD_TAG,
    rdb.BuiltInParameter.SECTION_ATTR_TAIL_TAG,
    rdb.BuiltInParameter.REFERENCE_VIEWER_ATTR_TAG
]

#: category filter for all view ref categories
VIEW_REF_CATEGORY_FILTER = List[rdb.BuiltInCategory] ([
        rdb.BuiltInCategory.OST_CalloutHeads,
        rdb.BuiltInCategory.OST_ElevationMarks,
        rdb.BuiltInCategory.OST_SectionHeads,
        rdb.BuiltInCategory.OST_ReferenceViewerSymbol
    ])

def GetReferenceTypeIdsFromViewType(viewType):
    '''
    Gets all reference type ids used in view type.

    :param viewType: The view type.
    :type viewType: Autodesk.Revit.DB.ViewType

    :return: dictionary, key: BuiltinParameterDefinition, value: id of a tag
    :rtype: dic{Autodesk.Revit.DB.BuiltinParameterDefinition:[Autodesk.Revit.DB.ElementId]}
    '''

    dic = {}
    for pDef in VIEW_REFERENCE_PARAMETER_DEF_NAMES:
        pValue = rParaGet.get_built_in_parameter_value(viewType, pDef)
        if(pValue != None):
            # there should only ever be one value per key!
            if(dic.has_key(pDef)):
                dic[pDef].append(pValue)
            else:
                dic[pDef] = [pValue]
    return dic

def GetUsedViewReferenceTypeIdData(doc):
    '''
    Gets all view references types in use in the model in a dictionary.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: key is the reference tag type: call out, section or elevation, values are the type ids in use
    :rtype: dictionary {reference tag type: list Autodesk.Revit.DB.ElementIds}
    '''

    dic = {}
    col = rView.GetViewTypes(doc)
    for c in col:
        # get reference types from view types
        referenceTypeByViewType = GetReferenceTypeIdsFromViewType(c)
        # check if already in dictionary , if not append
        for key, value in referenceTypeByViewType.items():
            if(dic.has_key(key)):
                for v in value:
                    if(v not in dic[key]):
                        dic[key].append(v)
            else:
              dic[key] = value
    return dic

def GetAllViewReferenceTypeIdData(doc):
    '''
    Gets all view references types available in the model in a dictionary.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: key is the reference type: call out, section or elevation, values are the type ids in use
    :rtype: dictionary {reference tag type: list Autodesk.Revit.DB.ElementIds}
    '''

    dic = {}
    col = rView.GetViewTypes(doc)
    for c in col:
        # get reference types from view types
        referenceTypeByViewType = GetReferenceTypeIdsFromViewType(c)
        # get all similar types
        for key, value in referenceTypeByViewType.items():
            for v in referenceTypeByViewType[key]:
                type = doc.GetElement(v)
                if(type !=None):
                    allSimTypeIds = type.GetSimilarTypes()
                    for simTypeId in allSimTypeIds:
                        if(dic.has_key(key)):
                            if(simTypeId not in dic[key]):
                                dic[key].append(simTypeId)
                        else:
                            dic[key] = [simTypeId]
    return dic

def GetAllViewReferenceTypeIdDataAsList(doc):
    '''
    Gets all view references type ids available in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing view reference types
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    dic = GetAllViewReferenceTypeIdData(doc)
    ids = []
    for key, value in dic.items():
        if(len(dic[key]) > 0):
            ids = ids + dic[key]
    return ids

def GetAllViewContinuationTypeIds(doc):
    '''
    Gets all view continuation type ids available in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of view continuation type ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    syms = GetAllReferenceViewElementsByCategory(doc)
    for sym in syms:
        simTypeIds = sym.GetValidTypes()
        for simType in simTypeIds:
            if (simType not in ids):
                ids.append (simType)
    return ids

def GetUsedViewContinuationTypeIds(doc):
    '''returns all view continuation types available in the model'''
    ids = []
    syms = GetAllReferenceViewElementsByCategory(doc)
    for sym in syms:
        if (sym.GetTypeId() not in ids):
                ids.append (sym.GetTypeId())
    return ids

def GetAllViewReferenceSymbolIds(doc):
    '''
    Gets the ids of all view reference family symbols(types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of view reference family symbols(types) ids.
    :rtype:  list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    multiCatFilter = rdb.ElementMulticategoryFilter(VIEW_REF_CATEGORY_FILTER)
    collector = rdb.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# ---------------------- view refs and continuation symbols -----------------------

def GetSymbolIdsFromTypeIds(doc, viewRefTypesIds):
    '''
    'Gets the ids of all view family symbols(types) from given view ref types or continuation types the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewRefTypesIds: list of ids representing view reference types or continuation types
    :type viewRefTypesIds: list Autodesk.Revit.DB.ElementId

    :return: List of ids of all view family symbols(types).
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for vrtId in viewRefTypesIds:
        el = doc.GetElement(vrtId)
        for pDef in VIEW_TAG_SYMBOL_PARAMETER_DEF:
            pValue = rParaGet.get_built_in_parameter_value(el, pDef)
            if (pValue != None and pValue not in ids):
                ids.append(pValue)
    return ids

def GetUsedViewReferenceAndContinuationMarkerSymbolIds(doc):
    '''
    Get the ids of all view reference symbols(types) and view continuations symbols (types) used by 
    view reference types and view continuation types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: List of ids of all view family symbols(types).
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    viewContTypes = GetAllViewContinuationTypeIds(doc)
    viewRefTypes = GetAllViewReferenceTypeIdData(doc)
    # get ids of symbols used in view ref types
    idsCont = GetSymbolIdsFromTypeIds(doc, viewContTypes)
    idsViewRefs = []
    for key,value in viewRefTypes.items():
        idsViewRefs = idsViewRefs + GetSymbolIdsFromTypeIds(doc, viewRefTypes[key])
    # build unique dictionary
    for idC in idsCont:
        ids.append(idC)
    for idV in idsViewRefs:
        if(idV not in ids):
            ids.append(idV)
    return ids

def GetNestedFamilyMarkerNames(doc, usedIds):
    '''
    Gets nested family names from provided symbols.

    - Retrieves a families from the symbols provided. 
    - Opens the family document and extracts the names off all nested families within.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param usedIds: List of symbol ids.
    :type usedIds: list of Autodesk.Revit.DB.ElementId

    :return: List of all unique nested family names.
    :rtype: list str
    '''

    names = []
    for usedSymbolId in usedIds:
        if(usedSymbolId != rdb.ElementId.InvalidElementId):
            # get the family
            elSymbol = doc.GetElement(usedSymbolId)
            fam = elSymbol.Family
            # open family
            try:
                famDoc = doc.EditFamily(fam)
                nestedFamCol = rFamU.GetAllLoadableFamilies(famDoc)
                for nFam in nestedFamCol:
                    if(nFam.Name not in names and nFam.Name != ''):
                        names.append(nFam.Name)        
                famDoc.Close(False)
            except Exception as e:
                print (e)
    #print (names)
    return names

def IsNestedFamilySymbol(doc, id, nestedFamilyNames):
    '''
    Returns true if symbol belongs to family in list past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id: The element id of a symbol.
    :type id: Autodesk.Revit.DB.ElementId
    :param nestedFamilyNames: list of family names know to be nested families.
    :type nestedFamilyNames: list str
    
    :return: True if family name derived from symbol is in list past in, otherwise False.
    :rtype: bool
    '''

    flag = False
    famSymbol = doc.GetElement(id)
    fam = famSymbol.Family
    if(fam.Name in nestedFamilyNames):
        flag = True
    return flag

def GetUnusedViewRefAndContinuationMarkerSymbolIds(doc):
    '''
    Gets the ids of all view reference symbols(types) and view continuation symbols (types) not used in the model.

    Not used: These symbols are not used in any view reference types, or nested in any symbols used in view reference types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # compare used vs available in view ref types
    # whatever is marked as unused: check for any instances in the model...placed on legends!
    availableIds = GetAllViewReferenceSymbolIds(doc) # check: does this really return all continuation marker types??
    usedIds = GetUsedViewReferenceAndContinuationMarkerSymbolIds(doc)
    # elevation marker families might use nested families...check!
    nestedFamilyNames = GetNestedFamilyMarkerNames(doc, usedIds)
    checkIds = []
    for aId in availableIds:
        if (aId not in usedIds):
            checkIds.append(aId)
    # check for any instances
    for id in checkIds:
        instances = rFamU.GetFamilyInstancesBySymbolTypeId(doc, id).ToList()
        if(len(instances) == 0):
            if(IsNestedFamilySymbol(doc, id, nestedFamilyNames) == False):
                ids.append(id)
    return ids

# ---------------------- purge unused view ref types and symbols -----------------------

def GetUnusedViewReferenceTypeIdsForPurge(doc):
    '''
    Gets all unused view references type ids in model for purge.

    This method can be used to safely delete all unused view reference types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    allAvailableTypeIds = GetAllViewReferenceTypeIdData(doc)
    allUsedTypeIds = GetUsedViewReferenceTypeIdData(doc)
    for key,value in allAvailableTypeIds.items():
        if(allUsedTypeIds.has_key(key)):
            for availableTypeId in allAvailableTypeIds[key]:
                if(availableTypeId not in allUsedTypeIds[key]):
                    ids.append(availableTypeId)
        else:
            # add all types under this key to be purge list...might need to check whether I need to leave one behind...
            if(len(allAvailableTypeIds[key])>0):
                ids = ids + allAvailableTypeIds[key]
    return ids

# ---------------------- purge unused view continuation types-----------------------

def GetUnusedContinuationMarkerTypeIdsForPurge(doc):
    '''
    Gets all unused view continuation type ids in model for purge.

    This method can be used to safely delete all unused view continuation marker types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    allAvailableTypeIds = GetAllViewContinuationTypeIds(doc)
    allUsedTypeIds = GetUsedViewContinuationTypeIds(doc)
    for aId in allAvailableTypeIds:
        if( aId not in allUsedTypeIds):
            ids.append(aId)
    return ids

# ---------------------- purge unused view ref symbol and continuation symbols -----------------------

def GetUnusedViewRefAndContinuationMarkerFamiliesForPurge(doc):
    '''
    Gets the ids of all view reference symbols(types) ids and or family ids not used in the model for purging.

    This method can be used to safely delete all unused view reference and continuation marker family symbols\
        or families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    return rFamU.GetUnusedInPlaceIdsForPurge(doc, GetUnusedViewRefAndContinuationMarkerSymbolIds)
