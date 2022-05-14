'''
This module contains a number of helper functions relating to Revit rooms. 
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

import clr
import System

# import common library modules
import RevitCommonAPI as com
import Result as res
import RevitGeometry as rGeo
import RevitDesignSetOptions as rDesignO
import DataRoom as dRoom
import DataGeometry as dGeometry

# import Autodesk
import Autodesk.Revit.DB as rdb

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_ROOMS_HEADER = ['HOSTFILE','ID', 'NAME', 'GROUP TYPE', 'NUMBER OF INSTANCES']

# --------------------------------------------- utility functions ------------------

# doc   current document
def GetAllRooms(doc):
    '''returns a list of rooms from the model'''
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms).ToList()


# doc   current document
def GetUnplacedRooms(doc):
    '''returns a list of unplaced rooms from the model'''
    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    for r in coll:
        if(r.Location == None):
            unplaced.append(r)
    return unplaced


# doc   current document
def GetNotEnclosedRooms(doc):
    '''returns a list of not enclosed rooms from the model'''
    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundaryOption = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundarySegments = r.GetBoundarySegments(boundaryOption)
        if(r.Area == 0.0 and r.Location != None and (boundarySegments == None or len(boundarySegments)) == 0):
            unplaced.append(r)
    return unplaced

# doc   current document
def GetRedundantRooms(doc):
    '''returns a list of redundants rooms from the model'''
    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundaryOption = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundarySegments = r.GetBoundarySegments(boundaryOption)
        if(r.Area == 0.0 and(boundarySegments != None and len(boundarySegments) > 0)):
            unplaced.append(r)
    return unplaced

# doc       current document
# tagId     the element Id of the tag to be moved
def MoveTagToRoom(doc, tagId):
    '''moves a tag to the room location point'''
    returnvalue = res.Result()
    rt = doc.GetElement(tagId)
    roomTagPoint = rt.Location.Point
    roomLocationPoint = rt.Room.Location.Point
    roomData = str(rt.Room.Number) + ' ' + str(rdb.Element.Name.GetValue(rt.Room))
    translation =  roomLocationPoint - roomTagPoint
    def action():
        actionReturnValue = res.Result()
        try:
            rt.Location.Move(translation)
            actionReturnValue.message = 'Moved tag to room ' + roomData
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed to move tag to room ' + roomData + ' with exception: ' + str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc, 'Moving room tag to room : ' + roomData)
    returnvalue.Update(com.InTransaction(transaction, action))
    return returnvalue

# -------------------------------- room geometry -------------------------------------------------------

# revitRoom         Revit Room element
def GetRoomBoundaryLoops(revitRoom):
    ''' 
    Returns all boundary loops for each rooms
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

# boundaryLoops     Revit Boundary loops
def GetPointsFromRoomBoundaries(boundaryLoops):
    '''
    Returns a list of lists of points representing the room boundary loops
    List of Lists because a room can be made up of multiple loops (holes in rooms!)
    First nested list represents the outer boundary of a room
    all loops are implicitly closed ( last point is not the first point again!)
    '''
    loopCounter = 0
    hasInnerLoops = False
    dgeo = dGeometry.DataGeometry()
    for bounadryLoop in boundaryLoops:
        for roomLoop in bounadryLoop:
            p = None # segment start point
            loopPoints = []
            for segment in roomLoop:
                p = segment.GetCurve().GetEndPoint(0)
                loopPoints.append(p)
            if(loopCounter == 0):
                dgeo.outerLoop = loopPoints
            else:
                dgeo.innerLoops.append(loopPoints)
                hasInnerLoops = True
            loopCounter += 1
    if (not hasInnerLoops):
        dgeo.innerLoops = []
    return dgeo

# doc       current model document
def Get2DPointsFromRevitRoom(revitRoom):
    '''
    Returns a list of lists of points representing the flattened(2D geometry) of each room in the model
    List of Lists because a rooms can have holes. First group of points represents external boundary of room. Any further list represents a hole in the room.
    '''
    allRoomPoints = []
    boundaryLoops = GetRoomBoundaryLoops(revitRoom)
    if(len(boundaryLoops) > 0):
        roomPoints = GetPointsFromRoomBoundaries(boundaryLoops)
        allRoomPoints.append(roomPoints)
    return allRoomPoints

# doc       current model document
def Get2DPointsFromAllRevitRoomsInModel(doc):
    '''
    Returns a list of lists of points representing the flattened(2D geometry) of each room in the model
    List of Lists because a rooms can have holes. First group of points represents external boundary of room. Any further list represents a hole in the room.
    '''
    allRoomPointGroups = []
    rooms = GetAllRooms(doc)
    for room in rooms:
        roomPoints = Get2DPointsFromRevitRoom(room)
        if(len(roomPoints) > 0):
            allRoomPointGroups.append(roomPoints)
    return allRoomPointGroups

# -------------------------------- room data -------------------------------------------------------

# doc       current model document
def GetAllRoomData(doc):
    '''
    returns a list of room data objects for each room in the model
    '''
    allRoomData = []
    rooms = GetAllRooms(doc)
    for room in rooms:
        rd = PopulateDataRoomObject(doc, room)
        if(rd is not None):
            allRoomData.append(rd)
    return allRoomData

# doc                   current revit document
# revitRoom             Revit Room element
def PopulateDataRoomObject(doc, revitRoom):
    '''
    returns a custom room data objects populated with some data from the revit model room passt in
    '''
    # set up data class object
    dataR = dRoom.DataRoom()
    # get room geometry (boundary points)
    revitGeometryPointGroups = Get2DPointsFromRevitRoom(revitRoom)
    if(len(revitGeometryPointGroups) > 0):
        roomPointGroupsAsDoubles = []
        for roomPointGroupByPoly in revitGeometryPointGroups:
            dgeoConverted = rGeo.ConvertXYZInDataGeometry(doc, roomPointGroupByPoly)
            roomPointGroupsAsDoubles.append(dgeoConverted)
        dataR.geometry = roomPointGroupsAsDoubles
        # get other data
        dataR.designSetAndOption = rDesignO.GetDesignSetOptionInfo(doc, revitRoom)
        dataR.id = revitRoom.Id.IntegerValue
        dataR.name = rdb.Element.Name.GetValue(revitRoom).encode('utf-8')
        dataR.number = revitRoom.Number.encode('utf-8')
        funcNumberValue = com.GetParameterValueByName(revitRoom, 'SP_Room_Function_Number')
        if(funcNumberValue != None):
            dataR.functionNumber = com.GetParameterValueByName(revitRoom, 'SP_Room_Function_Number').encode('utf-8')
        else:
            # use default instead
            pass
        try:
            dataR.levelName = rdb.Element.Name.GetValue(revitRoom.Level).encode('utf-8')
            dataR.levelId = revitRoom.Level.Id.IntegerValue
        except:
            dataR.levelName = 'no level'
            dataR.levelId = -1
        return dataR
    else:
        return None