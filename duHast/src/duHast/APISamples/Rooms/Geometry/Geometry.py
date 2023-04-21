'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit rooms geometry extraction functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Rooms.rooms import get_all_rooms
from duHast.DataSamples.Objects.Properties.Geometry import DataGeometryPolygon as dGeometryPoly


def get_room_boundary_loops(revit_room):
    '''
    Returns all boundary loops for a rooms.
    :param revit_room: The room.
    :type revit_room: Autodesk.Revit.DB.Architecture.Room
    :return: List of boundary loops defining the room.
    :rtype: List of lists of Autodesk.Revit.DB.BoundarySegment 
    '''

    all_boundary_loops = []
    # set up spatial boundary option
    spatial_boundary_option = rdb.SpatialElementBoundaryOptions()
    spatial_boundary_option.StoreFreeBoundaryFaces = True
    spatial_boundary_option.SpatialElementBoundaryLocation = rdb.SpatialElementBoundaryLocation.Center
    # get loops
    loops = revit_room.GetBoundarySegments(spatial_boundary_option)
    all_boundary_loops.append(loops)
    return all_boundary_loops


def get_points_from_room_boundaries(boundary_loops):
    '''
    Returns a list of lists of points representing the room boundary loops.

    - List of Lists because a room can be made up of multiple loops (holes in rooms!)
    - First nested list represents the outer boundary of a room
    - All loops are implicitly closed ( last point is not the first point again!)
    :param boundary_loops: List of boundary loops defining the room.
    :type boundary_loops: List of lists of Autodesk.Revit.DB.BoundarySegment 
    :return: A data geometry instance containing the points defining the boundary loop.
    :rtype: :class:`.DataGeometry`
    '''

    loop_counter = 0
    has_inner_loops = False
    data_geo_polygon = dGeometryPoly.DataPolygon()
    for boundary_loop in boundary_loops:
        for room_loop in boundary_loop:
            p = None # segment start point
            loop_points = []
            for segment in room_loop:
                p = segment.GetCurve().GetEndPoint(0)
                loop_points.append(p)
            if(loop_counter == 0):
                data_geo_polygon.outer_loop = loop_points
            else:
                data_geo_polygon.inner_loops.append(loop_points)
                has_inner_loops = True
            loop_counter += 1
    if (not has_inner_loops):
        data_geo_polygon.inner_loops = []
    return data_geo_polygon


def get_2d_points_from_revit_room(revit_room):
    '''
    Returns a list of dataGeometry object containing points representing the flattened(2D geometry) of a room in the model.
    List should only have one entry.
    :param revit_room: The room.
    :type revit_room: Autodesk.Revit.DB.Architecture.Room
    :return: A list of data geometry instance containing the points defining the boundary loop.
    :rtype: list of  :class:`.DataGeometry`
    '''

    all_room_points = []
    boundary_loops = get_room_boundary_loops(revit_room)
    if(len(boundary_loops) > 0):
        room_points = get_points_from_room_boundaries(boundary_loops)
        all_room_points.append(room_points)
    return all_room_points


def get_2d_points_from_all_revit_rooms(doc):
    '''
    Returns a list of dataGeometry object containing points representing the flattened(2D geometry) of all the rooms in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data geometry instances containing the points defining the boundary loop per room.
    :rtype: list of  :class:`.DataGeometry`
    '''

    all_room_point_groups = []
    rooms = get_all_rooms(doc)
    for room in rooms:
        room_points = get_2d_points_from_revit_room(room)
        if(len(room_points) > 0):
            all_room_point_groups.append(room_points)
    return all_room_point_groups