"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit fill patterns helper functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from Autodesk.Revit.DB import ElementId, FilteredElementCollector, FillPatternElement

from duHast.Revit.DetailItems.detail_items import (
    get_all_filled_region_type_ids_available,
)


def get_all_fill_pattern(doc):
    """
    Gets all fill pattern elements in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of all fill pattern elements.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return FilteredElementCollector(doc).OfClass(FillPatternElement)


def pattern_ids_by_name(doc):
    """
    Returns a dictionary where fill pattern name is key, values are all ids of line patterns with the exact same name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where fill pattern name is key, values are all ids of line patterns with the exact same name
    :rtype: dictionary(key str, value list of Autodesk.Revit.DB.ElementId)
    """

    pattern_dic = {}
    all_fill_pattern = get_all_fill_pattern(doc=doc)
    for fill_pattern in all_fill_pattern:
        pattern_name = fill_pattern.GetFillPattern().Name
        if pattern_name in pattern_dic:
            pattern_dic[pattern_name].append(fill_pattern.Id)
        else:
            pattern_dic[pattern_name] = [fill_pattern.Id]
    return pattern_dic


def get_used_pattern_ids_in_filled_region_types(doc):
    """
    Returns a list of all fill pattern ids used in filled region types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all fill pattern ids used in filled region types in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    fill_pattern_ids = []
    # get all filled region types in model
    filled_region_type_ids = get_all_filled_region_type_ids_available(doc)

    # return an empty list of no filled region types are available
    if len(filled_region_type_ids) == 0:
        return fill_pattern_ids

    for filled_region_type_id in filled_region_type_ids:
        # get the filled region type and its fill pattern ids for fore and background
        filled_region_type = doc.GetElement(filled_region_type_id)
        fore_ground_pattern_id = filled_region_type.ForegroundPatternId
        background_pattern_id = filled_region_type.BackgroundPatternId
        # check if already in unique list of fill pattern ids
        if (
            fore_ground_pattern_id not in fill_pattern_ids
            and fore_ground_pattern_id != ElementId.InvalidElementId
        ):
            fill_pattern_ids.append(fore_ground_pattern_id)
        if (
            background_pattern_id not in fill_pattern_ids
            and background_pattern_id != ElementId.InvalidElementId
        ):
            fill_pattern_ids.append(background_pattern_id)

    return fill_pattern_ids
