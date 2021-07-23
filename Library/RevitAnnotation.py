#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

# import common library modules
import RevitCommonAPI as com
import Result as res
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_DIMENSIONS_HEADER = ['HOSTFILE','ID', 'NAME']
REPORT_TEXT_HEADER = ['HOSTFILE','ID', 'NAME']

# --------------------------------------------- dimensions  ------------------

# doc: current model document
def GetDimTypes(doc):
    """returns all dimension types in a model"""
    return FilteredElementCollector(doc).OfClass(DimensionType)

# doc   current model document
def GetUsedDimTypeIdsInTheModel(doc):
    """returns all dimension type Ids in the model"""
    dimTypeIdsUsed = []
    col = GetAllDimensionElements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

# doc   current model document
def GetAllDimensionElements(doc):
    """returns all dimension elements in the model"""
    return FilteredElementCollector(doc).OfClass(Dimension)

# doc   current model document
def GetAllMultiRefAnnotationTypes(doc):
    """returns all multireference annotation types in the model"""
    return FilteredElementCollector(doc).OfClass(MultiReferenceAnnotationType)

# doc   current model document
def GetAllMultiRefAnnotationElements(doc):
    """returns all multireference annotation elements in the model"""
    return FilteredElementCollector(doc).OfClass(MultiReferenceAnnotation)

# doc   current model document
def GetUsedMultiRefDimTypeIdsInTheModel(doc):
    """returns all ids of multireference types used by elements in the model"""
    dimTypeIdsUsed = []
    col = GetAllMultiRefAnnotationElements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

# doc   current model document
def GetAllSimilarMultiReferenceAnnoTypes(doc):
    """returns all multireference annotation types from similar types in the model"""
    multiReferenceAnnoTypes = com.GetSimilarTypeFamiliesByType(doc, GetAllMultiRefAnnotationTypes)
    return multiReferenceAnnoTypes 

# doc   current model document
# multiReferenceAnnoTypes   :list in format [[multireftype, [element ids of similar multi ref types, ...]]]
def GetUsedDimstylesFromMultiRef(doc, multiReferenceAnnoTypes):
    """returns all dimension styles used in multi ref annotation"""
    dimTypeIdsUsed = []
    for mType in multiReferenceAnnoTypes:
        for t in mType[1]:
            multiRefType = doc.GetElement(t)
            if (multiRefType.DimensionStyleId not in dimTypeIdsUsed):
                dimTypeIdsUsed.append(multiRefType.DimensionStyleId)
    return dimTypeIdsUsed

# doc   current model document
def GetAllUnusedMultiRefDimTypeIdsInModel(doc):
    """returns IDs of unused multiref dimension types in the model"""
    return com.GetUnusedTypeIdsInModel(doc, GetAllMultiRefAnnotationTypes, GetUsedMultiRefDimTypeIdsInTheModel)

# doc   current model document
def GetAllUnusedDimTypeIdsInModel(doc):
    """returns ID of unused dim types in the model"""
    # get unused dimension type ids
    filteredUnusedDimTypeIds = com.GetUnusedTypeIdsInModel(doc, GetDimTypes, GetUsedDimTypeIdsInTheModel)
    # get all multiref dimension types in model
    multiReferenceAnnoTypes = GetAllSimilarMultiReferenceAnnoTypes(doc)
    # get all dim styles used in multirefs
    usedDimStylesInMultiRefs = GetUsedDimstylesFromMultiRef(doc, multiReferenceAnnoTypes)
    # cross reference filtered list vs multi ref list and only keep items which are just in the filtered list
    unusedDimTypeIds = []
    for f in filteredUnusedDimTypeIds:
        if(f not in usedDimStylesInMultiRefs):
            unusedDimTypeIds.append(f)
    return unusedDimTypeIds

# --------------------------------------------- Text  ------------------

# doc   current model document
def GetAllTextTypes(doc):
    """returns all text types in the model"""
    return FilteredElementCollector(doc).OfClass(TextElementType)

# doc   current model document
def GetAllTextAnnotationElements(doc):
    """returns all text annotation elements in the model"""
    return FilteredElementCollector(doc).OfClass(TextElement)

# doc   current model document
def GetUsedTextTypeIdsInTheModel(doc):
    """returns all ids of text types used by elements in the model, includes types used in schedules (appearance)!"""
    textTypeIdsUsed = []
    col = GetAllTextAnnotationElements(doc)
    for t in col:
        if(t.GetTypeId() not in textTypeIdsUsed):
            textTypeIdsUsed.append(t.GetTypeId())
    # get all schedules and check their appearance text proprties!
    col = FilteredElementCollector(doc).OfClass(ViewSchedule)
    for c in col:
        if(c.BodyTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.BodyTextTypeId)
        if(c.HeaderTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.HeaderTextTypeId)
        if(c.TitleTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.TitleTextTypeId)
    return textTypeIdsUsed

# doc   current model document
def GetAllUnusedTextTypeIdsInModel(doc):
    """returns ID of unused text types in the model"""
    filteredUnusedTextTypeIds = com.GetUnusedTypeIdsInModel(doc, GetAllTextTypes, GetUsedTextTypeIdsInTheModel)
    return filteredUnusedTextTypeIds

# --------------------------------------------- Arrow heads  ------------------

# list of built in parameters attached to dimensions containing arrow head ids
ARROWHEAD_PARAS_DIM = [
    BuiltInParameter.DIM_STYLE_CENTERLINE_TICK_MARK,
    BuiltInParameter.DIM_STYLE_INTERIOR_TICK_MARK,
    BuiltInParameter.DIM_STYLE_LEADER_TICK_MARK,
    BuiltInParameter.DIM_LEADER_ARROWHEAD,
    BuiltInParameter.WITNS_LINE_TICK_MARK
]

""" list of built in parameters attached to 
      - text 
      - independent tags 
      - Annotation symbols
    containing arrow head ids
"""
ARROWHEAD_PARAS_TEXT = [
    BuiltInParameter.LEADER_ARROWHEAD
]

# list of built in parameters attached to spot dims containing arrow head ids
ARROWHEAD_PARAS_SPOT_DIMS = [
    BuiltInParameter.SPOT_ELEV_LEADER_ARROWHEAD
]

# list of built in parameters attached to stair path types containing arrow head ids
ARROWHEAD_PARAS_STAIRS_PATH = [
    BuiltInParameter.ARROWHEAD_TYPE
]


# doc: current model
def GetArrowHeadIdsFromType(doc, typeGetter, parameterList):
    """returns all arrow head ids used in dim types in a model"""
    usedIds = []
    types = typeGetter(doc)
    for t in types:
        paras = t.GetOrderedParameters()
        for p in paras:
            for pInt in parameterList:
                if (p.Definition.BuiltInParameter == pInt):
                    id = com.getParameterValue(p)
                    if(id not in usedIds and id != ElementId.	InvalidElementId):
                        usedIds.append(id)
                    break
    return usedIds

#--------------------------------------

# doc: current model
def GetDimTypeArrowHeadIds(doc):
    """returns all arrow head ids used in dim types in a model"""
    usedIds = GetArrowHeadIdsFromType(doc, GetDimTypes, ARROWHEAD_PARAS_DIM)
    return usedIds
                        
#--------------------------------------

def GetTextTypeArrowHeadIds(doc):
    """returns all arrow head ids used in text types in a model"""
    usedIds = GetArrowHeadIdsFromType(doc, GetAllTextTypes, ARROWHEAD_PARAS_TEXT)
    return usedIds

#--------------------------------------

# doc   current model document
def GetAllIndependentTags(doc):
    """returns all text types in the model"""
    return FilteredElementCollector(doc).OfClass(IndependentTag)

def GetIndependentTagTypeArrowHeadIds(doc):
    """returns all arrow head ids used in independent tag types in a model"""
    usedIds = []
    tags = GetAllIndependentTags(doc)
    for t in tags:
        tTypeId = t.GetTypeId()
        tTypeElement = doc.GetElement(tTypeId)
        paras = tTypeElement.GetOrderedParameters()
        for p in paras:
            if (p.Definition.BuiltInParameter == BuiltInParameter.LEADER_ARROWHEAD):
                id = com.getParameterValue(p)
                if(id not in usedIds and id != ElementId.	InvalidElementId):
                    usedIds.append(id)
                break
    return usedIds

# -----------------------------------------------

# doc   current model document
def GetAllSpotDimTypes(doc):
    """returns all spot Dim types in the model"""
    return FilteredElementCollector(doc).OfClass(SpotDimensionType)

def GetSpotTypeArrowHeadIds(doc):
    """returns all arrow head ids used in text types in a model"""
    usedIds = GetArrowHeadIdsFromType(doc, GetAllSpotDimTypes, ARROWHEAD_PARAS_SPOT_DIMS)
    return usedIds

# ----------------------------------------------

# doc   current model document
def GetAllAnnoSymbolTypes(doc):
    """returns all annotation symbol types, area tag types, room tag types in the model"""
    types = []
    col = FilteredElementCollector(doc).OfClass(FamilySymbol)
    for c in col:
        if (c.GetType() == AnnotationSymbolType or c.GetType == AreaTagType or c.GetType() == Architecture.RoomTagType):
            types.append(c)
    return types

def GetAnnoSymbolArrowHeadIds(doc):
    """returns all arrow head ids used in text types in a model"""
    usedIds = GetArrowHeadIdsFromType(doc, GetAllAnnoSymbolTypes, ARROWHEAD_PARAS_TEXT)
    return usedIds

# ----------------------------------------------

# doc   current model document
def GetAllStairPathTypes(doc):
    """returns all stairs path types in the model"""
    return FilteredElementCollector(doc).OfClass(StairsPathType)
        
def GetStairsPathArrowHeadIds(doc):
    """returns all arrow head ids used in stairs path types in a model"""
    usedIds = GetArrowHeadIdsFromType(doc, GetAllStairPathTypes, ARROWHEAD_PARAS_STAIRS_PATH)
    return usedIds

# ----------------------------------------------

# doc   current model document
def GetAllUsedArrowHeadTypeIdsInModel(doc):
    """returns all used arrow types in the model considering dimension, text, 
    independent tags, spot dims, annotation symbols (incl room and area tags), stairs path"""
    usedIds = []
    usedIds = usedIds + GetDimTypeArrowHeadIds(doc)
    usedIds = usedIds +  GetTextTypeArrowHeadIds(doc)
    usedIds = usedIds + GetIndependentTagTypeArrowHeadIds(doc)
    usedIds = usedIds + GetSpotTypeArrowHeadIds(doc)
    usedIds = usedIds + GetAnnoSymbolArrowHeadIds(doc)
    usedIds = usedIds + GetStairsPathArrowHeadIds(doc)
    filteredIds = []
    for u in usedIds:
        if (u not in filteredIds):
            filteredIds.append(u)
    return filteredIds

# doc   current model document
def GetArrowTypesInModel(doc):
    """returns all arrow types in the model"""
    types = []
    similarTypes = []
    col = FilteredElementCollector(doc).OfClass(ElementType)
    for c in col:
        if (c.FamilyName == 'Arrowhead'):
            similarTypes = c.GetSimilarTypes()
            # filter out any types not in similar list...not sure what these are...
            if(c.Id in similarTypes):
                types.append(c)
    return types

# doc   current model document
def GetArrowTypesIdsInModel(doc):
    """returns all arrow type ids in the model"""
    types = []
    similarTypes = []
    col = FilteredElementCollector(doc).OfClass(ElementType)
    for c in col:
        if (c.FamilyName == 'Arrowhead'):
            similarTypes = c.GetSimilarTypes()
            # filter out any types not in similar list...not sure what these are...
            if(c.Id in similarTypes):
                types.append(c.Id)
    return types

# doc   current model document
def GetAllUnusedArrowTypeIdsInModel(doc):
    """returns all unused arrow type ids in the model"""
    unusedIds = []
    usedIds = GetAllUsedArrowHeadTypeIdsInModel(doc)
    availableIds = GetArrowTypesIdsInModel(doc)
    for aId in availableIds:
        if(aId not in usedIds):
            unusedIds.append(aId)
    return unusedIds 