'''
This module contains a number of functions around Revit annotation objects. 
'''
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
import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

import Autodesk.Revit.DB.Architecture as rdba

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
#: header used in dimensions reports
REPORT_DIMENSIONS_HEADER = ['HOSTFILE','ID', 'NAME']
#: header used in text reports
REPORT_TEXT_HEADER = ['HOSTFILE','ID', 'NAME']

# --------------------------------------------- dimensions  ------------------

def GetDimTypes(doc):
    '''
    Gets all dimension types in a model

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector of Dimension Types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of DimensionType
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.DimensionType)

def GetDimTypeIds(doc):
    '''
    Gets all dimension type ids in a model

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing Dimension Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.DimensionType)
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetUsedDimTypeIdsInTheModel(doc):
    '''
    Gets all used dimension type Ids in the model.
    
    Used: at least one instance using this type is placed in the model.

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing Dimension Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    dimTypeIdsUsed = []
    col = GetAllDimensionElements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

def GetAllDimensionElements(doc):
    '''
    Gets all dimension elements placed in the model.

    :param doc: _description_
    :type doc: _type_
    
    :return: A filtered element collector of Dimensions
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of Dimension
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.Dimension)

def GetAllMultiRefAnnotationTypes(doc):
    '''
    Gets all multireference annotation types in the model.

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector of MultiReferenceAnnotationType
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of MultiReferenceAnnotationType
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotationType)

def GetAllMultiRefAnnotationTypeIds(doc):
    '''
    Gets all multireference annotation type ids in the model.

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing Multireference Annotation Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotationType)
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetAllMultiRefAnnotationElements(doc):
    '''
    Gets all multireference annotation elements in the model.

    :param doc: _description_
    :type doc: _type_
    
    :return: A filtered element collector of MultiReferenceAnnotation
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of MultiReferenceAnnotation
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotation)

def GetUsedMultiRefDimTypeIdsInTheModel(doc):
    '''
    Gets all ids of multireference types used by elements in the model.

    Used: at least one instance using this type is placed in the model.

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing Multireference Annotation Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    dimTypeIdsUsed = []
    col = GetAllMultiRefAnnotationElements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

def GetAllSimilarMultiReferenceAnnoTypes(doc):
    '''
    Gets all multireference annotation types using get similar types in the model.

    :param doc: _description_
    :type doc: _type_

    :return: list in format [[multireftype, [element ids of similar multi ref types, ...]]]
    :rtype: List [[Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    '''

    multiReferenceAnnoTypes = com.GetSimilarTypeFamiliesByType(doc, GetAllMultiRefAnnotationTypes)
    return multiReferenceAnnoTypes 

def GetUsedDimstylesFromMultiRef(doc, multiReferenceAnnoTypes):
    '''
    Gets all dimension styles used in multi ref annotation types.

    :param doc: _description_
    :type doc: _type_
    :param multiReferenceAnnoTypes: list in format [[multireftype, [element ids of similar multi ref types, ...]]]
    :type multiReferenceAnnoTypes: List [[Autodesk.Revit.DB.ElementType, [Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]]
    
    :return: List of element ids representing dimension style
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    dimTypeIdsUsed = []
    for mType in multiReferenceAnnoTypes:
        for t in mType[1]:
            multiRefType = doc.GetElement(t)
            if (multiRefType.DimensionStyleId not in dimTypeIdsUsed):
                dimTypeIdsUsed.append(multiRefType.DimensionStyleId)
    return dimTypeIdsUsed

def GetAllUnusedMultiRefDimTypeIdsInModel(doc):
    '''
    Gets IDs of all unused multiref dimension types in the model.

    :param doc: _description_
    :type doc: _type_
    :return: List of element ids representing multi ref dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return com.GetUnusedTypeIdsInModel(doc, GetAllMultiRefAnnotationTypes, GetUsedMultiRefDimTypeIdsInTheModel)

def GetAllUnusedDimTypeIdsInModel(doc):
    '''
    Gets ID of all unused dim types in the model.

    Includes checking multi ref dims for used dim types.

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

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

def GetAllTextTypes(doc):
    '''
    Gets all text types in the model

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector of text element types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of text element types
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.TextElementType)

def GetAllTextTypeIds(doc):
    '''
    Gets all text type ids in the model.

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.TextElementType)
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetAllTextAnnotationElements(doc):
    '''
    Gets all text annotation elements in the model.

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector of text elements
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of text elements
    '''
    return rdb.FilteredElementCollector(doc).OfClass(rdb.TextElement)

def GetUsedTextTypeIdsInTheModel(doc):
    '''
    Gets all ids of text types used by elements in the model, includes types used in schedules (appearance)!
    
    Used: at least one instance of this type is placed in the model.
    
    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing used text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    textTypeIdsUsed = []
    col = GetAllTextAnnotationElements(doc)
    for t in col:
        if(t.GetTypeId() not in textTypeIdsUsed):
            textTypeIdsUsed.append(t.GetTypeId())
    # get all schedules and check their appearance text proprties!
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSchedule)
    for c in col:
        if(c.BodyTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.BodyTextTypeId)
        if(c.HeaderTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.HeaderTextTypeId)
        if(c.TitleTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.TitleTextTypeId)
    return textTypeIdsUsed

def GetAllUnusedTextTypeIdsInModel(doc):
    '''
    Gets ID of all unused text types in the model.
    
    Unused: Not one instance of this type is placed in the model.
    
    :param doc: _description_
    :type doc: _type_
    :return: List of element ids representing unused text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''
    filteredUnusedTextTypeIds = com.GetUnusedTypeIdsInModel(doc, GetAllTextTypes, GetUsedTextTypeIdsInTheModel)
    return filteredUnusedTextTypeIds

# --------------------------------------------- Arrow heads  ------------------

#: list of built in parameters attached to dimensions containing arrow head ids
ARROWHEAD_PARAS_DIM = [
    rdb.BuiltInParameter.DIM_STYLE_CENTERLINE_TICK_MARK,
    rdb.BuiltInParameter.DIM_STYLE_INTERIOR_TICK_MARK,
    rdb.BuiltInParameter.DIM_STYLE_LEADER_TICK_MARK,
    rdb.BuiltInParameter.DIM_LEADER_ARROWHEAD,
    rdb.BuiltInParameter.WITNS_LINE_TICK_MARK
]

 
#:  list of built in parameters attached to
#:
#:    - text 
#:    - independent tags 
#:    - Annotation symbols
#:
#: containing arrow head ids

#: paramter containing the arrowhead id in text types
ARROWHEAD_PARAS_TEXT = [
    rdb.BuiltInParameter.LEADER_ARROWHEAD
]

#: list of built in parameters attached to spot dims containing arrow head ids
#: and symbols used
ARROWHEAD_PARAS_SPOT_DIMS = [
    rdb.BuiltInParameter.SPOT_ELEV_LEADER_ARROWHEAD,
    rdb.BuiltInParameter.SPOT_ELEV_SYMBOL
]

#: list of built in parameters attached to stair path types containing arrow head ids
ARROWHEAD_PARAS_STAIRS_PATH = [
    rdb.BuiltInParameter.ARROWHEAD_TYPE
]


# doc: current model
def GetArrowHeadIdsFromType(doc, typeGetter, parameterList):
    '''
    returns all arrow head ids used in dim types in a model
    '''
    usedIds = []
    types = typeGetter(doc)
    for t in types:
        for pInt in parameterList:
            id = com.GetBuiltInParameterValue(t, pInt)
            if(id not in usedIds and id != rdb.ElementId.InvalidElementId and id != None):
                usedIds.append(id)
            break
    return usedIds

#--------------------------------------

# doc: current model
def GetDimTypeArrowHeadIds(doc):
    '''
    returns all arrow head ids used in dim types in a model
    '''
    usedIds = GetArrowHeadIdsFromType(doc, GetDimTypes, ARROWHEAD_PARAS_DIM)
    return usedIds
                        
#--------------------------------------

def GetTextTypeArrowHeadIds(doc):
    '''
    returns all arrow head ids used in text types in a model
    '''
    usedIds = GetArrowHeadIdsFromType(doc, GetAllTextTypes, ARROWHEAD_PARAS_TEXT)
    return usedIds

#--------------------------------------

# doc   current model document
def GetAllIndependentTags(doc):
    '''
    returns all text types in the model
    '''
    return rdb.FilteredElementCollector(doc).OfClass(rdb.IndependentTag)

def GetIndependentTagTypeArrowHeadIds(doc):
    '''
    returns all arrow head ids used in independent tag types in a model
    '''
    usedIds = []
    tags = GetAllIndependentTags(doc)
    for t in tags:
        tTypeId = t.GetTypeId()
        tTypeElement = doc.GetElement(tTypeId)
        id = com.GetBuiltInParameterValue(tTypeElement, rdb.BuiltInParameter.LEADER_ARROWHEAD)
        if(id not in usedIds and id != rdb.ElementId.InvalidElementId and id != None):
            usedIds.append(id)
    return usedIds

# -----------------------------------------------

# doc   current model document
def GetAllSpotDimTypes(doc):
    '''
    returns all spot Dim types in the model
    '''
    return rdb.FilteredElementCollector(doc).OfClass(rdb.SpotDimensionType)

def GetSpotTypeArrowHeadIds(doc):
    '''
    returns all arrow head ids used in text types in a model
    '''
    usedIds = GetArrowHeadIdsFromType(doc, GetAllSpotDimTypes, ARROWHEAD_PARAS_SPOT_DIMS)
    return usedIds

# ----------------------------------------------

# doc   current model document
def GetAllAnnoSymbolTypes(doc):
    '''
    returns all annotation symbol types, area tag types, room tag types in the model
    '''
    types = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol)
    for c in col:
        if (c.GetType() == rdb.AnnotationSymbolType or c.GetType == rdb.AreaTagType or c.GetType() == rdba.RoomTagType):
            types.append(c)
    return types

def GetAnnoSymbolArrowHeadIds(doc):
    '''
    returns all arrow head ids used in text types in a model
    '''
    usedIds = GetArrowHeadIdsFromType(doc, GetAllAnnoSymbolTypes, ARROWHEAD_PARAS_TEXT)
    return usedIds

# ----------------------------------------------

# doc   current model document
def GetAllStairPathTypes(doc):
    '''
    returns all stairs path types in the model
    '''
    return rdb.FilteredElementCollector(doc).OfClass(rdba.StairsPathType)
        
def GetStairsPathArrowHeadIds(doc):
    '''
    returns all arrow head ids used in stairs path types in a model
    '''
    usedIds = GetArrowHeadIdsFromType(doc, GetAllStairPathTypes, ARROWHEAD_PARAS_STAIRS_PATH)
    return usedIds

# ----------------------------------------------

# doc   current model document
def GetAllUsedArrowHeadTypeIdsInModel(doc):
    '''
    returns all used arrow types in the model considering dimension, text, 
    independent tags, spot dims, annotation symbols (incl room and area tags), stairs path
    '''
    usedIds = []
    usedIds = usedIds + GetDimTypeArrowHeadIds(doc)
    usedIds = usedIds + GetTextTypeArrowHeadIds(doc)
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
    '''
    returns all arrow types in the model
    '''
    types = []
    similarTypes = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ElementType)
    for c in col:
        if (c.FamilyName == 'Arrowhead'):
            similarTypes = c.GetSimilarTypes()
            # filter out any types not in similar list...not sure what these are...
            if(c.Id in similarTypes):
                types.append(c)
    return types

# doc   current model document
def GetArrowTypesIdsInModel(doc):
    '''
    returns all arrow type ids in the model
    '''
    arrowTypes = GetArrowTypesInModel(doc)
    ids = []
    for at in arrowTypes:
            if(at.Id not in ids):
                ids.append(at.Id)
    return ids

# doc   current model document
def GetAllUnusedArrowTypeIdsInModel(doc):
    '''
    returns all unused arrow type ids in the model
    '''
    unusedIds = []
    usedIds = GetAllUsedArrowHeadTypeIdsInModel(doc)
    availableIds = GetArrowTypesIdsInModel(doc)
    for aId in availableIds:
        if(aId not in usedIds):
            unusedIds.append(aId)
    return unusedIds


# --------------------------------------------- symbols used in dims and spots  ------------------
'''centre line symbols and spot symbols'''

# doc   current model document
def GetSymbolIdsFromDimTypes(doc):
    '''
    returns all symbol ids used as centre line symbol from all dim styles in the model
    '''
    ids = []
    dimTs = GetDimTypes(doc)
    for t in dimTs:
        id = com.GetBuiltInParameterValue(t, rdb.BuiltInParameter.DIM_STYLE_CENTERLINE_SYMBOL)
        if(id not in ids and id != rdb.ElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids

# doc   current model document
def GetSymbolIdsFromSpotTypes(doc):
    '''
    returns all symbol ids used as symbol from all spot elevation and coordinate
    '''
    ids = []
    dimTs = GetAllSpotDimTypes(doc)
    for t in dimTs:
        id = com.GetBuiltInParameterValue(t, rdb.BuiltInParameter.SPOT_ELEV_SYMBOL)
        if(id not in ids and id != rdb.ElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids

# doc   current model document
def GetAllSpotElevationSymbolsInModel(doc):
    '''
    returns all symbol of category Spot Elevation Symbol in model
    '''
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_SpotElevSymbols)
    return col

# doc   current model document
def GetAllSpotElevationSymbolIdsInModel(doc):
    '''
    returns all symbol of category Spot Elevation Symbol in model
    '''
    col = GetAllSpotElevationSymbolsInModel(doc)
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetUnusedSymbolIdsFromSpotTypes(doc):
    '''
    Get all symbol ids not used as symbol in any spot elevation or spot coordinate.
    

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids representing unused spot elevation or coordiante symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = []
    idsAvailable = GetAllSpotElevationSymbolIdsInModel(doc)
    dimTs = GetAllSpotDimTypes(doc)
    for t in dimTs:
        id = com.GetBuiltInParameterValue(t, rdb.BuiltInParameter.SPOT_ELEV_SYMBOL)
        if(id not in idsUsed and id != rdb.ElementId.InvalidElementId and id != None):
            idsUsed.append(id)
                
    # get unused ids
    for id in idsAvailable:
        if(id not in idsUsed):
            ids.append(id)
    return ids

# doc   current model document
def GetUnusedSymbolIdsFromSpotTypesToPurge(doc):
    '''get all un used symbol ids of category
    BuiltInCategory.OST_SpotElevSymbols
    '''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedSymbolIdsFromSpotTypes)
    return ids
