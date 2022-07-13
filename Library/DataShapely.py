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

import shapely.geometry as sg
import shapely.ops as so

import numpy as np

import Result as res
import DataCeiling as dc
import DataRoom as dr
import DataReadFromFile as dReader

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

def GetOuterLoopAsShape(geoObject, translationM):
    '''
    Returns the boundary loop of an object as list of shapely points. 
    
    Points are translated with passed in matrix.
    Any loops containing less then 3 points will be ignored. (Empty list will be returned)

    :param geoObject: A data geometry object instance.
    :type geoObject: :class:`.DataGeometry`
    :param translationM: A translation matrix.
    :type translationM: numpy array

    :return: List of shapely points defining a polygon. (Empty list will be returned if less then 3 points in loop.)
    :rtype: List[shapely.point]
    '''

    singlePolygonLoop = []
    if(geoObject.dataType == 'polygons'):
        for pointDouble in geoObject.outerLoop:
            # need to add 1 to list for matric multiplication
            # number of columns in first matrix (translation) must match number of rows in second matrix (point)
            translatedPoint = np.dot(translationM,[pointDouble[0], pointDouble[1], pointDouble[2], 1.0])
            p = sg.Point(translatedPoint[0],translatedPoint[1],translatedPoint[2])
            singlePolygonLoop.append(p)
    # ignore any poly loops with less then 3 sides (less then 3 points)
    if(len(singlePolygonLoop) > 2):
        return singlePolygonLoop
    else:
        return []

def GetInnerLoopsAsShape(geoObject, translationM):
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
    
    shapeS = []
    # get inner loops
    if(len(geoObject.innerLoops) > 0):
        # there might be more then one inner loop
        for innerLoop in geoObject.innerLoops:
            singlePolygonLoop = []
            for pointDouble in innerLoop:
                # need to add 1 to list for matrix multiplication
                # number of columns in first matrix (translation) must match number of rows in second matrix (point)
                translatedPoint = np.dot(translationM,[pointDouble[0], pointDouble[1], pointDouble[2], 1.0])
                p = sg.Point(translatedPoint[0],translatedPoint[1],translatedPoint[2])
                singlePolygonLoop.append(p)
            # ignore any poly loops with less then 3 sides ( less then 3 points)
            if(len(singlePolygonLoop)>2):
                shapeS.append(singlePolygonLoop)
    return shapeS

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

def GetShapelyPolygonsFromDataInstance(dataInstance):
    '''
    Returns a list of of shapely polygons from data instances past in.
    
    Polygons may contain holes

    :param dataInstance: _description_
    :type dataInstance: A class with .geometry property returning a :class:`.DataGeometry` instance.
    
    :return: A list of shapely polygons.
    :rtype: list [shapely.polygon]
    '''

    allPolygons = []
    # loop over data geometry and convert into shapely polygons

    for geoObject in dataInstance.geometry:
        if(geoObject.dataType == 'polygons'):
            translationM = GetTranslationMatrix(geoObject)
            shapeS = []
            outerLoop = GetOuterLoopAsShape(geoObject, translationM)
            shapeS.append(outerLoop)
            if(len(outerLoop) > 0):
                innerLoops = GetInnerLoopsAsShape(geoObject, translationM)
                if(len(innerLoops) > 0):
                    for l in innerLoops:
                        shapeS.append(l)
            poly = buildShapelyPolygon(shapeS)
            allPolygons.append(poly)
        else:
            print('Not a polygon data instance!')
    return allPolygons

# --------------- end generics ------------------

#: List of available geometry (from revit to shapely ) converters
geometryConverter_ = {
    dr.DataRoom.dataType : GetShapelyPolygonsFromDataInstance,
    dc.DataCeiling.dataType: GetShapelyPolygonsFromDataInstance
}

def ReadData(filePath):
    '''
    Reads text files into data objects within data reader class which is returned

    Data file to be json formatted. (one json entry per row)

    :param filePath: Fully qualified path to json formatted data file.
    :type filePath: str

    :return: A file data reader instance.
    :rtype: :class:`.ReadDataFromFile`
    '''
    # read json file and convert into data objects
    dataReader = dReader.ReadDataFromFile(filePath)
    dataReader.load_Data()
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
                    f.write('\t'.join(d + ['\n']))
                elif(len(d) == 1):
                    f.write(d[0] + '\n')
        f.close()


def BuildDictionaryByLevelAndDataType(dataReader):
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
        if(dObject.levelName not in dic):
            roomsByLevel = dataReader.get_data_by_level_and_dataType(dObject.levelName, dr.DataRoom.dataType)
            ceilingsByLevel = dataReader.get_data_by_level_and_dataType(dObject.levelName, dc.DataCeiling.dataType)
            dic[dObject.levelName] = (roomsByLevel, ceilingsByLevel)
    return dic
        
def GetShapelyPolygonsFromGeoObject(geoObjects, dataType):
    '''
    Converts polygon points from DataGeometry instances to shapely polygon instances and returns them as a dictionary where:

    - key is the geometry objects id
    - value is a list of shapely polygons

    :param geoObjects: A list of instances of the the same type (i.e DataRoom)
    :type geoObjects: list[data object]
    :param dataType: _string human readable identifying the data type ( each Data... class has this as a static field: dr.DataRoom.dataType)
    :type dataType: str

    :return: A dictionary.
    :rtype: {int:[shapely.polygon]}
    '''

    multiPolygons = {}
    for i in range (len(geoObjects)):
        multiPolygons[geoObjects[i].id] = []
        poly = geometryConverter_[dataType](geoObjects[i])
        for p in poly:
            if(p != None):
                multiPolygons[geoObjects[i].id].append(p)
    return multiPolygons

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
            # Build unique key from type mark, offset from level, design set name, design option name, isPrimary
            key = row[0] + row[2] + row[5] + row[6] + row[7]
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
      
def GetReportData(dicObject):
    '''
    Converts a dictionary of DataRoom objects by level into list of lists of data entries per room so it can be written to file.

    :param dicObject:  A dictionary where key is the level name and values is a list of DataRoom instances.
    :type dicObject: {str:[:class: `.DataRoom`]}

    :return: List of list of strings representing room data
    :rtype: list of list [str]
    '''

    data = []
    for levelName in dicObject:
        for room in dicObject[levelName][0]:
            dataRow = [
                room.functionNumber, 
                room.number, 
                room.name, 
                room.levelName, 
                str(room.id),
                room.designSetAndOption.designSetName,
                room.designSetAndOption.designOptionName,
                str(room.designSetAndOption.isPrimary)
                ]
            associatedDataRows = []
            for associatedElement in room.associatedElements:
                # only add ceiling data for now
                if(associatedElement.dataType == dc.DataCeiling.dataType):
                    associatedDataRow = [
                        associatedElement.typeMark, 
                        associatedElement.typeName, 
                        str(associatedElement.offsetFromLevel), 
                        associatedElement.levelName, 
                        str(associatedElement.id),
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

def GetCeilingsByRoom (dataSourcePath, outputFilePath):
    '''
    Reads geometry data from json formatted text file and does an intersection check between room and ceiling polygons.
    
    The result is written  to a report to provided path containing a row per room and ceiling within room.
    
    :param dataSourcePath: The fully qualified file path of json formatted data file containing room and ceiling data.
    :type dataSourcePath: str
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
    dataReader = ReadData(dataSourcePath)
    # check if read returned anything
    if(len(dataReader.data) > 0):
        # build dictionary of objects by level and object type
        dicObjects = BuildDictionaryByLevelAndDataType(dataReader)
        # key level name, value tuple ( rooms [index 0] and ceilings [index 1])
        # loop over dic and process each key (level):
        #       - check if rooms and ceilings
        #       - intersection check
        #       - update room object with ceiling match
        for levelName in dicObjects:
            # check rooms are on this level
            if(len(dicObjects[levelName][0]) > 0):
                # check ceilings are on this level
                if(len(dicObjects[levelName][1]) > 0):
                    polygonsByType = {}
                    # convert geometry data off all rooms and ceilings into dictionaries : key is Revit element id, values are shapely polygons
                    roomPolygons = GetShapelyPolygonsFromGeoObject(dicObjects[levelName][0], dr.DataRoom.dataType)
                    ceilingPolygons = GetShapelyPolygonsFromGeoObject(dicObjects[levelName][1], dc.DataCeiling.dataType)
                    polygonsByType[dr.DataRoom.dataType] = roomPolygons
                    polygonsByType[dc.DataCeiling.dataType] = ceilingPolygons
                    # loop over rooms ids
                    for roomPolyId in polygonsByType[dr.DataRoom.dataType]:
                        # check if valid room poly ( just in case that is a room in schedule only >> not placed in model , or unbound, or overlapping with other room)
                        if(len(roomPolygons[roomPolyId]) > 0):
                            # loop over each room polygon per room...there should only be one...
                            for rPolygon in roomPolygons[roomPolyId]:
                                # find overlapping ceiling polygons
                                intersections = {}
                                for ceilingPolyId in polygonsByType[dc.DataCeiling.dataType]:
                                    for cPolygon in ceilingPolygons[ceilingPolyId]:
                                        # add some exception handling here in case intersect check throws an error
                                        try:
                                            # debug
                                            match = False
                                            # check what exactly is happening
                                            if(cPolygon.intersects(rPolygon)):
                                                # calculates percentage of overlapping ceiling area vs room area
                                                # anything less then 0.1 will be ignored...
                                                areaIntersectionPercentageOfCeilingVsRoom = (cPolygon.intersection(rPolygon).area/rPolygon.area)*100
                                                # check what percentage the overlap area is...if less then 0.1 percent ignore!
                                                if(areaIntersectionPercentageOfCeilingVsRoom < 0.1):
                                                    # ceiling overlap area is to small...not in room
                                                    pass
                                                else:
                                                    # ceiling is within the room: add to room data object
                                                    # get the room object by its Revit ID
                                                    dataObjectRoom =  list(filter(lambda x: (x.id == roomPolyId ) , dicObjects[levelName][0]))[0]
                                                    # get the ceiling object by its Revit id
                                                    dataObjectCeiling =  list(filter(lambda x: (x.id == ceilingPolyId ) , dicObjects[levelName][1]))[0]
                                                    # add ceiling object to associated elements list of room object 
                                                    dataObjectRoom.associatedElements.append(dataObjectCeiling)
                                        except Exception as e:
                                            # get the offending elements:
                                            dataObjectRoom =  list(filter(lambda x: (x.id == roomPolyId ) , dicObjects[levelName][0]))[0]
                                            dataObjectCeiling =  list(filter(lambda x: (x.id == ceilingPolyId ) , dicObjects[levelName][1]))[0]
                                            result.AppendMessage(
                                                'Exception: ' + str(e) + '\n' +
                                                'offending room: room name '+ dataObjectRoom.name+ ' room number '+ dataObjectRoom.number + ' room id ' + str(dataObjectRoom.id) + ' is valid polygon ' + str(rPolygon.is_valid) +  '\n' +
                                                'offending ceiling id ' + str(dataObjectCeiling.id) + ' is valid polygon ' + str(cPolygon.is_valid)
                                                )
                else:
                    result.AppendMessage('No ceilings found for level: ' + str(dicObjects[levelName][0][0].levelName))
            else:
                result.AppendMessage('No rooms found for level: ' + str(dicObjects[levelName]))
        # write data out:
        # loop over dic
        # write single row for room and matching ceiling ( multiple rows for single room if multiple ceilings)
        reportData = GetReportData(dicObjects)
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
        result.UpdateSep(False, 'No data was fond in: ' + dataSourcePath)
    return result