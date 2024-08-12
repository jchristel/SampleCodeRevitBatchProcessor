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

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory


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
        print(" {} vs {} ".format(phase_Line_created_name, phase_created_name))
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
