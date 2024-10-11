"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit room separation lines reports functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


from duHast.Revit.Common.design_set_options import get_design_set_option_info
from duHast.Revit.Warnings.warning_guids import (
    ROOM_LINE_OFF_AXIS,
    ROOM_AND_WALL_SEPARATION_LINE_OVERLAP,
    ROOM_SEPARATION_LINES_OVERLAP,
)
from duHast.Revit.Warnings.warnings import get_unique_warnings_elements_by_guid
from duHast.Revit.Common.Geometry.curve import get_curve_level
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames

from Autodesk.Revit.DB import ModelCurve


def _remove_wall_ids(doc, ids):
    """
    Filters list of ids and returns ids of room separtion lines (ModelCurve) only

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ids: List of element ids to filter
    :type ids: [Autodesk.Revit.DB.ElementId]

    :return: List of element ids
    :rtype: [Autodesk.Revit.DB.ElementId]
    """

    filtered_ids = []
    for id in ids:
        element = doc.GetElement(id)
        if isinstance(element, ModelCurve):
            filtered_ids.append(id)
    return filtered_ids


def _sort_room_lines_by_design_option(doc, room_line_ids):
    """
    Sorts room lines into a dictionary where key is the combination of the design set name and
    design option name and value is a list of room separation lines.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room_line_ids: list of room separation line ids
    :type room_line_ids: [Autodesk.Revit.DB.ElementId]

    :return: Dictionary containing room separation lines by design set / option name
    :rtype: {str:[Autodesk.Revit.DB.ModelCurve]}
    """

    room_lines_by_design_option = {}

    # loop over ids, get the line and its design set / option data
    for id in room_line_ids:
        element = doc.GetElement(id)
        data_dic = get_design_set_option_info(doc=doc, element=element)
        key = "{}_{}".format(
            data_dic[DesignSetPropertyNames.DESIGN_SET_NAME],
            data_dic[DesignSetPropertyNames.DESIGN_OPTION_NAME],
        )
        if key in room_lines_by_design_option:
            room_lines_by_design_option[key].append(element)
        else:
            room_lines_by_design_option[key] = [element]

    return room_lines_by_design_option


def _sort_room_lines_by_level(doc, room_lines_by_design_option):
    """
    Sorts the lines by level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room_lines_by_design_option: A dictioanry where key is the design set / option name and value is a list of room separation lines
    :type room_lines_by_design_option: {str:[Autodesk.Revit.DB.ModelCurve]}

    :return: A dictionary where key is a dictioanry where key is the design set / option name and value is another dictionary where key is the level name and value is a list of room separation lines
    :rtype: {str:{str:[Autodesk.Revit.DB.ModelCurve]}}
    """
    room_lines_by_design_option_and_level = {}

    # loop over dictionary and get the level information per line
    for design_set_option, lines in room_lines_by_design_option.items():
        curves_by_level_name = {}
        for line in lines:
            level = get_curve_level(doc=doc, curve=line)
            level_name = "Line is not associated to any level"
            if level:
                level_name = level.Name
            if level_name in curves_by_level_name:
                curves_by_level_name[level_name].append(line)
            else:
                curves_by_level_name[level_name] = [line]
        room_lines_by_design_option_and_level[design_set_option] = curves_by_level_name

    return room_lines_by_design_option_and_level


def room_lines_with_warnings_by_design_option_and_level(doc):
    """
    Reports all room separation line with warnings by design option and level they belong too

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: dictionary where key is the design option name and value is a nested dictionary where key is the level name and value is a list of room line ids
    :rtype: {str: Autodesk.Revit.DB.ElementId]}
    """

    room_line_instances_by_design_option_and_level = {}

    # get room lines with warnings
    line_ids_of_axis = get_unique_warnings_elements_by_guid(
        doc=doc, guid=ROOM_LINE_OFF_AXIS
    )
    line_ids_overlapping = get_unique_warnings_elements_by_guid(
        doc=doc, guid=ROOM_SEPARATION_LINES_OVERLAP
    )

    # this will include wall ids...
    line_ids_overlapping_walls = get_unique_warnings_elements_by_guid(
        doc=doc, guid=ROOM_AND_WALL_SEPARATION_LINE_OVERLAP
    )
    filtered_line_ides_overlapping_walls = _remove_wall_ids(
        doc=doc, ids=line_ids_overlapping_walls
    )

    # combine all ids
    all_line_ids_with_warnings = []
    if len(line_ids_of_axis) > 0:
        all_line_ids_with_warnings = all_line_ids_with_warnings + line_ids_of_axis
    if len(line_ids_overlapping) > 0:
        all_line_ids_with_warnings = all_line_ids_with_warnings + line_ids_overlapping
    if len(filtered_line_ides_overlapping_walls) > 0:
        all_line_ids_with_warnings = (
            all_line_ids_with_warnings + filtered_line_ides_overlapping_walls
        )

    # check if any warning is present
    if len(all_line_ids_with_warnings) == 0:
        return room_line_instances_by_design_option_and_level

    # sort offending elements by design option
    room_lines_by_design_option = _sort_room_lines_by_design_option(
        doc=doc, room_line_ids=all_line_ids_with_warnings
    )

    # sort offending elements by level
    room_line_instances_by_design_option_and_level = _sort_room_lines_by_level(
        doc=doc, room_lines_by_design_option=room_lines_by_design_option
    )

    return room_line_instances_by_design_option_and_level
