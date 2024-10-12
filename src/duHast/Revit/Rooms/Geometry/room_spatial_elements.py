"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit API utility functions for Room boundary loops and elements.
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

from Autodesk.Revit.DB import SpatialElementBoundaryOptions, CurveLoop, Wall, ModelLine


def get_room_segments(room):
    """
    Get a rooms boundary segments with the default spatial element boundary options.
    :param room: The room to get for
    :type room: Room
    :return: The boundary segments of the room
    :rtype: List[List[BoundarySegment]]
    """
    return room.GetBoundarySegments(SpatialElementBoundaryOptions())


def get_segment_host(rvt_doc, seg):
    """
    Get the element that the room boundary segment belongs to
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param seg: The boundary segment
    :type seg: BoundarySegment
    """

    # TODO: Add support for linked elements
    return rvt_doc.GetElement(seg.ElementId)


def get_curves_as_curve_loop(rm_crvs):
    """
    Get a list of curves as a CurveLoop object.
    :param rm_crvs: The curves to get for
    :type rm_crvs: List[Curve]
    :return: The curves as a CurveLoop object
    :rtype: CurveLoop
    """
    cl = CurveLoop()
    for crv in rm_crvs:
        cl.Append(crv)
    return cl


def get_spatial_element_filter(filter_only):
    """
    Checks if there is a Wall, ModelLine or both filter and returns a list
    of the types to filter for.
    :param filter_only: The host type to filter for
    :type filter_only: Wall, ModelLine or both in a list
    :return: A list of types to filter for
    :rtype: List[Type] or None
    """

    if filter_only:
        if isinstance(filter_only, list):
            return filter_only
        else:
            return [filter_only]
    else:
        return None


def get_all_segs_from_list(segments):
    """
    Get a list of curves that represents the boundary segments of a room.

    Optional parameter to filter the segments by the host type (wall or
    room separation line).
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :param filter_only: Optional: The host type to filter for
    :type filter_only: Wall, ModelLine or both in a list
    :return: A list of curves
    :rtype: List[Curve]
    """
    segs = []

    for closed_seg_set in segments:
        for seg in closed_seg_set:
            segs.append(seg)

    return segs


def get_segment_hosts(rvt_doc, segments, filter_only=None):
    """
    Gets the host element of a boundary segment. With option
    to filter by the host type
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :param filter_only: Optional: The host type to filter for
    :type filter_only: Wall, ModelLine or both in a list
    :return: A list of hosts
    :rtype: List[Element]
    """

    segment_list = get_all_segs_from_list(segments)

    type_filter_list = get_spatial_element_filter(filter_only)

    hosts = []

    for seg in segment_list:
        host = get_segment_host(rvt_doc, seg)
        if type_filter_list is None:
            hosts.append(host)
        else:
            if host.GetType() in type_filter_list:
                hosts.append(host)

    return hosts


def get_segments_as_curves(rvt_doc, segments, filter_only=None):
    """
    Get the curves that make up the boundary segments of a room.
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :param filter_only: Optional: The host type to filter for
    :type filter_only: Wall, ModelLine or both in a list
    :return: A list of curves
    :rtype: List[Curve]
    """
    segment_list = get_all_segs_from_list(segments)

    type_filter_list = get_spatial_element_filter(filter_only)

    curves = []

    for seg in segment_list:
        host = get_segment_host(rvt_doc, seg)
        if type_filter_list is None:
            curves.append(seg.GetCurve())
        else:
            if host.GetType() in type_filter_list:
                curves.append(seg.GetCurve())

    return curves


def get_only_wall_segments_as_curves(rvt_doc, segments):
    """
    Get the wall segments of a room as curves.
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :return: A list of curves
    :rtype: List[Curve]
    """
    return get_segments_as_curves(rvt_doc, segments, filter_only=Wall)


def get_only_rm_sep_lines_as_curves(rvt_doc, segments):
    """
    Get the room separation line segments of a room as curves.
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :return: A list of curves
    :rtype: List[Curve]
    """
    return get_segments_as_curves(rvt_doc, segments, filter_only=ModelLine)


def get_only_wall_segments_as_walls(rvt_doc, segments):
    """
    Get the wall segments of a room as walls.
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :return: A list of walls
    :rtype: List[Wall]
    """
    return get_segment_hosts(rvt_doc, segments, filter_only=Wall)


def get_only_rm_sep_lines_as_model_lines(rvt_doc, segments):
    """
    Get the room separation line segments of a room as model lines.
    :param rvt_doc: The Revit document
    :type rvt_doc: Document
    :param segments: The boundary segments of a room
    :type segments: List[List[BoundarySegment]]
    :return: A list of model lines
    :rtype: List[ModelLine]
    """
    return get_segment_hosts(rvt_doc, segments, filter_only=ModelLine)
