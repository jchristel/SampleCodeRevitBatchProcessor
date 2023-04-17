'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit rooms export to DATA class functions. 
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

from duHast.APISamples.Common import RevitDesignSetOptions as rDesignO, RevitElementParameterGetUtils as rParaGet, RevitPhases as rPhase
from duHast.DataSamples.Objects import DataRoom as dRoom
from duHast.DataSamples.Objects.Properties.Geometry import FromRevitConversion as rGeo
from duHast.APISamples.Rooms.RevitRooms import get_all_rooms
from duHast.APISamples.Rooms.Geometry.Geometry import get_2d_points_from_revit_room


def populate_data_room_object(doc, revitRoom):
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
    revitGeometryPointGroups = get_2d_points_from_revit_room(revitRoom)
    if(len(revitGeometryPointGroups) > 0):
        roomPointGroupsAsDoubles = []
        for roomPointGroupByPoly in revitGeometryPointGroups:
            dataGeometryConverted = rGeo.convert_xyz_in_data_geometry_polygons(doc, roomPointGroupByPoly)
            roomPointGroupsAsDoubles.append(dataGeometryConverted)
        dataR.geometryPolygon = roomPointGroupsAsDoubles
        # get design set data
        design_set_data = rDesignO.get_design_set_option_info(doc, revitRoom)
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
            rdb.StorageType.ElementId : rParaGet.getter_element_id_as_element_int, # needs to be an integer for JSON encoding
            str(None) : rParaGet.getter_none
        }
        dataR.instanceProperties.properties=rParaGet.get_all_parameters_and_values_wit_custom_getters(revitRoom, value_getter)

        # get the model name
        if(doc.IsDetached):
            dataR.revitModel.modelName = 'Detached Model'
        else:
            dataR.revitModel.modelName = doc.Title

        # get phase name
        dataR.phasing.phaseCreated = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(revitRoom, rdb.BuiltInParameter.ROOM_PHASE, rParaGet.get_parameter_value_as_element_id)
            ).encode('utf-8')
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


def get_all_room_data(doc):
    '''
    Returns a list of room data objects for each room in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of room data instances.
    :rtype: list of  :class:`.DataRoom`
    '''

    allRoomData = []
    rooms = get_all_rooms(doc)
    for room in rooms:
        rd = populate_data_room_object(doc, room)
        if(rd is not None):
            allRoomData.append(rd)
    return allRoomData