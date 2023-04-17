'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit stairs and stair sub element types.
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

from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples.Stairs import RevitStairs as rStair
from duHast.APISamples.Stairs.Utility import RevitStairsTypeSorting as rStairSort
from duHast.APISamples.Stairs import RevitStairCutMarks as rStairCut
from duHast.APISamples.Stairs import RevitStairLandings as rStairLanding
from duHast.APISamples.Stairs import RevitStairPath as rStairPath
from duHast.APISamples.Stairs import RevitStairRuns as rStairRun
from duHast.APISamples.Stairs import RevitStairStringersAndCarriages as rStairStringersAndCarriages

#: Built in stair family name for basic stairs
BASIC_STAIR_FAMILY_NAME = 'Stair'

#: Built in stair family name for assembled stairs
ASSEMBLED_STAIR_FAMILY_NAME = 'Assembled Stair'

#: Built in stair family name for precast stairs
PRECAST_STAIR_FAMILY_NAME = 'Precast Stair'

#: Built in stair family name for cast in place stairs
CAST_IN_PLACE_STAIR_FAMILY_NAME = 'Cast-In-Place Stair'

#: List of all Built in stair family names
BUILTIN_STAIR_TYPE_FAMILY_NAMES = [
    BASIC_STAIR_FAMILY_NAME,
    ASSEMBLED_STAIR_FAMILY_NAME,
    PRECAST_STAIR_FAMILY_NAME,
    CAST_IN_PLACE_STAIR_FAMILY_NAME
]

def get_used_stair_type_ids(doc):
    '''
    Gets all used in Stair type ids.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc,  rStair.get_all_stair_type_ids_by_category, 1)
    return ids


def family_no_types_in_use(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of ids. True if any id is not in unUsedTypeIds.
    TODO: check for more generic list comparison and remove this function.
    :param famTypeIds: List of family type ids to check.
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: Reference list of ids.
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId
    :return: True if any id from amTypeIds is not in unUsedTypeIds.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match




# -------------------------------- none in place Stair types purge -------------------------------------------------------
def get_unused_non_in_place_stair_type_ids_to_purge(doc):
    '''
    Gets all unused Stair type ids for.
    Included are:
    - Stair Soffit
    - Compound Stair
    - Basic Stair
    It will therefore not return any in place family types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(doc, rStair.get_all_stair_type_ids_by_class, 0)
    # make sure there is at least on Stair type per system family left in model
    StairTypes =  rStairSort.sort_stair_types_by_family_name(doc)
    for key, value in StairTypes.items():
       if(key in BUILTIN_STAIR_TYPE_FAMILY_NAMES):
            if(family_no_types_in_use(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids

#--------------------------------utility functions to get unused sub types ----------------------

def get_used_sub_type_ids_from_stair_type(doc, stairTypeId, paras):
    '''
    Gets the id of types making up a stair.
    These could be stair landing types, stringer and carriage types etc.
    Types returned depend on parameter definitions past in. 
    Refer to: 
    - STAIR_LANDING_TYPE_PARAS, 
    - STAIR_CUTMARK_TYPE_PARAS, 
    - STAIR_SUPPORT_TYPE_PARAS 

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param stairTypeId: An element id representing a stair type. 
    :type stairTypeId: Autodesk.Revit.DB.ElementId
    :param paras: Parameters containing a type making up a stair.
    :type paras: list Autodesk.Revit.DB.BuiltInParameterDefinition
    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    stairType = doc.GetElement(stairTypeId)
    for pDef in paras:
        pValue = rParaGet.get_built_in_parameter_value(stairType, pDef)
        if(pValue !=None and pValue not in ids):
            ids.append(pValue)
    return ids


def get_all_similar_type_ids(doc, ids):
    '''
    Gets all unique ids of similar types of element ids passed in.
    TODO: check for similar function elsewhere!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: list of type ids to be added to.
    :type ids: list of Autodesk.Revit.ElementIds
    :return: List of unique ids of similar types.
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    simIds = []
    for id in ids:
         el = doc.GetElement(id)
         simTypes = el.GetSimilarTypes()
         for st in simTypes:
            if (st not in simIds):
                simIds.append(st)
    return simIds


def build_system_family_dictionary(doc, ids):
    '''
    Returns dictionary where key is the system family name and values list of available type ids of that system family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List of system family ids.
    :type ids: list of Autodesk.Revit.ElementIds
    :return: Dictionary of unique ids of similar types.
    :rtype: dictionary {str: list of Autodesk.Revit.ElementIds } 
    '''

    dic = {}
    for id in ids:
        el = doc.GetElement(id)
        if(dic.has_key(el.FamilyName)):
            dic[el.FamilyName].append(id)
        else:
            dic[el.FamilyName] = [id]
    return dic


def check_system_families(doc, ids, leaveOneBehind):
    '''
    Check whether a list of ids of system family is the entire list of types available in the model. If so it will remove one\
    type id per system family to allow safe purging.
    Revit requires at least one type definition per system family to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List of ids to check
    :type ids: list of Autodesk.Revit.ElementIds
    :param leaveOneBehind: True: at least one type will be omitted from list.
    :type leaveOneBehind: bool
    :return: List of unique ids of similar types.
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    dicToCheck = build_system_family_dictionary(doc, ids)
    similarIds = get_all_similar_type_ids(doc, ids)
    dicReference = build_system_family_dictionary(doc, similarIds)
    ids = []
    for key,value in dicToCheck.items():
        if (dicReference.has_key(key)):
            if(len(dicReference[key]) == len(dicToCheck[key]) and leaveOneBehind):
                # need to leave one behind...
                if(len(dicToCheck[key])>0):
                    dicToCheck[key].pop(0)
                    ids = ids + dicToCheck[key]
            else:
                 ids = ids + dicToCheck[key]
        else:
            ids = ids + dicToCheck[key]
    return ids


def get_used_sub_types(doc, availableIdsGetter, paras, leaveOneBehind = True):
    '''
    Returns a list of type ids which are not used in any stair types. 
    Type ids are provided via an id getter function
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param availableIdsGetter: function returning available type ids
    :type availableIdsGetter: func(doc)
    :param paras: list of built in parameters attached to a stair type for given sub types (stringers, path, run, landing)
    :type paras: list of Autodesk.Revit.DB.BuiltInParameter
    :param leaveOneBehind: _description_, defaults to True
    :type leaveOneBehind: bool, optional
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = []
    # get all available type ids and then check against all Stair type ids
    idsAvailable = availableIdsGetter(doc)
    allUsedStairTypeIds = rStair.get_all_stair_type_ids_by_category(doc)
    idsUsedTypes = []
    for used in allUsedStairTypeIds:
        idsUsed = get_used_sub_type_ids_from_stair_type(doc, used, paras)
        for id in idsUsed:
            if(id not in idsUsedTypes):
                idsUsedTypes.append(id)
    for idAvailable in idsAvailable:
        if(idAvailable not in idsUsedTypes):
            ids.append(idAvailable)
    # need to check that we are not trying to delete last type of a system family....
    ids = check_system_families(doc, ids, leaveOneBehind)
    return ids

# --------------------------------- purging subtypes ------------------------------------------------

def get_unused_stair_path_type_ids_to_purge(doc):
    '''
    Gets all unused Stair path ids to purge, will omit on path type id per system family if none are used.
    This method can be used to safely delete unused stair path types. In the case that no stair\
        path instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair path type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    idsUsed = []
    availableTypes = rStairPath.get_stair_path_types_ids_by_class(doc)
    col = rStairPath.get_all_stair_path_instances(doc)
    for c in col:
        if (c.GetTypeId() not in idsUsed):
            idsUsed.append(c.GetTypeId())
    ids = []
    for at in availableTypes:
        if(at not in idsUsed):
            ids.append(at)
    ids = check_system_families(doc, ids, True)
    return ids


def get_unused_stair_landing_type_ids_to_purge(doc):
    '''
    Gets all unused Stair landing type ids.
    This method can be used to safely delete unused stair landing types. In the case that no stair\
        landing instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair landing type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = get_used_sub_types(doc, rStairLanding.get_stair_landing_types_ids_by_class, rStairLanding.STAIR_LANDING_TYPE_PARAS)
    return ids


def get_unused_stair_run_type_ids_to_purge(doc):
    '''
    Gets all unused Stair run type ids.
    This method can be used to safely delete unused stair run types. In the case that no stair\
        run instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair run type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = get_used_sub_types(doc, rStairRun.get_stair_run_types_ids_by_class, rStairRun.STAIR_RUN_TYPE_PARAS)
    return ids


def get_unused_stair_cut_mark_type_ids_to_purge(doc):
    '''
    Gets all unused Stair cut mark type ids.
    This method can be used to safely delete unused stair cut mark types. In the case that no stair\
        cut mark instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair cut mark type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = get_used_sub_types(doc, rStairCut.get_stair_cut_mark_types_ids_by_class, rStairCut.STAIR_CUT_MARK_TYPE_PARAS)
    return ids


def get_unused_stair_stringers_carriage_type_ids_to_purge(doc):
    '''
    Gets all unused Stair stringer / carriage type ids.
    This method can be used to safely delete unused stair stringer / carriage types. In the case that no stair\
        string carriage instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stringer carriage type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = get_used_sub_types(doc, rStairStringersAndCarriages.get_all_stair_stringers_carriage_type_ids_by_category, rStairStringersAndCarriages.STAIR_SUPPORT_TYPE_PARAS)
    return ids

# -------------------------------- In place Stair types -------------------------------------------------------

def get_used_in_place_stair_type_ids(doc):
    '''
    Gets all used in place stair type ids.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, rStair.get_all_in_place_stair_type_ids, 1)
    return ids


def get_unused_in_place_stair_type_ids(doc):
    '''
    Gets all unused in place stair type ids.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, rStair.get_all_in_place_stair_type_ids, 0)
    return ids


def get_unused_in_place_stair_type_ids_for_purge(doc):
    '''
    Gets symbol (type) ids and family ids (when no type is in use) of in place Stair families which can be purged.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    '''

    ids = rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_in_place_stair_type_ids)
    return ids


