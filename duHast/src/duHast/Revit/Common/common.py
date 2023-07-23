"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Common Revit API utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#

# import datetime
import System
import clr


clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import glob
# class used for stats reporting

# import everything from Autodesk Revit DataBase namespace (Revit API)
import Autodesk.Revit.DB as rdb
import os.path as path

# utilities
from duHast.Utilities import utility as util
from duHast.Revit.Common import parameter_get_utils as rParaGet

# importing revit groups module
from duHast.Revit.Common import groups as rGroup


def get_element_mark(e):
    """
    Returns the mark value of an element.

    :param e: The element.
    :type e: Autodesk.Revit.DB.Element

    :return:
        The element mark value.
        If an exception occurred, the message will be 'Failed with exception: ' + the exception string.
    :rtype: str
    """

    mark = ""
    try:
        para_mark = e.get_Parameter(rdb.BuiltInParameter.ALL_MODEL_MARK)
        mark = "" if para_mark == None else para_mark.AsString()
    except Exception as e:
        mark = "Failed with exception: " + str(e)
    return mark


# ----------------------------------------Legend Components -----------------------------------------------


def get_legend_components_in_model(doc, type_ids):
    """
    Returns all symbol (type) ids of families which have been placed as legend components and have match in list past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param type_ids: List of typeIds to check against.
    :type type_ids: list str
    :raise: Any exception will need to be managed by the function caller.

    :return: Values are representing symbol (type) ids of legend components in models filtered by ids past in.
    :rtype: list of str
    """

    ids = []
    # get all legend components in the model to check against list past in
    col = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_LegendComponents
    )
    for c in col:
        id = rParaGet.get_built_in_parameter_value(
            c, rdb.BuiltInParameter.LEGEND_COMPONENT, rParaGet.get_parameter_value
        )
        if id in type_ids and id not in ids:
            ids.append(id)
            break
    return ids


# ----------------------------------------types - Autodesk.Revit.DB ElementType -----------------------------------------------


def get_similar_type_families_by_type(doc, type_getter):
    """
    Returns a list of unique types its similar family (symbol) types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param function type_getter:
        The function which takes the document as an argument and returns a list of family symbols (types).
    :raise: Any exception will need to be managed by the function caller.

    :return: list of Autodesk.Revit.DB.Symbol and Autodesk.Revit.DB.ElementId:
    :rtype: List [[Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    """

    sim_types = []
    types = type_getter(doc)
    for t in types:
        t_data = [t]
        sims = t.GetSimilarTypes()
        sim_data = []
        for sim in sims:
            sim_data.append(sim)
        # simData.sort() # not sure a sort is actually doing anything
        t_data.append(sim_data)
        if check_unique_type_data(sim_types, t_data):
            sim_types.append(t_data)
    return sim_types


def check_unique_type_data(existing_types, new_type_data):
    """
    Compares two lists of types and their similar types (ids).

    Assumes that second list past in has only one occurrence of type and its similar types
    Compares types by name and if match their similar types.

    :param existing_types: Source list
    :type existing_types: List of List in format [[Autodesk.Revit.DB.ElementType , Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    :param new_type_data: Comparison list
    :type new_type_data: List in format [Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...]

    :return:
        True, if new type is not in list existing Types passed in or
        if ids of similar family types do not match any similar types already in list
    :rtype: bool
    """

    result = True
    for s in existing_types:
        # check for matching family name
        if s[0].FamilyName == new_type_data[0].FamilyName:
            # check if match has the same amount of similar family types
            # if not it is unique
            if len(s[1]) == len(new_type_data[1]):
                # assume IDs do match
                match_i_ds = True
                for i in range(len(s[1])):
                    if s[1][i] != new_type_data[1][i]:
                        # id's dont match, this is unique
                        match_i_ds = False
                        break
                if match_i_ds:
                    # data is not unique
                    result = False
                    break
    return result


def get_unused_type_ids_in_model(doc, type_getter, instance_getter):
    """
    Returns ID of unused family types in the model.

    Used in purge code since it leaves at least one type behind (built in families require at least one type in the model)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param type_getter: Function accepting current document as argument and returning a collector of types in model
    :type type_getter: func
    :param instance_getter: Function accepting current document as argument and returning a list of instances in model
    :type instance_getter: func

    :return: List of type ids which can be purged from the model.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    # get all  types available and associated family types
    family_types_available = get_similar_type_families_by_type(doc, type_getter)
    # get used type ids
    used_family_type_ids = instance_getter(doc)
    # flag indicating that at least one type was removed from list because it is in use
    # this flag used when checking how many items are left...
    removed_at_least_one = []
    # set index to 0, type names might not be unique!!
    counter = 0
    # loop over available types and check which one is used
    for t in family_types_available:
        # remove all used family type Id's from the available list...
        # whatever is left can be deleted if not last available item in list for type
        # there should always be just one match
        for used_family_type_id in used_family_type_ids:
            # get the index of match
            index = util.index_of(t[1], used_family_type_id)
            # remove used item from list
            if index > -1:
                t[1].pop(index)
                if t not in removed_at_least_one:
                    removed_at_least_one.append(counter)
        counter = counter + 1
    # filter these by family types where is only one left
    # make sure to leave at least one family type behind, since the last type cannot be deleted
    filtered_unused_type_ids = []
    # reset index
    counter = 0
    for t in family_types_available:
        if counter in removed_at_least_one:
            # at least one item was already removed from list...so all left over ones can be purged
            for id in t[1]:
                # get the element
                t_fam = doc.GetElement(id)
                if t_fam.CanBeDeleted:
                    filtered_unused_type_ids.append(id)
        else:
            # need to keep at least one item
            if len(t[1]) > 1:
                # maxLength = len(t[1])
                # make sure to leave the first one behind to match Revit purge behavior
                for x in range(1, len(t[1])):
                    id = t[1][x]
                    # get the element
                    t_fam = doc.GetElement(id)
                    # check whether this can be deleted...
                    if t_fam.CanBeDeleted:
                        filtered_unused_type_ids.append(id)
        counter = counter + 1
    return filtered_unused_type_ids


# ----------------------------------------instances of types - Autodesk.Revit.DB ElementType -----------------------------------------------


def get_not_placed_types(doc, get_types, get_instances):
    """

    returns a list of unused types foo by comparing type Ids of placed instances with types past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param get_types: Types getter function. Needs to accept doc as argument and return a collector of type foo
    :type get_types: func (doc)
    :param get_instances: Instances getter function. Needs to accept doc as argument and return a collector of instances foo
    :type get_instances: func(doc)

    :return: returns a list of unused types
    :rtype: list of type foo
    """

    avail_types = get_types(doc)
    placed_instances = get_instances(doc)
    not_placed = []
    already_checked = []
    # loop over all types and check for matching instances
    for at in avail_types:
        match = False
        for pi in placed_instances:
            # check if we had this type checked already, if so ignore and move to next
            if pi.GetTypeId() not in already_checked:
                #  check for type id match
                if pi.GetTypeId() == at.Id:
                    # add to already checked and verified as match list
                    already_checked.append(pi.GetTypeId())
                    match = True
                    break
        if match == False:
            not_placed.append(at)
    return not_placed


# --------------------------------------------- check whether groups contain certain element types - Autodesk.Revit.DB ElementType  ------------------


def check_group_for_type_ids(doc, group_type, type_ids):
    """

    Filters passed in list of type ids by type ids found in group and returns list of unmatched Id's

    This only returns valid data if at least one instance of the group is placed in the model, otherwise GetMemberIds() returns empty!!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param group_type: Group to be checked whether they contains elements of types past in.
    :type group_type: Autodesk.Revit.DB.GroupType
    :param type_ids: List of type ids to confirm whether they are in use a group
    :type type_ids: list of Autodesk.Revit.Db.ElementId

    :return: Returns all type ids not matched
    :rtype: list of Autodesk.Revit.Db.ElementId
    """

    unused_type_ids = []
    used_type_ids = []
    # get the first group from the group type and get its members
    for g in group_type.Groups:
        # get ids of group elements:
        member_ids = g.GetMemberIds()
        # built list of used type ids
        for member_id in member_ids:
            member = doc.GetElement(member_id)
            used_type_id = member.GetTypeId()
            if used_type_id not in used_type_ids:
                used_type_ids.append(used_type_id)
    for check_id in type_ids:
        if check_id not in used_type_ids:
            unused_type_ids.append(check_id)
    return unused_type_ids


def check_groups_for_matching_type_ids(doc, group_types, type_ids):
    """
    Checks all elements in groups past in whether group includes element of which type Id is matching any type ids past in

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param group_types: Groups to be checked whether they contains elements of types past in.
    :type group_types: list of Autodesk.Revit.DB.GroupType
    :param type_ids: List of type ids to confirm whether they are in use a group
    :type type_ids: list of Autodesk.Revit.Db.ElementId

    :return: Returns all type ids not matched
    :rtype: list of Autodesk.Revit.Db.ElementId
    """

    for group_type in group_types:
        type_ids = check_group_for_type_ids(doc, group_type, type_ids)
        # check if all type ids where matched up
        if len(type_ids) == 0:
            break
    return type_ids


def get_unused_type_ids_from_detail_groups(doc, type_ids):
    """
    Checks elements in nested detail groups and detail groups whether their type ElementId is in the list past in.

    This only returns valid data if at least one instance of the group is placed in the model!!!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param type_ids: List of type ids to confirm whether they are in use a group
    :type type_ids: list of Autodesk.Revit.Db.ElementId

    :return: Returns all type Ids from list past in not found in group definitions
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    unused_type_ids = []
    nested_detail_groups = rGroup.get_nested_detail_groups(doc)
    detail_groups = rGroup.get_detail_groups(doc)
    unused_type_ids = check_groups_for_matching_type_ids(
        doc, nested_detail_groups, type_ids
    )
    unused_type_ids = check_groups_for_matching_type_ids(doc, detail_groups, type_ids)
    return unused_type_ids


# ----------------------------------------elements-----------------------------------------------


def get_ids_from_element_collector(col):
    """
    This will return a list of all element ids in collector.

    Any element in collector which is invalid will be ignored.

    :param col: A filtered element collector.
    :type col: Autodesk.Revit.DB.FilteredElementCollector

    :return: list of all element ids of valid elements in collector.
    :rtype: List of Autodesk.Revit.DB.ElementId
    """

    ids = []
    for c in col:
        try:
            ids.append(c.Id)
        except Exception as e:
            pass
    return ids
