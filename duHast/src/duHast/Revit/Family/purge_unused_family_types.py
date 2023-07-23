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
