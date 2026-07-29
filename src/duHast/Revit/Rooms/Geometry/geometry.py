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
    Options,
    ViewDetailLevel,
    Solid,
    PlanarFace,
    XYZ,
)

# Tolerance for "do these two points coincide", in feet.
# Revit precision is ~1/16" (~0.0052 ft), so 1e-3 ft (~0.3 mm) is safely below
# a real join but well above floating noise.
GAP_TOL = 1e-3

def _pt_gap(a, b):
    """Planar distance between two XYZ points (ignores Z)."""
    dx = a.X - b.X
    dy = a.Y - b.Y
    return (dx * dx + dy * dy) ** 0.5


def _loop_has_gap(loop_segments):
    """True if any segment's END does not meet the NEXT segment's START
    (the dropped-segment quirk). Checks consecutive end->next-start, wrapping
    the last segment back to the first."""
    n = len(loop_segments)
    if n < 3:
        return True  # too few to be a valid polygon -> treat as broken
    for i in range(n):
        end_i = loop_segments[i].GetCurve().GetEndPoint(1)
        start_next = loop_segments[(i + 1) % n].GetCurve().GetEndPoint(0)
        if _pt_gap(end_i, start_next) > GAP_TOL:
            return True
    return False


def _polygon_area(pts):
    """Signed shoelace area of a list of XYZ points (uses X and Y only). Used
    only to pick the largest loop; sign/winding not relied upon elsewhere."""
    n = len(pts)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        s += p1.X * p2.Y - p2.X * p1.Y
    return s * 0.5


def _outer_loop_via_solid(room):
    """Fall back to the room's 3D solid: take the lowest horizontal planar
    face (the floor) and return its largest edge loop as the outer boundary.
    Inner loops (holes) are ignored. Returns a list of XYZ or None."""
    
    data_geo_polygon = dGeometryPoly.DataGeometryPolygon2()
    
    opt = Options()
    opt.ComputeReferences = False
    opt.DetailLevel = ViewDetailLevel.Fine

    geo = room.get_Geometry(opt)
    if geo is None:
        return data_geo_polygon

    solid = None
    for obj in geo:
        if isinstance(obj, Solid) and obj.Faces.Size > 0 and obj.Volume > 0:
            solid = obj
            break
    if solid is None:
        return data_geo_polygon

    # Lowest horizontal planar face = floor.
    floor = None
    lowest_z = None
    for f in solid.Faces:
        if isinstance(f, PlanarFace) and abs(f.FaceNormal.Z) > 0.99:
            z = f.Origin.Z
            if lowest_z is None or z < lowest_z:
                lowest_z = z
                floor = f
    if floor is None:
        return data_geo_polygon

    # The floor may have several edge loops (outer + holes). Pick the one with
    # the largest absolute area as the outer boundary; ignore the rest.
    best_pts = None
    best_area = -1.0
    for edge_loop in floor.EdgeLoops:
        pts = []
        for edge in edge_loop:
            p = edge.AsCurve().GetEndPoint(0)
            pts.append(p)
        a = abs(_polygon_area(pts))
        if a > best_area:
            best_area = a
            best_pts = pts
    
    # set the outer loop in the data geometry polygon
    if best_pts is not None:
        data_geo_polygon.outer_loop = best_pts
        
    return data_geo_polygon


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
    boundary_loops_all = get_room_boundary_loops(revit_room)
    boundary_loops = boundary_loops_all[0] if boundary_loops_all else []
    
    # debug: before get points

    # any internal loops will be ignored in this case
    if len(boundary_loops) == 0:
        # this can happen if the room is enclosed by linked model only. Revit api does not return any boundary segments in this case. We will try to get the outer loop via solid
        room_points = _outer_loop_via_solid(revit_room)
        all_room_points.append(room_points)
        # debug: after get points via solids after no boundary elements
        return all_room_points
    
    # Outer loop is the first; check it for gaps. If broken, go to fallback.
    # means that the room is not closed and we need to get the outer loop via solid
    if _loop_has_gap(boundary_loops[0]):
        room_points = _outer_loop_via_solid(revit_room)
        all_room_points.append(room_points)
        # debug: after get points via solids due to gaps
        return all_room_points

    # go standard route and get the points from the boundary segments
    room_points = get_points_from_room_boundaries(boundary_loops_all)
    all_room_points.append(room_points)

    # debug: after get points via segments

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
