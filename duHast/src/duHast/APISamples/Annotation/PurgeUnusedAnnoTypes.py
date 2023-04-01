'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging annotation types. 
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

import Autodesk.Revit.DB as rdb


from duHast.APISamples.Annotation import RevitGenericAnnotation as rGenericAnno
from duHast.APISamples.Family import RevitFamilyUtils as rFam
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Annotation import RevitAnnotation as rAnno
from duHast.APISamples.Annotation import RevitDimensions as rDim
from duHast.APISamples.Annotation import RevitMultiRefAnno as rMultiRefAnno
from duHast.APISamples.Annotation import RevitText as rText
from duHast.APISamples.Annotation import RevitArrowHeads as rArrow
from duHast.APISamples.Annotation import RevitIndependentTags as rIndyTags
from duHast.APISamples.Annotation import RevitSpotDimensions as rSpots
from duHast.APISamples.Annotation import RevitStairPath as rStairPath


# ------------------ used annotation types  ------------------

def GetUsedTextTypeIdsInTheModel(doc):
    '''
    Gets all ids of text types used by elements in the model, includes types used in schedules (appearance)!
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    textTypeIdsUsed = []
    col = rText.GetAllTextAnnotationElements(doc)
    for t in col:
        if(t.GetTypeId() not in textTypeIdsUsed):
            textTypeIdsUsed.append(t.GetTypeId())
    # get all schedules and check their appearance text properties!
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSchedule)
    for c in col:
        if(c.BodyTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.BodyTextTypeId)
        if(c.HeaderTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.HeaderTextTypeId)
        if(c.TitleTextTypeId not in textTypeIdsUsed):
            textTypeIdsUsed.append(c.TitleTextTypeId)
    return textTypeIdsUsed

def GetUsedDimTypeIdsInTheModel(doc):
    '''
    Gets all used dimension type Ids in the model.
    Used: at least one instance using this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing Dimension Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    dimTypeIdsUsed = []
    col = rDim.GetAllDimensionElements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

def GetUsedDimStylesFromMultiRef(doc, multiReferenceAnnoTypes):
    '''
    Gets all dimension styles used in multi ref annotation types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param multiReferenceAnnoTypes: list in format [[multi refType, [element ids of similar multi ref types, ...]]]
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

def GetUsedMultiRefDimTypeIdsInTheModel(doc):
    '''
    Gets all ids of multi reference types used by elements in the model.
    Used: at least one instance using this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi reference Annotation Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    dimTypeIdsUsed = []
    col = rMultiRefAnno.GetAllMultiRefAnnotationElements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

def GetAllUsedArrowHeadTypeIdsInModel(doc):
    '''
    Returns all used arrow types in the model.
    Used in types of dimension, text, independent tags, spot dims, annotation symbols (incl room and area tags), stairs path
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedIds = []
    usedIds = usedIds + rDim.GetDimTypeArrowHeadIds(doc)
    usedIds = usedIds + rText.GetTextTypeArrowHeadIds(doc)
    usedIds = usedIds + rIndyTags.GetIndependentTagTypeArrowHeadIds(doc)
    usedIds = usedIds + rSpots.GetSpotTypeArrowHeadIds(doc)
    usedIds = usedIds + rAnno.GetAnnoSymbolArrowHeadIds(doc)
    usedIds = usedIds + rStairPath.GetStairsPathArrowHeadIds(doc)
    filteredIds = []
    for u in usedIds:
        if (u not in filteredIds):
            filteredIds.append(u)
    return filteredIds


# ------------------ unused annotation types  ------------------


def GetAllUnusedTextTypeIdsInModel(doc):
    '''
    Gets ID of all unused text types in the model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filteredUnusedTextTypeIds = com.GetUnusedTypeIdsInModel(doc, rText.GetAllTextTypes, GetUsedTextTypeIdsInTheModel)
    return filteredUnusedTextTypeIds

def GetAllUnusedDimTypeIdsInModel(doc):
    '''
    Gets ID of all unused dim types in the model.
    Includes checking multi ref dims for used dim types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused dimension type ids
    filteredUnusedDimTypeIds = com.GetUnusedTypeIdsInModel(doc, rDim.GetDimTypes, GetUsedDimTypeIdsInTheModel)
    # get all multi ref dimension types in model
    multiReferenceAnnoTypes = rMultiRefAnno.GetAllSimilarMultiReferenceAnnoTypes(doc)
    # get all dim styles used in multi refs
    usedDimStylesInMultiRefs = GetUsedDimStylesFromMultiRef(doc, multiReferenceAnnoTypes)
    # cross reference filtered list vs multi ref list and only keep items which are just in the filtered list
    unusedDimTypeIds = []
    for f in filteredUnusedDimTypeIds:
        if(f not in usedDimStylesInMultiRefs):
            unusedDimTypeIds.append(f)
    return unusedDimTypeIds

def GetAllUnusedMultiRefDimTypeIdsInModel(doc):
    '''
    Gets IDs of all unused multi ref dimension types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi ref dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return com.GetUnusedTypeIdsInModel(doc, rMultiRefAnno.GetAllMultiRefAnnotationTypes, GetUsedMultiRefDimTypeIdsInTheModel)

def GetAllUnusedArrowTypeIdsInModel(doc):
    '''
    Gets all unused arrow type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    unusedIds = []
    usedIds = GetAllUsedArrowHeadTypeIdsInModel(doc)
    availableIds =rArrow.GetArrowTypesIdsInModel(doc)
    for aId in availableIds:
        if(aId not in usedIds):
            unusedIds.append(aId)
    return unusedIds


def GetUnusedSymbolIdsFromSpotTypes(doc):
    '''
    Gets all family symbol ids not used as symbol in any spot elevation or spot coordinate type definition.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols not used in spot elevation or spot coordinate type definition.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = []
    idsAvailable = rSpots.GetAllSpotElevationSymbolIdsInModel(doc)
    dimTs = rSpots.GetAllSpotDimTypes(doc)
    for t in dimTs:
        id = rParaGet.get_built_in_parameter_value (t, rdb.BuiltInParameter.SPOT_ELEV_SYMBOL)
        if(id not in idsUsed and id != rdb.ElementId.InvalidElementId and id != None):
            idsUsed.append(id)

    # get unused ids
    for id in idsAvailable:
        if(id not in idsUsed):
            ids.append(id)
    return ids


def GetUnusedSymbolIdsFromSpotTypesToPurge(doc):
    '''
    Gets all unused family and family symbol ids of category BuiltInCategory.OST_SpotElevSymbols. 
    This method can be used to safely delete unused families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family and family symbols not used in spot elevation or spot coordinate type definition.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedSymbolIdsFromSpotTypes)
    return ids


def GetUsedGenericAnnotationTypeIds(doc):
    '''
    Returns all used generic annotation symbol ids ( used in model as well as dimension types)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # get ids from symbols used in dim types
    idsDimTypes = rDim.GetSymbolIdsFromDimTypes(doc)
    # get ids from symbols used in spots
    idsSpots = rAnno.GetSymbolIdsFromSpotTypes(doc)
    # get detail types used in model
    idsUsedInModel = com.GetUsedUnusedTypeIds(doc, rGenericAnno.GetAllGenericAnnotationTypeIdsByCategory, 1)
    # build overall list
    for id in idsUsedInModel:
        ids.append(id)
    for id in idsDimTypes:
        if(id not in ids):
            ids.append(id)
    for id in idsSpots:
        if (id not in ids):
            ids.append(id)
    return ids


def GetUnusedGenericAnnotationTypeIds(doc):
    '''
    Returns all unused annotation symbol ids ( unused in model as well as dimension types)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = GetUsedGenericAnnotationTypeIds(doc)
    idsAll = rGenericAnno.GetAllGenericAnnotationTypeIdsByCategory(doc)
    for id in idsAll:
        if (id not in idsUsed):
            ids.append(id)
    return ids


def GetUnusedGenericAnnotationIdsForPurge(doc):
    '''
    returns symbol(type) ids and family ids (when no type is in use) of in generic anno families which can be purged
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedGenericAnnotationTypeIds)
    return ids