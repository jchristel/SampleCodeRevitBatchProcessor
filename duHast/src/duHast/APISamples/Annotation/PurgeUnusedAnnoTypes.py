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
from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge
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
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
 

# ------------------ used annotation types  ------------------

def get_used_text_type_ids_in_model(doc):
    '''
    Gets all ids of text types used by elements in the model, includes types used in schedules (appearance)!
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    textTypeIdsUsed = []
    col = rText.get_all_text_annotation_elements(doc)
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

def get_used_dim_type_ids_in_model(doc):
    '''
    Gets all used dimension type Ids in the model.
    Used: at least one instance using this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing Dimension Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    dimTypeIdsUsed = []
    col = rDim.get_all_dimension_elements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

def get_used_dim_styles_from_multi_ref(doc, multiReferenceAnnoTypes):
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

def get_used_multi_ref_dim_type_ids_in_model(doc):
    '''
    Gets all ids of multi reference types used by elements in the model.
    Used: at least one instance using this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi reference Annotation Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    dimTypeIdsUsed = []
    col = rMultiRefAnno.get_all_multi_ref_annotation_elements(doc)
    for v in col:
        if(v.GetTypeId() not in dimTypeIdsUsed):
            dimTypeIdsUsed.append(v.GetTypeId())
    return dimTypeIdsUsed

def get_all_used_arrow_head_type_ids_in_model(doc):
    '''
    Returns all used arrow types in the model.
    Used in types of dimension, text, independent tags, spot dims, annotation symbols (incl room and area tags), stairs path
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedIds = []
    usedIds = usedIds + rDim.get_dim_type_arrow_head_ids(doc)
    usedIds = usedIds + rText.get_text_type_arrow_head_ids(doc)
    usedIds = usedIds + rIndyTags.get_independent_tag_type_arrow_head_ids(doc)
    usedIds = usedIds + rSpots.get_spot_type_arrow_head_ids(doc)
    usedIds = usedIds + rAnno.get_anno_symbol_arrow_head_ids(doc)
    usedIds = usedIds + rStairPath.get_stairs_path_arrow_head_ids(doc)
    filteredIds = []
    for u in usedIds:
        if (u not in filteredIds):
            filteredIds.append(u)
    return filteredIds


# ------------------ unused annotation types  ------------------


def get_all_unused_text_type_ids_in_model(doc):
    '''
    Gets ID of all unused text types in the model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filteredUnusedTextTypeIds = com.get_unused_type_ids_in_model(doc, rText.get_all_text_types, get_used_text_type_ids_in_model)
    return filteredUnusedTextTypeIds

def get_all_unused_dim_type_ids_in_model(doc):
    '''
    Gets ID of all unused dim types in the model.
    Includes checking multi ref dims for used dim types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused dimension type ids
    filteredUnusedDimTypeIds = com.get_unused_type_ids_in_model(doc, rDim.get_dim_types, get_used_dim_type_ids_in_model)
    # get all multi ref dimension types in model
    multiReferenceAnnoTypes = rMultiRefAnno.get_all_similar_multi_reference_anno_types(doc)
    # get all dim styles used in multi refs
    usedDimStylesInMultiRefs = get_used_dim_styles_from_multi_ref(doc, multiReferenceAnnoTypes)
    # cross reference filtered list vs multi ref list and only keep items which are just in the filtered list
    unusedDimTypeIds = []
    for f in filteredUnusedDimTypeIds:
        if(f not in usedDimStylesInMultiRefs):
            unusedDimTypeIds.append(f)
    return unusedDimTypeIds

def get_all_unused_multi_ref_dim_type_ids_in_model(doc):
    '''
    Gets IDs of all unused multi ref dimension types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi ref dimension types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return com.get_unused_type_ids_in_model(doc, rMultiRefAnno.get_all_multi_ref_annotation_types, get_used_multi_ref_dim_type_ids_in_model)

def get_all_unused_arrow_type_ids_in_model(doc):
    '''
    Gets all unused arrow type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    unusedIds = []
    usedIds = get_all_used_arrow_head_type_ids_in_model(doc)
    availableIds =rArrow.get_arrow_type_ids_in_model(doc)
    for aId in availableIds:
        if(aId not in usedIds):
            unusedIds.append(aId)
    return unusedIds


def get_unused_symbol_ids_from_spot_types(doc):
    '''
    Gets all family symbol ids not used as symbol in any spot elevation or spot coordinate type definition.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols not used in spot elevation or spot coordinate type definition.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = []
    idsAvailable = rSpots.get_all_spot_elevation_symbol_ids_in_model(doc)
    dimTs = rSpots.get_all_spot_dim_types(doc)
    for t in dimTs:
        id = rParaGet.get_built_in_parameter_value (t, rdb.BuiltInParameter.SPOT_ELEV_SYMBOL)
        if(id not in idsUsed and id != rdb.ElementId.InvalidElementId and id != None):
            idsUsed.append(id)

    # get unused ids
    for id in idsAvailable:
        if(id not in idsUsed):
            ids.append(id)
    return ids


def get_unused_symbol_ids_from_spot_types_to_purge(doc):
    '''
    Gets all unused family and family symbol ids of category BuiltInCategory.OST_SpotElevSymbols. 
    This method can be used to safely delete unused families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family and family symbols not used in spot elevation or spot coordinate type definition.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.GetUnusedInPlaceIdsForPurge(doc, get_unused_symbol_ids_from_spot_types)
    return ids


def get_used_generic_annotation_type_ids(doc):
    '''
    Returns all used generic annotation symbol ids ( used in model as well as dimension types)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # get ids from symbols used in dim types
    idsDimTypes = rDim.get_symbol_ids_from_dim_types(doc)
    # get ids from symbols used in spots
    idsSpots = rAnno.GetSymbolIdsFromSpotTypes(doc)
    # get detail types used in model
    idsUsedInModel = rPurgeUtils.get_used_unused_type_ids(doc, rGenericAnno.get_all_generic_annotation_type_ids_by_category, 1)
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


def get_unused_generic_annotation_type_ids(doc):
    '''
    Returns all unused annotation symbol ids ( unused in model as well as dimension types)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    idsUsed = get_used_generic_annotation_type_ids(doc)
    idsAll = rGenericAnno.get_all_generic_annotation_type_ids_by_category(doc)
    for id in idsAll:
        if (id not in idsUsed):
            ids.append(id)
    return ids


def get_unused_generic_annotation_ids_for_purge(doc):
    '''
    returns symbol(type) ids and family ids (when no type is in use) of in generic anno families which can be purged
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.GetUnusedInPlaceIdsForPurge(doc, get_unused_generic_annotation_type_ids)
    return ids