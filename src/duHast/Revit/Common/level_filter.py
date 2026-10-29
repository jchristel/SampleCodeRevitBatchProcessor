"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to limit an export to some levels, before the (slow) conversion of each element.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The get_all_*_data export functions take an optional level_ids argument. When it is given only the
elements on those levels are converted; when it is None (the default) the export is as it always was.

A level is named by its Revit element id, as an integer (text holding an integer, and an ElementId, are
accepted). Which level an element is on is, for each kind of element, the level its exported data
reports: the element's own LevelId. A family instance whose level is worked out from its geometry
rather than assigned (see Family.Export.to_data_item) is filtered after that is worked out.
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Revit.Common.element_id import get_el_id_int

from Autodesk.Revit.DB import ElementId


def get_level_id_values(level_ids):
    """
    Normalises level ids to a set of integers.

    :param level_ids: Level ids as integers, text holding an integer, or Autodesk.Revit.DB.ElementId; None for no filter.
    :type level_ids: list or None

    :return: The set of integer ids, or None when there is no filter (None passed in). An empty list is a filter that
        lets nothing through, and is returned as an empty set.
    :rtype: set of int or None
    """

    if level_ids is None:
        return None
    values = set()
    for level_id in level_ids:
        if isinstance(level_id, ElementId):
            values.add(get_el_id_int(level_id))
        else:
            values.add(int(level_id))
    return values


def get_element_level_id_value(element):
    """
    The id of the level an element reports as its own (its LevelId), as an integer.

    :param element: A Revit element.
    :type element: Autodesk.Revit.DB.Element

    :return: The level id, or None when the element has no level (an invalid id).
    :rtype: int or None
    """

    try:
        level_id = element.LevelId
    except Exception:
        return None
    if level_id is None or level_id == ElementId.InvalidElementId:
        return None
    return get_el_id_int(level_id)


def is_on_levels(element, level_values):
    """
    Whether an element is on one of the levels.

    :param element: A Revit element.
    :type element: Autodesk.Revit.DB.Element
    :param level_values: The ids from get_level_id_values; None means no filter, so everything is on them.
    :type level_values: set of int or None

    :return: True if there is no filter or the element's level is in it.
    :rtype: bool
    """

    if level_values is None:
        return True
    return get_element_level_id_value(element) in level_values
