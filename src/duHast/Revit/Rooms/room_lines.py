"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit API utility functions for Room separation lines.
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

from Autodesk.Revit.DB import BuiltInCategory, ElementId, FilteredElementCollector

from duHast.Revit.Common.phases import get_all_phases_in_order


def get_room_separation_lines(doc):
    """
    Get all room separation lines in the document.

    :param doc: The Revit document.
    :type doc: Document

    :return: A collector containing room separation lines.
    :rtype: FilteredElementCollector
    """

    return FilteredElementCollector(doc).OfCategory(
        BuiltInCategory.OST_RoomSeparationLines
    )


def get_room_separation_lines_by_level_name(doc, level_name):
    """
    Get all room separation lines in the document on a specific level by name.

    :param doc: The Revit document.
    :type doc: Document
    :param level_name: The name of the level.
    :type level_name: str

    :return: A list of room separation lines on the specified level.
    :rtype: list

    """

    room_separation_lines = []
    # get all room separation lines in the model
    col = get_room_separation_lines(doc)

    # loop over lines and filter them by level name
    for room_line in col:
        level_name_from_line = doc.GetElement(room_line.LevelId).Name
        if level_name_from_line == level_name:
            room_separation_lines.append(room_line)

    # return any matches
    return room_separation_lines


def get_room_separation_lines_by_level_names(doc):
    """
    Get all room separation lines in the document sorted by level name.

    :param doc: The Revit document.
    :type doc: Document

    :return: A dictionary containing room separation lines sorted by level name.
    :rtype: dict

    """

    room_separation_lines = {}

    # get all room separation lines in the model
    col = get_room_separation_lines(doc)

    # loop over lines and sort them by level name
    for room_line in col:
        level_name_from_line = doc.GetElement(room_line.LevelId).Name
        if level_name_from_line in room_separation_lines:
            room_separation_lines[level_name_from_line].append(room_line)
        else:
            room_separation_lines[level_name_from_line] = [room_line]

    # return any sorted lines
    return room_separation_lines


def sort_room_separation_line_by_phase_created(room_separation_lines):
    """
    Sorts the room separation lines by phase created id

    :param room_separation_lines: list of room separation lines
    :type room_separation_lines:list

    :return: A dictionary of room separation lines, where key is the phase created id, and values are the associated room separation lines
    :rtype: {ElementId:[ModelLine]}

    """
    sorted_lines = {}

    for line in room_separation_lines:
        if line.CreatedPhaseId in sorted_lines:
            sorted_lines[line.CreatedPhaseId].append(line)
        else:
            sorted_lines[line.CreatedPhaseId] = [line]

    return sorted_lines


def filter_room_separation_lines_by_phase_created(
    doc, room_separation_lines, phase_created_name
):
    """
    Filter room separation lines by phase created.

    :param doc: The Revit document.
    :type doc: Document
    :param phase_created_name: The phase name of the phase the room separation lines was created in.
    :type phase_created_name: str

    :return: A list of room separation lines filtered by phase created.
    :rtype: list

    """

    room_separation_lines_filtered = []

    # loop over lines and filter them by phase created
    for room_line in room_separation_lines:
        phase_Line_created_name = doc.GetElement(room_line.CreatedPhaseId).Name
        # print(" {} vs {} ".format(phase_Line_created_name, phase_created_name))
        if phase_Line_created_name == phase_created_name:
            room_separation_lines_filtered.append(room_line)

    # return any matches
    return room_separation_lines_filtered


def filter_room_separation_lines_by_phase_demolished(
    doc, room_separation_lines, phase_demolished_name
):
    """
    Filter room separation lines by phase created.

    :param doc: The Revit document.
    :type doc: Document
    :param phase_demolished_name: The phase name of the phase the room separation lines was created in.
    :type phase_demolished_name: str

    :return: A list of room separation lines filtered by phase created.
    :rtype: list

    """

    room_separation_lines_filtered = []

    # loop over lines and filter them by phase created
    for room_line in room_separation_lines:

        # get the demo phase of the room separation line
        phase_Line_demoed = doc.GetElement(room_line.DemolishedPhaseId)

        # check if both values are None (no demoed phase set)
        if phase_Line_demoed is None and phase_demolished_name == None:
            room_separation_lines_filtered.append(room_line)
        # check if one value is None (no demoed phase set but checking for demoed phase name)
        elif phase_Line_demoed is None and phase_demolished_name != None:
            continue
        # check if one value is None (a demoed phase is set but checking for no demoed phase)
        elif phase_Line_demoed is not None and phase_demolished_name == None:
            continue
        # check if both values are not None ( a demoed phase is set and checking for demoed phase name )
        else:
            phase_line_demolished_name = phase_Line_demoed.Name
            if phase_line_demolished_name == phase_demolished_name:
                room_separation_lines_filtered.append(room_line)

    # return any matches
    return room_separation_lines_filtered


def filter_room_separation_lines_by_phase_created_older_than_upper_bound_phase(
    doc, room_separation_lines, upper_bound_phase_id
):
    """
    Filter room separation lines by phase created. Phase created value must be a phase equal to or older than the upper bound phase id.
    If upper bound phase Id is and ElementId.InvalidElementId the list will be returned unchanged.

    :param doc: The Revit document.
    :type doc: Document
    :param room_separation_lines: A list of room separation lines
    :type room_separation_lines: []
    :param upper_bound_phase_id: the id of the phase to be used as upper bound
    :type upper_bound_phase_id: Autodesk.Revit.ElementId

    :return: A list of room separation lines filtered by phase created.
    :rtype: list
    """

    if isinstance(upper_bound_phase_id, ElementId) == False:
        raise TypeError(
            "upper_bound_phase_id needs to be of type ElementId. But is: {}".format(
                upper_bound_phase_id
            )
        )

    if upper_bound_phase_id == ElementId.InvalidElementId:
        return room_separation_lines

    # filtered lines
    lines_filtered = []

    # phases in model
    phases_ordered = get_all_phases_in_order(doc)

    # flip the phases_ordered list to get the index of the active view phase
    phase_id_index_by_phase_id = {}
    counter = 0
    for phase in phases_ordered:
        phase_id_index_by_phase_id[phase[0]] = counter
        counter += 1

    # index of upper bound
    upper_bound_phase_id_index = phase_id_index_by_phase_id[upper_bound_phase_id]

    # loop over lines and filter away any room separation lines newer then the upper bound phase id
    for line in room_separation_lines:
        line_phase_index = phase_id_index_by_phase_id[line.CreatedPhaseId]
        if line_phase_index <= upper_bound_phase_id_index:
            lines_filtered.append(line)

    return lines_filtered


def filter_room_separation_lines_by_level_id(room_separation_lines, level_id):
    """
    Filter room separation lines by level id its placed on.

    :param room_separation_lines: A list of room separation lines
    :type room_separation_lines: []
    :param level_id: The id of he level to be filtered by.
    :type level_id: Autodesk.Revit.ElementId

    :return: A list of room separation lines filtered by level placed on.
    :rtype: list
    """

    lines_filtered = []
    for room_line in room_separation_lines:
        if room_line.LevelId == level_id:
            lines_filtered.append(room_line)

    return lines_filtered
