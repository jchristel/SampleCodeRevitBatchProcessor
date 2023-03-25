'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit rooms. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
import System

# import common library modules
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res
from duHast.APISamples import RevitGeometry as rGeo
from duHast.APISamples import RevitDesignSetOptions as rDesignO
from duHast.DataSamples import DataRoom as dRoom
from duHast.DataSamples import DataGeometry as dGeometry
from duHast.APISamples import RevitPhases as rPhase
from duHast.APISamples import RevitTransaction as rTran

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_ROOMS_HEADER = ['HOSTFILE','ID', 'NAME', 'GROUP TYPE', 'NUMBER OF INSTANCES']

# --------------------------------------------- utility functions ------------------

def GetAllRooms(doc):
    '''
    Gets a list of rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms).ToList()

def GetUnplacedRooms(doc):
    '''
    Gets a list of unplaced rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the unplaced rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    for r in coll:
        if(r.Location == None):
            unplaced.append(r)
    return unplaced

def GetNotEnclosedRooms(doc):
    '''
    Gets a list of not enclosed rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the unenclosed rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundaryOption = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundarySegments = r.GetBoundarySegments(boundaryOption)
        if(r.Area == 0.0 and r.Location != None and (boundarySegments == None or len(boundarySegments)) == 0):
            unplaced.append(r)
    return unplaced

def GetRedundantRooms(doc):
    '''
    Gets a list of redundant rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the redundant rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundaryOption = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundarySegments = r.GetBoundarySegments(boundaryOption)
        if(r.Area == 0.0 and(boundarySegments != None and len(boundarySegments) > 0)):
            unplaced.append(r)
    return unplaced

def MoveTagToRoom(doc, tagId):
    '''
    Moves a room tag to the associated rooms location point.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tagId: The element id of the tag to be moved to the room.
    :type tagId: Autodesk.Revit.DB.ElementId

    :return: 
        Result class instance.

        - Tag moving status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name and number of the room.
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain the name and number of the room and the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
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
    returnValue.Update(rTran.in_transaction(transaction, action))
    return returnValue

# -------------------------------- room geometry -------------------------------------------------------

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
    dataGeometry = dGeometry.DataGeometry()
    for boundaryLoop in boundaryLoops:
        for roomLoop in boundaryLoop:
            p = None # segment start point
            loopPoints = []
            for segment in roomLoop:
                p = segment.GetCurve().GetEndPoint(0)
                loopPoints.append(p)
            if(loopCounter == 0):
                dataGeometry.outerLoop = loopPoints
            else:
                dataGeometry.innerLoops.append(loopPoints)
                hasInnerLoops = True
            loopCounter += 1
    if (not hasInnerLoops):
        dataGeometry.innerLoops = []
    return dataGeometry

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

# -------------------------------- room data -------------------------------------------------------

def GetAllRoomData(doc):
    '''
    Returns a list of room data objects for each room in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of room data instances.
    :rtype: list of  :class:`.DataRoom`
    '''

    allRoomData = []
    rooms = GetAllRooms(doc)
    for room in rooms:
        rd = PopulateDataRoomObject(doc, room)
        if(rd is not None):
            allRoomData.append(rd)
    return allRoomData

def PopulateDataRoomObject(doc, revitRoom):
    '''
    Returns a custom room data objects populated with some data from the revit model room past in.

    data points:
    
    - room name, number, id
    - if exists: parameter value of SP_Room_Function_Number
    - level name and id (if not placed 'no level' and -1)
    - Design set and option

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitRoom: The room.
    :type revitRoom: Autodesk.Revit.DB.Architecture.Room

    :return: A room data instance.
    :rtype: :class:`.DataRoom`
    '''

    # set up data class object
    dataR = dRoom.DataRoom()
    # get room geometry (boundary points)
    revitGeometryPointGroups = Get2DPointsFromRevitRoom(revitRoom)
    if(len(revitGeometryPointGroups) > 0):
        roomPointGroupsAsDoubles = []
        for roomPointGroupByPoly in revitGeometryPointGroups:
            dataGeometryConverted = rGeo.ConvertXYZInDataGeometry(doc, roomPointGroupByPoly)
            roomPointGroupsAsDoubles.append(dataGeometryConverted)
        dataR.geometry = roomPointGroupsAsDoubles
        # get design set data
        design_set_data = rDesignO.GetDesignSetOptionInfo(doc, revitRoom)
        dataR.designSetAndOption.designOptionName = design_set_data['designOptionName']
        dataR.designSetAndOption.designSetName = design_set_data['designSetName']
        dataR.designSetAndOption.isPrimary = design_set_data['isPrimary']
        
        # get instance properties
        dataR.instanceProperties.instanceId=revitRoom.Id.IntegerValue
        # custom parameter value getters
        value_getter = {
            rdb.StorageType.Double : rParaGet.getter_double_as_double_converted_to_millimeter, 
            rdb.StorageType.Integer : rParaGet.getter_int_as_int, 
            rdb.StorageType.String : rParaGet.getter_string_as_UTF8_string, # encode ass utf 8 just in case
            rdb.StorageType.ElementId : rParaGet.getter_element_id_as_element_int # needs to be an integer for JSON encoding
        }
        dataR.instanceProperties.properties=rParaGet.get_all_parameters_and_values_wit_custom_getters(revitRoom, value_getter)
        
        # get the model name
        if(doc.IsDetached):
            dataR.revitModel.modelName = 'Detached Model'
        else:
            dataR.revitModel.modelName = doc.Title
        
        # get phase name
        dataR.phasing.phaseCreated = rPhase.GetPhaseNameById(doc, rParaGet.get_built_in_parameter_value(revitRoom, rdb.BuiltInParameter.ROOM_PHASE, rParaGet.get_parameter_value_as_element_id)).encode('utf-8')
        dataR.phasing.phaseDemolished = -1
        
        # get level data
        try:
            dataR.level.levelName = rdb.Element.Name.GetValue(revitRoom.Level).encode('utf-8')
            dataR.level.levelId = revitRoom.Level.Id.IntegerValue
        except:
            dataR.level.levelName = 'no level'
            dataR.level.levelId = -1
        return dataR
    
    else:
        return None