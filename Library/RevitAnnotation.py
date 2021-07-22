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

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_DIMENSIONS_HEADER = ['HOSTFILE','ID', 'NAME']
REPORT_TEXT_HEADER = ['HOSTFILE','ID', 'NAME']

# --------------------------------------------- utility functions ------------------

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
