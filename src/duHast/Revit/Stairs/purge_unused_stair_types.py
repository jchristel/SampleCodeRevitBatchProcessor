"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit stairs and stair sub element types.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

from duHast.Revit.Family import purge_unused_family_types as rFamPurge
from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Stairs import stairs as rStair
from duHast.Revit.Stairs.Utility import stairs_type_sorting as rStairSort
from duHast.Revit.Stairs import cut_marks as rStairCut
from duHast.Revit.Stairs import landings as rStairLanding
from duHast.Revit.Stairs import path as rStairPath
from duHast.Revit.Stairs import runs as rStairRun
from duHast.Revit.Stairs import stringers_carriages as rStairStringersAndCarriages

#: Built in stair family name for basic stairs
BASIC_STAIR_FAMILY_NAME = "Stair"

#: Built in stair family name for assembled stairs
ASSEMBLED_STAIR_FAMILY_NAME = "Assembled Stair"

#: Built in stair family name for precast stairs
PRECAST_STAIR_FAMILY_NAME = "Precast Stair"

#: Built in stair family name for cast in place stairs
CAST_IN_PLACE_STAIR_FAMILY_NAME = "Cast-In-Place Stair"

#: List of all Built in stair family names
BUILTIN_STAIR_TYPE_FAMILY_NAMES = [
    BASIC_STAIR_FAMILY_NAME,
    ASSEMBLED_STAIR_FAMILY_NAME,
    PRECAST_STAIR_FAMILY_NAME,
    CAST_IN_PLACE_STAIR_FAMILY_NAME,
]


def get_used_stair_type_ids(doc):
    """
    Gets all used in Stair type ids.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rStair.get_all_stair_type_ids_by_category, 1
    )
    return ids


def family_no_types_in_use(fam_type_ids, un_used_type_ids):
    """
    Compares two lists of ids. True if any id is not in un_used_type_ids.
    TODO: check for more generic list comparison and remove this function.
    :param fam_type_ids: List of family type ids to check.
    :type fam_type_ids: List of Autodesk.Revit.DB.ElementId
    :param un_used_type_ids: Reference list of ids.
    :type un_used_type_ids: List of Autodesk.Revit.DB.ElementId
    :return: True if any id from amTypeIds is not in un_used_type_ids.
    :rtype: bool
    """

    match = True
    for fam_type_id in fam_type_ids:
        if fam_type_id not in un_used_type_ids:
            match = False
            break
    return match


# -------------------------------- none in place Stair types purge -------------------------------------------------------
def get_unused_non_in_place_stair_type_ids_to_purge(doc):
    """
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
    """

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rStair.get_all_stair_type_ids_by_class, 0
    )
    # make sure there is at least on Stair type per system family left in model
    stair_types = rStairSort.sort_stair_types_by_family_name(doc)
    for key, value in stair_types.items():
        if key in BUILTIN_STAIR_TYPE_FAMILY_NAMES:
            if family_no_types_in_use(value, ids) == True:
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


# --------------------------------utility functions to get unused sub types ----------------------


def get_used_sub_type_ids_from_stair_type(doc, stair_type_id, paras):
    """
    Gets the id of types making up a stair.
    These could be stair landing types, stringer and carriage types etc.
    Types returned depend on parameter definitions past in.
    Refer to:
    - STAIR_LANDING_TYPE_PARAS,
    - STAIR_CUTMARK_TYPE_PARAS,
    - STAIR_SUPPORT_TYPE_PARAS

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param stair_type_id: An element id representing a stair type.
    :type stair_type_id: Autodesk.Revit.DB.ElementId
    :param paras: Parameters containing a type making up a stair.
    :type paras: list Autodesk.Revit.DB.BuiltInParameterDefinition
    :return: List of element ids representing stair types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    stair_type = doc.GetElement(stair_type_id)
    for p_def in paras:
        p_value = rParaGet.get_built_in_parameter_value(stair_type, p_def)
        if p_value != None and p_value not in ids:
            ids.append(p_value)
    return ids


def get_all_similar_type_ids(doc, ids):
    """
    Gets all unique ids of similar types of element ids passed in.
    TODO: check for similar function elsewhere!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: list of type ids to be added to.
    :type ids: list of Autodesk.Revit.ElementIds
    :return: List of unique ids of similar types.
    :rtype: list of Autodesk.Revit.ElementIds
    """

    sim_ids = []
    for id in ids:
        el = doc.GetElement(id)
        sim_types = el.GetSimilarTypes()
        for st in sim_types:
            if st not in sim_ids:
                sim_ids.append(st)
    return sim_ids


def build_system_family_dictionary(doc, ids):
    """
    Returns dictionary where key is the system family name and values list of available type ids of that system family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List of system family ids.
    :type ids: list of Autodesk.Revit.ElementIds
    :return: Dictionary of unique ids of similar types.
    :rtype: dictionary {str: list of Autodesk.Revit.ElementIds }
    """

    dic = {}
    for id in ids:
        el = doc.GetElement(id)
        if dic.has_key(el.FamilyName):
            dic[el.FamilyName].append(id)
        else:
            dic[el.FamilyName] = [id]
    return dic


def check_system_families(doc, ids, leave_one_behind):
    """
    Check whether a list of ids of system family is the entire list of types available in the model. If so it will remove one\
    type id per system family to allow safe purging.
    Revit requires at least one type definition per system family to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List of ids to check
    :type ids: list of Autodesk.Revit.ElementIds
    :param leave_one_behind: True: at least one type will be omitted from list.
    :type leave_one_behind: bool
    :return: List of unique ids of similar types.
    :rtype: list of Autodesk.Revit.ElementIds
    """

    dic_to_check = build_system_family_dictionary(doc, ids)
    similar_ids = get_all_similar_type_ids(doc, ids)
    dic_reference = build_system_family_dictionary(doc, similar_ids)
    ids = []
    for key, value in dic_to_check.items():
        if dic_reference.has_key(key):
            if len(dic_reference[key]) == len(dic_to_check[key]) and leave_one_behind:
                # need to leave one behind...
                if len(dic_to_check[key]) > 0:
                    dic_to_check[key].pop(0)
                    ids = ids + dic_to_check[key]
            else:
                ids = ids + dic_to_check[key]
        else:
            ids = ids + dic_to_check[key]
    return ids


def get_used_sub_types(doc, available_ids_getter, paras, leave_one_behind=True):
    """
    Returns a list of type ids which are not used in any stair types.
    Type ids are provided via an id getter function
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param available_ids_getter: function returning available type ids
    :type available_ids_getter: func(doc)
    :param paras: list of built in parameters attached to a stair type for given sub types (stringers, path, run, landing)
    :type paras: list of Autodesk.Revit.DB.BuiltInParameter
    :param leave_one_behind: _description_, defaults to True
    :type leave_one_behind: bool, optional
    :return: List of element ids
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = []
    # get all available type ids and then check against all Stair type ids
    ids_available = available_ids_getter(doc)
    all_used_stair_type_ids = rStair.get_all_stair_type_ids_by_category(doc)
    ids_used_types = []
    for used in all_used_stair_type_ids:
        ids_used = get_used_sub_type_ids_from_stair_type(doc, used, paras)
        for id in ids_used:
            if id not in ids_used_types:
                ids_used_types.append(id)
    for id_available in ids_available:
        if id_available not in ids_used_types:
            ids.append(id_available)
    # need to check that we are not trying to delete last type of a system family....
    ids = check_system_families(doc, ids, leave_one_behind)
    return ids


# --------------------------------- purging subtypes ------------------------------------------------


def get_unused_stair_path_type_ids_to_purge(doc):
    """
    Gets all unused Stair path ids to purge, will omit on path type id per system family if none are used.
    This method can be used to safely delete unused stair path types. In the case that no stair\
        path instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair path type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids_used = []
    available_types = rStairPath.get_stair_path_types_ids_by_class(doc)
    col = rStairPath.get_all_stair_path_instances(doc)
    for c in col:
        if c.GetTypeId() not in ids_used:
            ids_used.append(c.GetTypeId())
    ids = []
    for at in available_types:
        if at not in ids_used:
            ids.append(at)
    ids = check_system_families(doc, ids, True)
    return ids


def get_unused_stair_landing_type_ids_to_purge(doc):
    """
    Gets all unused Stair landing type ids.
    This method can be used to safely delete unused stair landing types. In the case that no stair\
        landing instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair landing type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = get_used_sub_types(
        doc,
        rStairLanding.get_stair_landing_types_ids_by_class,
        rStairLanding.STAIR_LANDING_TYPE_PARAS,
    )
    return ids


def get_unused_stair_run_type_ids_to_purge(doc):
    """
    Gets all unused Stair run type ids.
    This method can be used to safely delete unused stair run types. In the case that no stair\
        run instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair run type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = get_used_sub_types(
        doc, rStairRun.get_stair_run_types_ids_by_class, rStairRun.STAIR_RUN_TYPE_PARAS
    )
    return ids


def get_unused_stair_cut_mark_type_ids_to_purge(doc):
    """
    Gets all unused Stair cut mark type ids.
    This method can be used to safely delete unused stair cut mark types. In the case that no stair\
        cut mark instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stair cut mark type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = get_used_sub_types(
        doc,
        rStairCut.get_stair_cut_mark_types_ids_by_class,
        rStairCut.STAIR_CUT_MARK_TYPE_PARAS,
    )
    return ids


def get_unused_stair_stringers_carriage_type_ids_to_purge(doc):
    """
    Gets all unused Stair stringer / carriage type ids.
    This method can be used to safely delete unused stair stringer / carriage types. In the case that no stair\
        string carriage instance using any of the types is placed, this will return all but one type id since\
        Revit requires at least one stringer carriage type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids 
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = get_used_sub_types(
        doc,
        rStairStringersAndCarriages.get_all_stair_stringers_carriage_type_ids_by_category,
        rStairStringersAndCarriages.STAIR_SUPPORT_TYPE_PARAS,
    )
    return ids


# -------------------------------- In place Stair types -------------------------------------------------------


def get_used_in_place_stair_type_ids(doc):
    """
    Gets all used in place stair type ids.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rStair.get_all_in_place_stair_type_ids, 1
    )
    return ids


def get_unused_in_place_stair_type_ids(doc):
    """
    Gets all unused in place stair type ids.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rStair.get_all_in_place_stair_type_ids, 0
    )
    return ids


def get_unused_in_place_stair_type_ids_for_purge(doc):
    """
    Gets symbol (type) ids and family ids (when no type is in use) of in place Stair families which can be purged.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids
    :rtype: list of Autodesk.Revit.ElementIds
    """

    ids = rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_in_place_stair_type_ids
    )
    return ids
