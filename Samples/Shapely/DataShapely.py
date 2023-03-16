'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions converting data retrieved from Revit into shapely geometry and processing it.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module requires python >3.9 due to dependencies:

- numpy
- shapely

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

import sys
import codecs


# path to shared packages on network drive (currently debug path only)
DUHAST_SOURCE_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'



LIBRARY = r'\\bvn\Data\studio\infotech\standards\Scripts\Revit Python\RBP\Lib\site-packages'

LIBRARY_LIB = r'C:\Users\jchristel\AppData\Roaming\Python\Python39\site-packages'

# set path to shared packages
sys.path += [DUHAST_SOURCE_PATH, LIBRARY_LIB]

# these packages are not available in an ironpython environment .e.g. Revit Python shell
# to avoid an exception stopping the entire package to load these are within a try catch block

import shapely.geometry as sg
import numpy as np

    
from duHast.Utilities import Result as res
from duHast.DataSamples import DataCeiling as dc
from duHast.DataSamples import DataRoom as dr
from duHast.DataSamples import DataReadFromFile as dReader

# --------------- generics shape creation ------------------

def GetTranslationMatrix(geoObject):
    '''
    Gets the rotation/ translation matrix from the geometry object

    :param geoObject: A data geometry object instance.
    :type geoObject: :class:`.DataGeometry`

    :return: A translation matrix.
    :rtype: numpy array
    '''

    transM = [] # translation only matrix
    # note numpy creates arrays by row!
    # need to append one more row since matrix dot multiplication rule:
    # number of columns in first matrix must match number of rows in second matrix (point later on)
    for vector in geoObject.rotationCoord:
        vector.append(0.0)
        transM.append(vector)
    rotationM = geoObject.translationCoord # rotation matrix
    # adding extra row here
    rotationM.append(1.0)
    transM.append(rotationM)
    # build combined rotation and translation matrix
    combinedM = np.array(transM)
    # transpose matrix (translation matrix in json file is stored by columns not by rows!)
    combinedM = np.transpose(combinedM)
    return combinedM

def get_outer_loop_as_shapely_points(geometry_object, translation_matrix):
    '''
    Returns the boundary loop of an object as list of shapely points. 
    
    Points are translated with passed in matrix.
    Any loops containing less then 3 points will be ignored. (Empty list will be returned)

    :param geometry_object: A data geometry object instance.
    :type geometry_object: :class:`.DataGeometry`
    :param translation_matrix: A translation matrix.
    :type translation_matrix: numpy array

    :return: List of shapely points defining a polygon. (Empty list will be returned if less then 3 points in loop.)
    :rtype: List[shapely.point]
    '''

    single_polygon_loop = []
    if(geometry_object.dataType == 'polygons'):
        for point_double in geometry_object.outerLoop:
            # need to add 1 to list for matrix multiplication
            # number of columns in first matrix (translation) must match number of rows in second matrix (point)
            translated_point = np.dot(translation_matrix,[point_double[0], point_double[1], point_double[2], 1.0])
            p = sg.Point(translated_point[0],translated_point[1],translated_point[2])
            single_polygon_loop.append(p)
    # ignore any poly loops with less then 3 sides (less then 3 points)
    if(len(single_polygon_loop) > 2):
        return single_polygon_loop
    else:
        return []

def get_inner_loops_as_shapely_points(geometry_object, translation_matrix):
    '''
    Returns the inner loops (holes) of an object as list of lists of shapely points. 
    
    Points are translated with passed in matrix.
    Any inner loops containing less then 3 points will be ignored. (Empty list will be returned)

    :param geoObject: A data geometry object instance.
    :type geoObject: :class:`.DataGeometry`
    :param translationM: A translation matrix.
    :type translationM: numpy array

    :return: List of lists of shapely points defining a polygon.
    :rtype: list [list[shapely.point]]
    '''
    
    shapely_points = []
    # get inner loops
    if(len(geometry_object.innerLoops) > 0):
        # there might be more then one inner loop
        for inner_loop in geometry_object.innerLoops:
            single_polygon_loop = []
            for point_double in inner_loop:
                # need to add 1 to list for matrix multiplication
                # number of columns in first matrix (translation) must match number of rows in second matrix (point)
                translated_point = np.dot(translation_matrix,[point_double[0], point_double[1], point_double[2], 1.0])
                p = sg.Point(translated_point[0],translated_point[1],translated_point[2])
                single_polygon_loop.append(p)
            # ignore any poly loops with less then 3 sides ( less then 3 points)
            if(len(single_polygon_loop)>2):
                shapely_points.append(single_polygon_loop)
    return shapely_points

def buildShapelyPolygon(shapeS):
    '''
    Creates shapely polygons from list of polygons past in.

    Assumptions is first polygon describes the boundary loop and any subsequent polygons are describing\
         holes within the boundary 

    :param shapeS: list of shapely polygons
    :type shapeS: list[shapely.polygon]

    :return: A shapely polygon.
    :rtype: shapely.polygon
    '''

    # convert to shapely
    poly = None
    # check if we got multiple polygons
    if(len(shapeS) == 1):
        # single exterior boundary ... no holes
        poly = sg.Polygon(shapeS[0])
    elif(len(shapeS) > 1):
        # got holes...
        # set up interior holes to be added to polygon
        # (remember exterior point order is ccw, holes cw else
        # holes may not appear as holes.)
        interiors = {}
        for i in range(1,len(shapeS)):
            interiors[i-1] = shapeS[i]
        i_p = {k: sg.Polygon(v) for k, v in interiors.items()}
        # create polygon with holes
        poly = sg.Polygon(shapeS[0], [poly.exterior.coords for poly in i_p.values() \
            if poly.within(sg.Polygon(shapeS[0])) is True])
    return poly

def get_shapely_polygons_from_data_instance(data_instance):
    '''
    Returns a list of of shapely polygons from data instances past in.
    
    Polygons may contain holes

    :param data_instance: _description_
    :type data_instance: A class with .geometry property returning a :class:`.DataGeometry` instance.
    
    :return: A list of shapely polygons.
    :rtype: list [shapely.polygon]
    '''

    all_polygons = []
    # loop over data geometry and convert into shapely polygons

    for geometry_object in data_instance.geometry:
        if(geometry_object.dataType == 'polygons'):
            translation_matrix = GetTranslationMatrix(geometry_object)
            shape_shapely = []
            outer_loop = get_outer_loop_as_shapely_points(geometry_object, translation_matrix)
            shape_shapely.append(outer_loop)
            if(len(outer_loop) > 0):
                inner_loops = get_inner_loops_as_shapely_points(geometry_object, translation_matrix)
                if(len(inner_loops) > 0):
                    for l in inner_loops:
                        shape_shapely.append(l)
            poly = buildShapelyPolygon(shape_shapely)
            all_polygons.append(poly)
        else:
            print('Not a polygon data instance!')
    return all_polygons

# --------------- end generics ------------------

#: List of available geometry (from revit to shapely ) converters
GEOMETRY_CONVERTER = {
    dr.DataRoom.dataType : get_shapely_polygons_from_data_instance,
    dc.DataCeiling.dataType: get_shapely_polygons_from_data_instance
}

def read_data(file_path):
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

# --------------- data processing ------------------

def writeReportData(fileName, header, data, writeType = 'w'):
    '''
    Method writing out report information to file.
 
    :param fileName: Fully qualified file path to data file.
    :type fileName: str
    :param header: List of column headers, provide empty list if not required!
    :type header: list[str]
    :param data: List of list of strings representing row data
    :type data: list[list[str]]
    :param writeType: 'w' new file, 'a' append to existing file., defaults to 'w'
    :type writeType: str, optional
    '''

    with codecs.open(fileName, writeType, encoding='utf-8') as f:
        # check if header is required
        if(len(header) > 0):
            print('\t'.join(header + ['\n']))
            f.write('\t'.join(header + ['\n']))
        # check if data is required
        if(len(data) > 0):
            for d in data:
                if (len(d) > 1):
                    to_file = ''
                    for v in d:
                        if(v==None):
                            v = 'null'
                        to_file = to_file + "\t{}".format(v)
                    # replace any NONE values to avoid issue with join command below
                    to_file = to_file.strip()
                    f.write(to_file + '\n')
                elif(len(d) == 1):
                    f.write(d[0] + '\n')
        f.close()


def build_dictionary_by_level_and_data_type(dataReader):
    '''
    Returns a dictionary where:

    - key: is the level name
    - values is a list of list of data objects
    -       first list room data objects
    -       second list ceilings data objects

    :param dataReader: A data reader class instance
    :type dataReader: :class:`.ReadDataFromFile`

    :return: A dictionary where key is the level name, value is a list of lists of data objects.
    :rtype: dic{str:[[:class:`.DataRoom],[:class:`.DataCeiling`]]}
    '''

    dic = {}
    for dObject in dataReader.data:
        if(dObject.level.levelName not in dic):
            roomsByLevel = dataReader.get_data_by_level_and_data_type(dObject.level.levelName, dr.DataRoom.dataType)
            ceilingsByLevel = dataReader.get_data_by_level_and_data_type(dObject.level.levelName, dc.DataCeiling.dataType)
            dic[dObject.level.levelName] = (roomsByLevel, ceilingsByLevel)
    return dic
        
def get_shapely_polygons_from_geo_object(geometry_objects, data_type):
    '''
    Converts polygon points from DataGeometry instances to shapely polygon instances and returns them as a dictionary where:

    - key is the geometry objects id
    - value is a list of shapely polygons

    :param geometry_objects: A list of instances of the the same type (i.e DataRoom)
    :type geometry_objects: list[data object]
    :param data_type: string human readable identifying the data type ( each Data... class has this as a static field: dr.DataRoom.dataType)
    :type data_type: str

    :return: A dictionary.
    :rtype: {int:[shapely.polygon]}
    '''

    multi_polygons = {}
    for i in range (len(geometry_objects)):
        multi_polygons[geometry_objects[i].instanceProperties.instanceId] = []
        poly = GEOMETRY_CONVERTER[data_type](geometry_objects[i])
        for p in poly:
            if(p != None):
                multi_polygons[geometry_objects[i].instanceProperties.instanceId].append(p)
    return multi_polygons

def SortMultipleDataRows(associatedDataRows, roomData):
    '''
    Collapses multiple ceilings of one type into one with multiple ids.

    Note: Works for ceilings only in the moment.
    This is to avoid situations where one type of ceiling is briefed in a room, but in the model, multiple instances of another type are modelled.
    In this case multiple type mismatches would be reported where we want only one type mismatch to be reported.
    Takes into account design set / design options and offset from level.

    :param associatedDataRows: List of list of strings representing ceiling data
    :type associatedDataRows: list[list[str]]
    :param roomData: List of string representing room data for a single room
    :type roomData: list[str]
    
    :return: List of list of strings representing room data
    :rtype: List of list [str]
    '''

    data = []
    if (len(associatedDataRows)>0):
        # build dictionary based on unique keys
        dic = {}
        for row in associatedDataRows:
            print(row)
            # Build unique key from type mark, offset from level, design set name, design option name, isPrimary
            key = '{}{}{}{}{}'.format(row[0],row[2],row[5],row[6],row[7])
            if(key in dic):
                dic[key].append(row)
            else:
                dic[key] = [row]
        # loop over dic and check whether some have multiple entries
        for entry in dic:
            if(len(dic[entry]) > 1):
                # get all ids
                ids = []
                for d in dic[entry]:
                    ids.append(d[4])
                # build rest of data but replace id field
                newDataRow = list(roomData)
                counter = 0
                for d in dic[entry][0]:
                    if(counter == 4):
                        newDataRow.append(','.join(ids))
                    else:
                        newDataRow.append(d)
                    counter = counter + 1
                data.append(newDataRow)
            else:
                newDataRow = list(roomData)
                for dList in dic[entry]:
                    for d in dList:
                        newDataRow.append(d)
                data.append(newDataRow)
    else:
        # just return the room data since no matching ceiling was found
        data.append(roomData)
    return data
      
def get_report_data(dic_object):
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
            dataRow = [
                room.instanceProperties.properties['drofus_room_function_number'], 
                room.instanceProperties.properties['Number'], 
                room.instanceProperties.properties['Name'], 
                room.level.levelName, 
                str(room.instanceProperties.instanceId),
                room.designSetAndOption.designSetName,
                room.designSetAndOption.designOptionName,
                str(room.designSetAndOption.isPrimary)
                ]
            associatedDataRows = []
            for associatedElement in room.associatedElements:
                # only add ceiling data for now
                if(associatedElement.dataType == dc.DataCeiling.dataType):
                    associatedDataRow = [
                        associatedElement.typeProperties.properties['Type Mark'], 
                        associatedElement.typeProperties.typeName, 
                        str(associatedElement.instanceProperties.properties['Height Offset From Level']), 
                        associatedElement.level.levelName, 
                        str(associatedElement.instanceProperties.instanceId),
                        associatedElement.designSetAndOption.designSetName,
                        associatedElement.designSetAndOption.designOptionName,
                        str(associatedElement.designSetAndOption.isPrimary)
                        ]
                    associatedDataRows.append(associatedDataRow)
            
            # get the data as list of strings. Collapse multiple ceilings of the same type into one entry
            # with multiple ids
            dataBySomething = SortMultipleDataRows(associatedDataRows, dataRow)
            for d in dataBySomething:
                data.append(d)
    return data

def GetCeilingsByRoom (data_source_path, outputFilePath):
    '''
    Reads geometry data from json formatted text file and does an intersection check between room and ceiling polygons.
    
    The result is written  to a report to provided path containing a row per room and ceiling within room.
    
    :param data_source_path: The fully qualified file path of json formatted data file containing room and ceiling data.
    :type data_source_path: str
    :param outputFilePath: The fully qualified file path of the output report. 
    :type outputFilePath: str

    :return: 
        Result class instance.
        result.status. True if:

        - all levels in file had ceilings and rooms.
        - report file was written successfully, 
        
        Otherwise False.
        
        - result.message will confirm report was written successfully.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain room name and number where exception occurred as well as ceiling id.
        - result.result will be empty
        
    :rtype: :class:`.Result`
    '''

    result = res.Result()
    data_reader = read_data(data_source_path)
    # check if read returned anything
    if(len(data_reader.data) > 0):
        # build dictionary of objects by level and object type
        data_objects = build_dictionary_by_level_and_data_type(data_reader)
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
                    room_polygons = get_shapely_polygons_from_geo_object(data_objects[level_name][0], dr.DataRoom.dataType)
                    ceilingPolygons = get_shapely_polygons_from_geo_object(data_objects[level_name][1], dc.DataCeiling.dataType)
                    polygons_by_type[dr.DataRoom.dataType] = room_polygons
                    polygons_by_type[dc.DataCeiling.dataType] = ceilingPolygons
                    # loop over rooms ids and find intersecting ceilings
                    for room_poly_id in polygons_by_type[dr.DataRoom.dataType]:
                        # check if valid room poly ( just in case that is a room in schedule only >> not placed in model , or unbound, or overlapping with other room)
                        if(len(room_polygons[room_poly_id]) > 0):
                            # loop over each room polygon per room...there should only be one...
                            for room_polygon in room_polygons[room_poly_id]:
                                # find overlapping ceiling polygons
                                intersections = {}
                                for ceiling_poly_id in polygons_by_type[dc.DataCeiling.dataType]:
                                    for ceiling_polygon in ceilingPolygons[ceiling_poly_id]:
                                        # add some exception handling here in case intersect check throws an error
                                        try:
                                            # debug
                                            match = False
                                            # check what exactly is happening
                                            if(ceiling_polygon.intersects(room_polygon)):
                                                # calculates percentage of overlapping ceiling area vs room area
                                                # anything less then 0.1 will be ignored...
                                                area_intersection_percentage_of_ceiling_vs_room = (ceiling_polygon.intersection(room_polygon).area/room_polygon.area)*100
                                                # check what percentage the overlap area is...if less then 0.1 percent ignore!
                                                if(area_intersection_percentage_of_ceiling_vs_room < 0.1):
                                                    # ceiling overlap area is to small...not in room
                                                    pass
                                                else:
                                                    # ceiling is within the room: add to room data object
                                                    # get the room object by its Revit ID
                                                    data_object_room =  list(filter(lambda x: (x.instanceProperties.instanceId == room_poly_id ) , data_objects[level_name][0]))[0]
                                                    # get the ceiling object by its Revit id
                                                    data_object_Ceiling =  list(filter(lambda x: (x.instanceProperties.instanceId == ceiling_poly_id ) , data_objects[level_name][1]))[0]
                                                    # add ceiling object to associated elements list of room object 
                                                    data_object_room.associatedElements.append(data_object_Ceiling)
                                        except Exception as e:
                                            # get the offending elements:
                                            data_object_room =  list(filter(lambda x: (x.instanceProperties.instanceId == room_poly_id ) , data_objects[level_name][0]))[0]
                                            data_object_Ceiling =  list(filter(lambda x: (x.instanceProperties.instanceId == ceiling_poly_id ) , data_objects[level_name][1]))[0]
                                            result.AppendMessage(
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
                else:
                    result.AppendMessage('No ceilings found for level: {}'.format(data_objects[level_name][0][0].level.levelName))
            else:
                result.AppendMessage('No rooms found for level: {}'.format(data_objects[level_name]))
        # write data out:
        # loop over dic
        # write single row for room and matching ceiling ( multiple rows for single room if multiple ceilings)
        reportData = get_report_data(data_objects)
        writeReportData(outputFilePath, [       # header
            'room function number', 
            'room number',
            'room name', 
            'room level name', 
            'room revit id', 
            'room design set name',
            'room design option name',
            'room design option is primary',
            'ceiling type mark', 
            'ceiling type name', 
            'offset from level', 
            'ceiling level name', 
            'ceiling revit id',
            'ceiling design set name',
            'ceiling design option name',
            'ceiling design option is primary'
            ], reportData)
        result.UpdateSep(True, 'Wrote data to file: ' + outputFilePath)
    else:
        result.UpdateSep(False, 'No data was fond in: ' + data_source_path)
    return result


GetCeilingsByRoom (r'C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\jsonFromFile.json', 
                   r'C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\roomsOut_.txt')