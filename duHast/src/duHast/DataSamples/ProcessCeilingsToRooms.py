'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sample showing how to find which ceilings are in which rooms.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module requires python >3.9 due to dependencies:

    - numpy
    - shapely

This module:

    - collects ceiling and room data instances by level ( assume a ceiling is always modelled as the room it is in )
    - converts room and ceiling outlines to shapely polygons
    - test for intersection of all ceilings on a given level with all rooms on a given level
    - stores any intersections found ( does a check how much area is  intersecting...if to small its assumed its not an intended intersection)
    - reports all rooms and any associated ceiling(s) found

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

import codecs
import csv


from duHast.Utilities import Result as res
from duHast.DataSamples import DataCeiling as dc
from duHast.DataSamples import DataRoom as dr
from duHast.DataSamples import DataReadFromFile as dReader
from duHast.DataSamples import DataToShapely as dToS

# --------------- writing out data ------------------

def _read_data(file_path):
    '''
    Reads text files into data objects within data reader class which is returned

    Data file to be json formatted. (one json entry per row)

    :param filePath: Fully qualified path to json formatted data file.
    :type filePath: str

    :return: A file data reader instance.
    :rtype: :class:`.ReadDataFromFile`
    '''

    # read json file and convert into data objects
    dataReader = dReader.ReadDataFromFile(file_path)
    dataReader.load_data()
    return dataReader

# --------------- writing out data ------------------

def _write_report_data(file_name, header, data,):
    '''
    Method writing out report information to csv file.
 
    :param file_name: Fully qualified file path to data file.
    :type file_name: str
    :param header: List of column headers, provide empty list if not required!
    :type header: list[str]
    :param data: List of list of strings representing row data
    :type data: list[list[str]]

    :return: 
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain file name of file written.
        - result.result: empty list
        
        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result: will be an empty list

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    try:
        # open the file in the write mode
        with codecs.open(file_name, 'w', encoding='utf-8') as f:
         # create the csv writer
            writer = csv.writer(f)
            # check header
            if(len(header) > 0):
                writer.writerow(header)
            if(len(data) > 0):
                for d in data:
                    # write a row to the csv file
                    writer.writerow(d)
            f.close()
        return_value.UpdateSep(True, 'Successfully wrote data to: {}'.format(file_name))
    except  Exception as e:
        return_value.UpdateSep(False, 'Failed to write data to: {}'.format(file_name))
    return return_value

# --------------- data processing ------------------

def _build_dictionary_by_level_and_data_type(dataReader):
    '''
    Returns a dictionary where:

    - key: is the level name
    - values is a list of list of data objects
    -       first list room data objects
    -       second list ceilings data objects

    :param dataReader: A data reader class instance
    :type dataReader: :class:`.ReadDataFromFile`

    :return: A dictionary where key is the level name, value is a tuple of two lists: first one are rooms, second ones are ceiling data objects.
    :rtype: dic{str:[[:class:`.DataRoom],[:class:`.DataCeiling`]]}
    '''

    dic = {}
    for dObject in dataReader.data:
        if(dObject.level.levelName not in dic):
            roomsByLevel = dataReader.get_data_by_level_and_data_type(dObject.level.levelName, dr.DataRoom.dataType)
            ceilingsByLevel = dataReader.get_data_by_level_and_data_type(dObject.level.levelName, dc.DataCeiling.dataType)
            dic[dObject.level.levelName] = (roomsByLevel, ceilingsByLevel)
    return dic

def _get_property_values_as_list(properties, property_keys):
    '''
    _summary_

    :param properties: _description_
    :type properties: _type_
    :param property_keys: _description_
    :type property_keys: _type_

    :return: _description_
    :rtype: _type_
    '''

    values = []
    for property_key in property_keys:
        if(property_key in properties):
            values.append(str(properties[property_key]))
        else:
            values.append('null')
    return values

def _convert_object_data_into_report_data(dic_object, room_instance_property_keys, ceiling_type_property_keys, ceiling_instance_property_keys):
    '''
    Converts a dictionary of DataRoom objects by level into list of lists of data entries per room so it can be written to file.

    :param dic_object:  A dictionary where key is the level name and values is a list of DataRoom instances.
    :type dic_object: {str:[:class: `.DataRoom`]}

    :return: List of list of strings representing room data
    :rtype: list of list [str]
    '''

    data = []
    for levelName in dic_object:
        for room in dic_object[levelName][0]:
            # put fixed (always exported ) values first
            dataRow = [
                room.level.levelName,
                room.revitModel.modelName,
                str(room.instanceProperties.instanceId),
                room.designSetAndOption.designSetName,
                room.designSetAndOption.designOptionName,
                str(room.designSetAndOption.isPrimary)
            ]
            # get custom values
            dataRow = dataRow + _get_property_values_as_list(room.instanceProperties.properties, room_instance_property_keys)
            
            #data.append (dataRow)

            associatedDataRows = []
            for associatedElement in room.associatedElements:
                # only add ceiling data for now
                if(associatedElement.dataType == dc.DataCeiling.dataType):
                    associatedDataRow = [
                        associatedElement.level.levelName,
                        room.revitModel.modelName,
                        str(associatedElement.instanceProperties.instanceId),
                        associatedElement.designSetAndOption.designSetName,
                        associatedElement.designSetAndOption.designOptionName,
                        str(associatedElement.designSetAndOption.isPrimary)
                    ]
                    
                    associatedDataRow = associatedDataRow + _get_property_values_as_list(associatedElement.typeProperties.properties, ceiling_type_property_keys)
                    associatedDataRow = associatedDataRow + _get_property_values_as_list(associatedElement.instanceProperties.properties, ceiling_instance_property_keys)
                    associatedDataRows.append(associatedDataRow)
            
                    data.append( dataRow + associatedDataRow )
    return data

def _intersect_ceiling_vs_room(ceiling_poly_id, ceiling_polygon, room_poly_id, room_polygon, data_objects, level_name):
    '''
    Does an intersection check of a ceiling polygon with a room polygon. If there is an intersection, the ceiling object will be added to the associated elements list of the room object.

    Note:

    - To avoid false positives: only ceiling which overlap a room by an area greater then 0.1 percent of the ceiling area will be considered as intersecting.
    - Manipulates the past in data_objects by reference!

    :param ceiling_poly_id: The Revit ceiling element id.
    :type ceiling_poly_id: int
    :param ceiling_polygon: A polygon representing the ceiling element.
    :type ceiling_polygon: shapely.polygon
    :param  room_poly_id: The Revit room element id.
    :type  room_poly_id: int
    :param room_polygon: A polygon representing the room element.
    :type room_polygon: shapely.polygon
    :param data_objects: A dictionary where key is the level name, value is a tuple of two lists: first one are rooms, second ones are ceiling data objects.
    :type data_objects: [str:([:class:`.DataRoom`],[:class:`.DataCeiling`])]
    :type  level_name: The level name where room and ceiling are on.
    :param room_polygon: str

    :return: 
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result: empty list
        
        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # add some exception handling here in case intersect check throws an error
    try:
        # check what exactly is happening
        if(ceiling_polygon.intersects(room_polygon)):
            # calculates percentage of overlapping ceiling area vs room area
            # anything less then 0.1 will be ignored...
            area_intersection_percentage_of_ceiling_vs_room = (ceiling_polygon.intersection(room_polygon).area/room_polygon.area)*100
            # check what percentage the overlap area is...if less then 0.1 percent ignore!
            if(area_intersection_percentage_of_ceiling_vs_room < 0.1):
                # ceiling overlap area is to small...not in room
                return_value.AppendMessage('Ceiling {} has an overlap of {} % with  room {}. Ignored!'.format(ceiling_poly_id, area_intersection_percentage_of_ceiling_vs_room, room_poly_id, ))
            else:
                # ceiling is within the room: add to room data object
                # get the room object by its Revit ID
                data_object_room =  list(filter(lambda x: (x.instanceProperties.instanceId == room_poly_id ) , data_objects[level_name][0]))[0]
                # get the ceiling object by its Revit id
                data_object_Ceiling =  list(filter(lambda x: (x.instanceProperties.instanceId == ceiling_poly_id ) , data_objects[level_name][1]))[0]
                # add ceiling object to associated elements list of room object 
                data_object_room.associatedElements.append(data_object_Ceiling)
                return_value.AppendMessage('Added ceiling {} to room {}'.format(room_poly_id, ceiling_poly_id))
    except Exception as e:
        # get the offending elements:
        data_object_room =  list(filter(lambda x: (x.instanceProperties.instanceId == room_poly_id ) , data_objects[level_name][0]))[0]
        data_object_Ceiling =  list(filter(lambda x: (x.instanceProperties.instanceId == ceiling_poly_id ) , data_objects[level_name][1]))[0]
        return_value.AppendMessage(
            'Exception: {} \n' +
            'offending room: room name: {} , room number: {} , room id: {} , is valid polygon: {}\n' +
            'offending ceiling id: {} , is valid polygon: {}').format(
                e.message, 
                data_object_room.instanceProperties.properties['Name'],
                data_object_room.instanceProperties.properties['Number'],
                data_object_room.instanceProperties.instanceId,
                room_polygon.is_valid,
                data_object_Ceiling.instanceProperties.instanceId,
                ceiling_polygon.is_valid
                )
    return return_value

# --------------- main functions ------------------

def write_data_to_file(data, output_file_path, room_instance_property_keys= ['Number', 'Name'], ceiling_type_property_keys = ['Type Mark'], ceiling_instance_property_keys =['Height Offset From Level'] ):
    '''
    Writes Room data to file. 

    Note:

    - Room data consists of fixed (always reported) instance properties and custom instance properties defined in room_instance_property_keys
    - Ceiling data consists of fixed (always reported) instance properties, custom type properties defined in ceiling_type_property_keys and custom instance properties defined in ceiling_instance_property_keys
    - the report contains a row per associated element per room ( if 2 ceilings are in a room, the report will contain 2 rows)

    :param data: A dictionary where key is the level name and values is a list of DataRoom instances.
    :type data: {str:[:class: `.DataRoom`]}
    :param output_file_path: Fully qualified file path to output report file.
    :type output_file_path: str
    :param room_instance_property_keys: Names of room instance properties to be reported, defaults to ['Number', 'Name']
    :type room_instance_property_keys: list, optional
    :param ceiling_type_property_keys: Names of ceiling type properties to be reported, defaults to ['Type Mark']
    :type ceiling_type_property_keys: list, optional
    :param ceiling_instance_property_keys: Names of ceiling instance properties to be reported, defaults to ['Height Offset From Level']
    :type ceiling_instance_property_keys: list, optional

    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the processing messages.
        - result.result will be an empty list
        
        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    try:
        converted_data =  _convert_object_data_into_report_data(
            data,
            room_instance_property_keys,
            ceiling_type_property_keys,
            ceiling_instance_property_keys)
    
        # create header for report file
        # rooms always written values first
        data_header = ['room level name', 'room model name', 'room revit id','room design set name','room design option name', 'room design option is primary']
        # rooms custom data next
        data_header = data_header + room_instance_property_keys
        # ceilings always written values first
        data_header = data_header + ['ceiling level name', 'ceiling model name','ceiling revit id','ceiling design set name','ceiling design option name', 'ceiling design option is primary']
        # ceilings custom data next
        data_header = data_header + ceiling_type_property_keys + ceiling_instance_property_keys
        # write data to file
        return_value.Update(_write_report_data(output_file_path, data_header, converted_data))

    except Exception as e:
        return_value.UpdateSep(False, 'Failed to write report with exception {}'.format(e))
    return return_value

def get_ceilings_by_room(data_source_path):
    '''
    Reads Revit data from file and runs an intersection check of each ceiling on a level with each room on the same level.

    Note:
    DataRoom instance will contain any ceilings in that room in associated elements property.

    :param data_source_path: Fully qualified file path to json formatted file containing DataRoom and DataCeiling objects.
    :type data_source_path: str

    :return: 
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result A dictionary where key is the level name, value is a tuple of two lists: first one are rooms, second ones are ceiling data objects.
        
        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # read exported ceiling and room data from file
    data_reader = _read_data(data_source_path)
    # check if read returned anything
    if(len(data_reader.data) > 0):
        # build dictionary of objects by level and object type
        data_objects = _build_dictionary_by_level_and_data_type(data_reader)
        # key level name, value tuple ( rooms [index 0] and ceilings [index 1])
        # loop over dic and process each key (level):
        #       - check if rooms and ceilings
        #       - intersection check
        #       - update room object with ceiling match
        for level_name in data_objects:
            # check rooms are on this level
            if(len(data_objects[level_name][0]) > 0):
                # check ceilings are on this level
                if(len(data_objects[level_name][1]) > 0):
                    polygons_by_type = {}
                    # convert geometry data off all rooms and ceilings into dictionaries : key is Revit element id, values are shapely polygons
                    room_polygons = dToS.get_shapely_polygons_from_geo_object(data_objects[level_name][0], dr.DataRoom.dataType)
                    ceiling_polygons = dToS.get_shapely_polygons_from_geo_object(data_objects[level_name][1], dc.DataCeiling.dataType)
                    polygons_by_type[dr.DataRoom.dataType] = room_polygons
                    polygons_by_type[dc.DataCeiling.dataType] = ceiling_polygons
                    # loop over rooms ids and find intersecting ceilings
                    for room_poly_id in polygons_by_type[dr.DataRoom.dataType]:
                        # check if valid room poly ( just in case that is a room in schedule only >> not placed in model , or unbound, or overlapping with other room)
                        if(len(room_polygons[room_poly_id]) > 0):
                            # loop over each room polygon per room...there should only be one...
                            for room_polygon in room_polygons[room_poly_id]:
                                # find overlapping ceiling polygons
                                for ceiling_poly_id in polygons_by_type[dc.DataCeiling.dataType]:
                                    for ceiling_polygon in ceiling_polygons[ceiling_poly_id]:
                                        return_value.Update(   
                                            _intersect_ceiling_vs_room(
                                                ceiling_poly_id, 
                                                ceiling_polygon, 
                                                room_poly_id, 
                                                room_polygon, 
                                                data_objects, 
                                                level_name
                                                )
                                            )
                        else:
                            return_value.AppendMessage('Room with id {} has no valid room poly lines.'.format(room_poly_id))
                else:
                    return_value.AppendMessage('No ceilings found for level: {}'.format(data_objects[level_name][0][0].level.levelName))
            else:
                return_value.AppendMessage('No rooms found for level: {}'.format(data_objects[level_name]))
        return_value.result = data_objects
    else:
        return_value.UpdateSep(False, 'File: {} did not contain any valid data.'.format(data_source_path))
    return return_value