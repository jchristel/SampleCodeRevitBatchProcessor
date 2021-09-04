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


import RevitCommonAPI as com
import RevitFamilyUtils as rFamU
import RevitViews as rView

# import Autodesk
from Autodesk.Revit.DB import *

# ------------------------ deprecated -----------------------
# the following element collectors dont seem to return any types ...

# doc:   current model document
def Deprecated_GetAllCallOutTypesByCategory(doc):
    """ this will return an EMPTY filtered element collector of all call out types in the model in Revit 2019"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Callouts).WhereElementIsElementType()
    return collector

# doc:   current model document
def Deprecated_GetAllReferenceViewTypesByCategory(doc):
    """this will return an EMPTY filtered element collector of all reference view types in the model in Revit 2019"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ReferenceViewer).WhereElementIsElementType()
    return collector
 
# doc:   current model document
def Deprecated_GetAllCallOutTypeIdsByCategory(doc):
    """ this will return an EMPTY filtered element collector of all call out type ids in the model"""
    collector = Deprecated_GetAllCallOutTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# doc:   current model document
def Deprecated_GetAllReferenceViewTypeIdsByCategory(doc):
    """ this will return an EMPTY filtered element collector of all reference view types in the model"""
    collector = Deprecated_GetAllReferenceViewTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# ---------------------- utility -----------------------

# doc:   current model document
def GetAllCallOutHeadsByCategory(doc):
    """ this will return a filtered element collector of all callOut Head symbol (types) in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CalloutHeads).WhereElementIsElementType()
    return collector

# doc:   current model document
def GetAllElevationHeadsByCategory(doc):
    """ this will return a filtered element collector of all elevation symbols (types) in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ElevationMarks).WhereElementIsElementType()
    return collector

# doc:   current model document
def GetAllSectionHeadsByCategory(doc):
    """ this will return a filtered element collector of all section symbols (types) in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_SectionHeads).WhereElementIsElementType()
    return collector

# doc:   current model document
def GetAllViewContinuationMarkersByCategory(doc):
    """ this will return a filtered element collector of all view contiunation symbols (types) in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ReferenceViewerSymbol)
    return collector

# doc:   current model document
def GetAllReferenceViewElementsByCategory(doc):
    """this will return an filtered element collector of all reference elements in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ReferenceViewer)
    return collector

# contains the builtin parameter definitions for Call out type ids, section type ids, elevation type ids
VIEW_REFERENCE_PARAMETER_DEF_NAMES = [
    BuiltInParameter.ELEVATN_TAG,
    BuiltInParameter.CALLOUT_TAG,
    BuiltInParameter.SECTION_TAG
]

# contains the builtin parameter definitions for Callout symbol tag ids, section symbol tag ids, elevation symbol tag ids
VIEW_TAG_SYMBOL_PARAMETER_DEF = [
    BuiltInParameter.CALLOUT_ATTR_HEAD_TAG,
    BuiltInParameter.ELEV_SYMBOL_ID,
    BuiltInParameter.SECTION_ATTR_HEAD_TAG,
    BuiltInParameter.SECTION_ATTR_TAIL_TAG,
    BuiltInParameter.REFERENCE_VIEWER_ATTR_TAG
]

# category filter for all view ref categories
VIEWREF_CATEGORYFILTER = List[BuiltInCategory] ([
        BuiltInCategory.OST_CalloutHeads,
        BuiltInCategory.OST_ElevationMarks,
        BuiltInCategory.OST_SectionHeads,
        BuiltInCategory.OST_ReferenceViewerSymbol
    ])

def GetReferenceTypeIdsFromViewType(viewType):
    """returns all reference type ids used in view type"""
    dic = {}
    paras = viewType.GetOrderedParameters()
    for p in paras:
        if(p.Definition.BuiltInParameter in VIEW_REFERENCE_PARAMETER_DEF_NAMES):
            pvalue = com.getParameterValue(p)
            # there should only ever be one value per key!
            if(dic.has_key(p.Definition.BuiltInParameter)):
                dic[p.Definition.BuiltInParameter].append(pvalue)
            else:
                dic[p.Definition.BuiltInParameter] = [pvalue]
    return dic

# doc:   current model document
def GetUsedViewReferenceTypeIdData(doc):
    """returns all view references types in use in the model in a dictionary
    key is the reference tag type: callout, section or elevation
    values are the type ids in use"""
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

# doc:   current model document
def GetAllViewReferenceTypeIdData(doc):
    """returns all view references types available in the model in a dictionary
    key is the reference type: callout, section or elevation
    values are the symbol ids"""
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

# doc:   current model document
def GetAllViewContinuationTypeIds(doc):
    """returns all view continuation types available in the model"""
    ids = []
    syms = GetAllReferenceViewElementsByCategory(doc)
    for sym in syms:
        simTypeIds = sym.GetValidTypes()
        for simType in simTypeIds:
            if (simType not in ids):
                ids.append (simType)
    return ids

# doc:   current model document
def GetUsedViewContinuationTypeIds(doc):
    """returns all view continuation types available in the model"""
    ids = []
    syms = GetAllReferenceViewElementsByCategory(doc)
    for sym in syms:
        if (sym.GetTypeId() not in ids):
                ids.append (sym.GetTypeId())
    return ids

# doc:   current model document
def GetUnusedContinuationMarkerTypeIdsForPurge(doc):
    """returns all unused view continuation type ids in model for purge"""
    ids = []
    allAvailableTypeIds = GetAllViewContinuationTypeIds(doc)
    allUsedTypeIds = GetUsedViewContinuationTypeIds(doc)
    for aId in allAvailableTypeIds:
        if( aId not in allUsedTypeIds):
            ids.append(aId)
    return ids

# doc:   current model document
def GetUnusedViewReferenceTypeIdsForPurge(doc):
    """returns all unused view references type ids in model for purge"""
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

# doc:   current model document
def GetAllViewReferenceSymbolIds(doc):
    """returns the ids of all view reference symbols(types) in the model"""
    ids = []
    multiCatFilter = ElementMulticategoryFilter(VIEWREF_CATEGORYFILTER)
    collector = FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# doc:   current model document
# viewRefTypesIds   list of view reference types
def GetSymbolIdsFromTypeIds(doc, viewRefTypesIds):
    """returns the ids of all view symbols(types) from given view ref types the model"""
    ids = []
    for vrtId in viewRefTypesIds:
        el = doc.GetElement(vrtId)
        paras = el.GetOrderedParameters()
        for p in paras:
            if (p.Definition.BuiltInParameter in VIEW_TAG_SYMBOL_PARAMETER_DEF):
                pvalue = com.getParameterValue(p)
                if(pvalue not in ids):
                    ids.append(pvalue)
    return ids

# doc:   current model document
def GetUsedViewReferenceSymbolIds(doc):
    """returns the ids of all view reference symbols(types) used by view reference types in the model"""
    ids = []
    viewContTypes = GetAllViewContinuationTypeIds(doc)
    viewReftypes = GetAllViewReferenceTypeIdData(doc)
    # get ids of symbols used in view ref types
    idsCont = GetSymbolIdsFromTypeIds(doc, viewContTypes)
    idsViewRefs = []
    for key,value in viewReftypes.items():
        idsViewRefs = idsViewRefs + GetSymbolIdsFromTypeIds(doc, viewReftypes[key])
    # build unique dictionary
    for idC in idsCont:
        ids.append(idC)
    for idV in idsViewRefs:
        if(idV not in ids):
            ids.append(idV)
    return ids

# doc:      current model document
# typeId:   symbol type id
def GetFamilyInstancesBySymbolTypeId(doc, typeId):
    """returns all instances of a given family symbol"""
    pvpSymbol = ParameterValueProvider(ElementId( BuiltInParameter.SYMBOL_ID_PARAM ) )
    equals = FilterNumericEquals()
    idFilter = FilterElementIdRule( pvpSymbol, equals, typeId)
    efilter =  ElementParameterFilter( idFilter )
    collector = FilteredElementCollector(doc).WherePasses( efilter )
    return collector


# doc:   current model document
def GetUnusedViewRefSymbolIds(doc):
    """returns the ids of all view reference symbols(types) not used in the model"""
    ids = []
    # compare used vs available in view ref types
    # whatever is marked as unused: check for any instances in the model...placed on legends!
    availableIds = GetAllViewReferenceSymbolIds(doc)
    usedIds = GetUsedViewReferenceSymbolIds(doc)
    checkIds = []
    for aId in availableIds:
        if (aId not in usedIds):
            checkIds.append(aId)
    # check for any instances
    for id in checkIds:
        instances = rFamU.GetFamilyInstancesBySymbolTypeId(doc, id).ToList()
        if(len(instances) == 0):
            ids.append(id)
    return ids

# doc:   current model document
def GetUnusedViewRefFamiliesForPurge(doc):
    """returns the ids of all view reference symbols(types) ids and or family ids not used in the model for purging"""
    return rFamU.GetUnusedInPlaceIdsForPurge(doc, GetUnusedViewRefSymbolIds)