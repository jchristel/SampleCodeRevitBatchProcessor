"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit railing balusters. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import common as com
from duHast.Revit.Railings.Utility.merge_lists import merge_into_unique_list
from duHast.Revit.Railings.railings import (
    get_all_railing_type_ids_by_class_and_category,
)


def get_balusters_used_in_pattern(b_pattern):
    """
    Gets list of unique baluster family ids used in a pattern only.
    :param b_pattern: A revit baluster pattern.
    :type b_pattern: Autodesk.Revit.DB.Architecture.BalusterPattern
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    for i in range(0, b_pattern.GetBalusterCount()):
        bal_info = b_pattern.GetBaluster(i)
        if (
            bal_info.BalusterFamilyId not in ids
            and bal_info.BalusterFamilyId != rdb.ElementId.InvalidElementId
        ):
            ids.append(bal_info.BalusterFamilyId)
    # add excess pattern baluster id
    if (
        b_pattern.ExcessLengthFillBalusterId not in ids
        and b_pattern.ExcessLengthFillBalusterId != rdb.ElementId.InvalidElementId
    ):
        ids.append(b_pattern.ExcessLengthFillBalusterId)
    return ids


def get_used_baluster_post_ids(b_post_pattern):
    """
    Gets list of unique baluster posts ids only.
    Includes:
    - CornerPost
    - EndPost
    - StartPost
    :param b_post_pattern: A revit post pattern.
    :type b_post_pattern: Autodesk.Revit.DB.Architecture.PostPattern
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    # get corner post
    if b_post_pattern.CornerPost.BalusterFamilyId != rdb.ElementId.InvalidElementId:
        ids.append(b_post_pattern.CornerPost.BalusterFamilyId)
    # get end post id
    if (
        b_post_pattern.EndPost.BalusterFamilyId != rdb.ElementId.InvalidElementId
        and b_post_pattern.EndPost.BalusterFamilyId not in ids
    ):
        ids.append(b_post_pattern.EndPost.BalusterFamilyId)
    # get start post id
    if (
        b_post_pattern.StartPost.BalusterFamilyId != rdb.ElementId.InvalidElementId
        and b_post_pattern.StartPost.BalusterFamilyId not in ids
    ):
        ids.append(b_post_pattern.StartPost.BalusterFamilyId)
    return ids


def get_used_baluster_per_tread(b_placement):
    """
    Gets the id of the baluster per stair tread.
    :param b_placement: A baluster placement element.
    :type b_placement: Autodesk.Revit.DB.Architecture.BalusterPlacement
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    # get baluster per tread
    if b_placement.BalusterPerTreadFamilyId != rdb.ElementId.InvalidElementId:
        ids.append(b_placement.BalusterPerTreadFamilyId)
    return ids


def get_all_baluster_symbols(doc):
    """
    Gets all baluster symbols (fam types) in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of baluster symbols (types).
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_StairsRailingBaluster)
        .WhereElementIsElementType()
    )
    return col


def get_all_baluster_symbols_ids(doc):
    """
    Gets all baluster symbol (fam type) ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = get_all_baluster_symbols(doc)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_baluster_types_from_railings(doc):
    """
    Gets a list of unique baluster symbol (fam type) ids used in railing types in the model.
    Incl:
    - baluster patterns
    - baluster posts
    - baluster per stair 
    There can be additional baluster symbols in the model. Those belong to loaded families which are not used in\
        any railing type definition.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    railing_type_ids = get_all_railing_type_ids_by_class_and_category(doc)
    for rt_id in railing_type_ids:
        el = doc.GetElement(rt_id)
        # put into try catch since some rail types have no balusters ...top rail
        try:
            baluster_placement = el.BalusterPlacement
            ids_pattern = get_balusters_used_in_pattern(
                baluster_placement.BalusterPattern
            )
            ids_posts = get_used_baluster_post_ids(baluster_placement.PostPattern)
            ids_per_tread = get_used_baluster_per_tread(baluster_placement)
            # build overall ids list
            ids = merge_into_unique_list(ids, ids_pattern)
            ids = merge_into_unique_list(ids, ids_posts)
            ids = merge_into_unique_list(ids, ids_per_tread)
        except:
            pass
    return ids
