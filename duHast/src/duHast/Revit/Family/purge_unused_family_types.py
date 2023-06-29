"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit family types. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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
from duHast.Revit.Common import purge_utils as rPurgeUtils
from duHast.Utilities import utility as util
from duHast.Revit.Family.family_utils import (
    get_family_symbols_ids,
    get_symbols_from_type,
)
from duHast.Revit.Family.Utility.loadable_family_categories import (
    CATEGORIES_LOADABLE_TAGS,
    CATEGORIES_LOADABLE_3D,
)


def family_all_types_in_use(fam_type_ids, used_type_ids):
    """
    Checks if symbols (types) of a family are in use in a model.
    Check is done by comparing entries of fam_type_ids with used_type_ids.
    :param fam_type_ids: list of symbol(type) ids of a family
    :type fam_type_ids: list Autodesk.Revit.DB.ElementId
    :param  used_type_ids: list of symbol(type) ids in use in a project
    :type used_type_ids: list Autodesk.Revit.DB.ElementId
    :return: False if a single symbol id contained in list fam_type_ids has a match in list used_type_ids, otherwise True.
    :rtype: bool
    """

    match = True
    for fam_type_id in fam_type_ids:
        if fam_type_id not in used_type_ids:
            match = False
            break
    return match


def get_unused_in_place_ids_for_purge(doc, unused_type_getter):
    """
    Filters symbol(type) ids and family ids (when not a single type of given family is in use) of families.
    The returned list of ids can be just unused family symbols or entire families if none of their symbols are in use.
    in terms of purging its faster to delete an entire family definition rather then deleting it's symbols first and then the
    definition.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param unused_type_getter:
        A function returning ids of unused symbols (family types) as a list.
        It requires as argument the current model document only.
    :type unused_type_getter: function (doc) -> list Autodesk.Revit.DB.ElementId
    :return: A list of Element Ids representing the family symbols and or family id's matching filter.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    unused_ids = []
    unused_family_ids = []
    # get all unused type Ids
    unused_type_ids = unused_type_getter(doc)
    # get family Elements belonging to those type ids
    families = get_symbols_from_type(doc, unused_type_ids)
    # check whether an entire family can be purged and if so remove their symbol(type) ids from
    # from unusedType ids list since we will be purging the family instead
    for key, value in families.items():
        if family_all_types_in_use(value, unused_type_ids):
            unused_family_ids.append(key)
            unused_type_ids = util.remove_items_from_list(unused_type_ids, value)
    # check whether entire families can be purged and if so add their ids to list to be returned
    if len(unused_family_ids) > 0:
        unused_ids = unused_family_ids + unused_type_ids
    else:
        unused_ids = unused_type_ids
    return unused_ids


def get_used_unused_type_ids(doc, type_id_getter, use_type=0, exclude_shared_fam=True):
    """
    Filters types obtained by past in type_id_getter method and depending on use_type past in returns either the used or unused symbols of a family
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param type_id_getter:
        A function returning ids of symbols (family types) as a list, requires as argument:
        the current model doc,
        ICollection of built in categories,
        bool: exclude shared families
    :type type_id_getter: function (doc, ICollection, bool) -> list[Autodesk.Revit.DB.ElementId]
    :param use_type: 0, no dependent elements (not used); 1: has dependent elements(is in use)
    :type use_type: int
    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # get all types elements available
    all_loadable_three_d_type_ids = type_id_getter(
        doc, CATEGORIES_LOADABLE_3D, exclude_shared_fam
    )
    all_loadable_tags_type_ids = type_id_getter(
        doc, CATEGORIES_LOADABLE_TAGS, exclude_shared_fam
    )
    all_type_ids = all_loadable_three_d_type_ids + all_loadable_tags_type_ids
    ids = []
    for type_id in all_type_ids:
        type = doc.GetElement(type_id)
        has_dependents = rPurgeUtils.has_dependent_elements(doc, type)
        if has_dependents == use_type:
            ids.append(type_id)
    return ids


def get_unused_family_types(doc, exclude_shared_fam=True):
    """
    Filters unused non shared family (symbols) type ids in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param exclude_shared_fam: Default is True (exclude any shared families from filter result)
    :type exclude_shared_fam: bool
    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = get_used_unused_type_ids(doc, get_family_symbols_ids, 0, exclude_shared_fam)
    return ids


def get_unused_non_shared_family_symbols_and_type_ids_to_purge(doc):
    """
    Filters unused, non shared and in place family (symbols) type ids in model which can be purged from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids_unused = get_unused_in_place_ids_for_purge(doc, get_unused_family_types)
    return ids_unused
