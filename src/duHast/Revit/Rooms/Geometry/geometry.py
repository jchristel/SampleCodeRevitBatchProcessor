"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit rooms geometry extraction functions. 
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


from duHast.Utilities.Objects.result import Result
from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_polygon_2 as dGeometryPoly
from duHast.Revit.Common.Geometry.curve import splice_adjacent_lines

from Autodesk.Revit.DB import (
    CurveLoop,
    SpatialElementBoundaryOptions,
    SpatialElementBoundaryLocation,
    ElementId,
    Line,
    Arc,
)


def get_room_boundary_loops(
    revit_room,
    spatial_boundary_option=SpatialElementBoundaryOptions(),
    boundary_location=SpatialElementBoundaryLocation.Center,
):
    """
    Returns all boundary loops for a rooms. Default value set to the center
    boundary location.

    Note: Revit will return multiple BoundarySegments if the wall, which bounding a room, has another wall joining it on the opposing site of the room.

    :param revit_room: The room.
    :type revit_room: Autodesk.Revit.DB.Architecture.Room
    :return: List of boundary loops defining the room.
    :rtype: List of lists of Autodesk.Revit.DB.BoundarySegment
    """

    all_boundary_loops = []
    # set up spatial boundary option
    spatial_boundary_option.StoreFreeBoundaryFaces = True
    spatial_boundary_option.SpatialElementBoundaryLocation = boundary_location
    # get loops
    loops = revit_room.GetBoundarySegments(spatial_boundary_option)
    all_boundary_loops.append(loops)
    return all_boundary_loops


def get_points_from_room_boundaries(boundary_loops):
    """
    Returns a list of lists of points representing the room boundary loops.

    - List of Lists because a room can be made up of multiple loops (holes in rooms!)
    - First nested list represents the outer boundary of a room
    - All loops are implicitly closed ( last point is not the first point again!)

    :param boundary_loops: List of boundary loops defining the room.
    :type boundary_loops: List of lists of Autodesk.Revit.DB.BoundarySegment
    :return: A data geometry instance containing the points defining the boundary loop.
    :rtype: :class:`.DataPolygon`
    """

    loop_counter = 0
    has_inner_loops = False
    data_geo_polygon = dGeometryPoly.DataGeometryPolygon2()
    for boundary_loop in boundary_loops:
        for room_loop in boundary_loop:
            p = None  # segment start point
            loop_points = []
            for segment in room_loop:
                p = segment.GetCurve().GetEndPoint(0)
                loop_points.append(p)
            if loop_counter == 0:
                data_geo_polygon.outer_loop = loop_points
            else:
                data_geo_polygon.inner_loops.append(loop_points)
                has_inner_loops = True
            loop_counter += 1
    if not has_inner_loops:
        data_geo_polygon.inner_loops = []
    return data_geo_polygon


def get_2d_points_from_revit_room(revit_room):
    """
    Returns a list of dataGeometry object containing points representing the flattened(2D geometry) of a room in the model.
    List should only have one entry.

    :param revit_room: The room.
    :type revit_room: Autodesk.Revit.DB.Architecture.Room
    :return: A list of data geometry instance containing the points defining the boundary loop.
    :rtype: list of  :class:`.DataGeometry`
    """

    all_room_points = []
    boundary_loops = get_room_boundary_loops(revit_room)
    if len(boundary_loops) > 0:
        room_points = get_points_from_room_boundaries(boundary_loops)
        all_room_points.append(room_points)
    return all_room_points


def get_2d_points_from_all_revit_rooms(doc):
    """
    Returns a list of dataGeometry object containing points representing the flattened(2D geometry) of all the rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data geometry instances containing the points defining the boundary loop per room.
    :rtype: list of  :class:`.DataGeometry`
    """

    all_room_point_groups = []
    rooms = get_all_rooms(doc)
    for room in rooms:
        room_points = get_2d_points_from_revit_room(room)
        if len(room_points) > 0:
            all_room_point_groups.append(room_points)
    return all_room_point_groups


def convert_boundary_segments_to_curve_loops(boundary_loop):
    """
    Takes a boundary loop and checks whether consecutive segments host have the same id ( same wall  or room separation line. )
    If that is the case it will attempt to splice these segments and return them as one curve within the CurveLoop.

    :param boundary_loop: List of boundary segments defining the room.
    :type boundary_loop: List of Autodesk.Revit.DB.BoundarySegment

    :return:
        Result class instance.

        - conversion status (bool) returned in result.status. False if an exception occurred, otherwise True.
        - Result.message contain logs of segment conversion step by step.
        - Result.result will contain the created CurveLoop instance.

        On exception:

        - .status (bool) will be False.
        - .message will contain the exception message.

    :rtype: :class:`.Result`
    
    """
    return_value = Result()

    # set up curve loops for ceiling creation
    curve_loop = CurveLoop()

    # boundary loops are nested and contain the outlines of the room
   
    current_host_id = ElementId.InvalidElementId
    current_curve = None
    
    counter = 0
    # change boundary loop to curve loop
    for boundary_seg in boundary_loop:

        # get the host id
        host_id = boundary_seg.ElementId
        # get the curve from the boundary segment
        curve = boundary_seg.GetCurve()

        # logging
        return_value.append_message("current host id: {} and host id: {}".format(current_host_id, host_id))

        # only add the previous curve ... in case curves need to be combined!!
        # if curve host as changed, append the current curve to the curve loop
        if host_id != current_host_id:
            return_value.append_message("host id changed: {} to {}".format(current_host_id, host_id))
            return_value.append_message("current curve: {} {} ".format(curve.GetEndPoint(0), curve.GetEndPoint(1)))
            # set the current host id
            current_host_id = host_id
            # if there is a current curve, append it to the curve loop
            if current_curve is not None:
                curve_loop.Append(current_curve)
            # set the new curve to be the current curve
            current_curve = curve
        else:

            # check if line or arc...if neither do not combine
            if not isinstance(curve, Line) and not isinstance(curve, Arc):
                return_value.append_message("current curve is not a line or arc: {}".format(curve))
                # if the curve is not a line or arc, do not combine
                curve_loop.Append(curve)
                current_curve = curve

            # check if curve is a line
            elif isinstance(curve, Line):
                return_value.append_message ("current curve: {} {} and curve: {} {}".format(
                    current_curve.GetEndPoint(0),
                    current_curve.GetEndPoint(1),
                    curve.GetEndPoint(0),
                    curve.GetEndPoint(1))
                )
                return_value.append_message("current curve is a line: {}".format(current_curve))
                combined_curve = splice_adjacent_lines(current_curve, curve)

                if combined_curve is None:
                    return_value.append_message("failed to combine")
                    # if no match is found, do not combine
                    current_curve = curve
                    continue
                
                return_value.append_message("combined curve: {} {}".format(combined_curve.GetEndPoint(0),combined_curve.GetEndPoint(1)))
                # dont append the combined curve in case its more then 2 segments 
                current_curve = combined_curve
            # check if curve is an arc
            elif isinstance(curve, Arc):
                return_value.append_message("current curve is an arc: {}".format(curve))
                # dont combine just yet
                current_curve = curve
            # curve is neither a line nor an arc
            else:
                # if the curve is not a line or arc, do not combine
                return_value.append_message("current curve is not a line or arc: {}".format(curve))
                current_curve = curve
                
        counter = counter + 1
    
    # append the last curve to the curve loop
    if current_curve is not None:
        return_value.append_message("appending last curve: {} {}".format(current_curve.GetEndPoint(0), current_curve.GetEndPoint(1)))
        curve_loop.Append(current_curve)


    return_value.append_message("counter : {}".format(counter))
    return_value.result.append(curve_loop)
    return return_value