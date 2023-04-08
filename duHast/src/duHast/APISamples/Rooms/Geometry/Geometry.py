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

from duHast.APISamples.Rooms.RevitRooms import GetAllRooms
from duHast.DataSamples.Objects.Properties.Geometry import DataGeometryPolygon as dGeometryPoly


def GetRoomBoundaryLoops(revitRoom):
    '''
    Returns all boundary loops for a rooms.
    :param revitRoom: The room.
    :type revitRoom: Autodesk.Revit.DB.Architecture.Room
    :return: List of boundary loops defining the room.
    :rtype: List of lists of Autodesk.Revit.DB.BoundarySegment 
    '''

    allBoundaryLoops = []
    # set up spatial boundary option
    spatialBoundaryOption = rdb.SpatialElementBoundaryOptions()
    spatialBoundaryOption.StoreFreeBoundaryFaces = True
    spatialBoundaryOption.SpatialElementBoundaryLocation = rdb.SpatialElementBoundaryLocation.Center
    # get loops
    loops = revitRoom.GetBoundarySegments(spatialBoundaryOption)
    allBoundaryLoops.append(loops)
    return allBoundaryLoops


def GetPointsFromRoomBoundaries(boundaryLoops):
    '''
    Returns a list of lists of points representing the room boundary loops.
    - List of Lists because a room can be made up of multiple loops (holes in rooms!)
    - First nested list represents the outer boundary of a room
    - All loops are implicitly closed ( last point is not the first point again!)
    :param boundaryLoops: List of boundary loops defining the room.
    :type boundaryLoops: List of lists of Autodesk.Revit.DB.BoundarySegment 
    :return: A data geometry instance containing the points defining the boundary loop.
    :rtype: :class:`.DataGeometry`
    '''

    loopCounter = 0
    hasInnerLoops = False
    data_geo_polygon = dGeometryPoly.DataPolygon()
    for boundaryLoop in boundaryLoops:
        for roomLoop in boundaryLoop:
            p = None # segment start point
            loopPoints = []
            for segment in roomLoop:
                p = segment.GetCurve().GetEndPoint(0)
                loopPoints.append(p)
            if(loopCounter == 0):
                data_geo_polygon.outerLoop = loopPoints
            else:
                data_geo_polygon.innerLoops.append(loopPoints)
                hasInnerLoops = True
            loopCounter += 1
    if (not hasInnerLoops):
        data_geo_polygon.innerLoops = []
    return data_geo_polygon


def Get2DPointsFromRevitRoom(revitRoom):
    '''
    Returns a list of dataGeometry object containing points representing the flattened(2D geometry) of a room in the model.
    List should only have one entry.
    :param revitRoom: The room.
    :type revitRoom: Autodesk.Revit.DB.Architecture.Room
    :return: A list of data geometry instance containing the points defining the boundary loop.
    :rtype: list of  :class:`.DataGeometry`
    '''

    allRoomPoints = []
    boundaryLoops = GetRoomBoundaryLoops(revitRoom)
    if(len(boundaryLoops) > 0):
        roomPoints = GetPointsFromRoomBoundaries(boundaryLoops)
        allRoomPoints.append(roomPoints)
    return allRoomPoints


def Get2DPointsFromAllRevitRoomsInModel(doc):
    '''
    Returns a list of dataGeometry object containing points representing the flattened(2D geometry) of all the rooms in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data geometry instances containing the points defining the boundary loop per room.
    :rtype: list of  :class:`.DataGeometry`
    '''

    allRoomPointGroups = []
    rooms = GetAllRooms(doc)
    for room in rooms:
        roomPoints = Get2DPointsFromRevitRoom(room)
        if(len(roomPoints) > 0):
            allRoomPointGroups.append(roomPoints)
    return allRoomPointGroups