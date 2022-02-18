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
from collections import namedtuple
import codecs
import json

import shapely.geometry as sg
import shapely.ops as so

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection

import numpy as np

import Result as res
import DataCeiling as dc
import DataRoom as dr
import DataReadFromFile as dReader

# --------------- printing to matplotlib ------------------
# mat plot lib is used to visually check whether code generates the right shapely objects

colourKeysInterSectTypes = {
    'contains' : (0.2, 0.4, 1.0, 0.8), # royal blue (65,105,225) 
    'covers' : (0.5, 0.9, 0.5, 0.8), # light green (144,238,144)
    'toSmall' : (0.9, 0.5, 0.5, 0.8), # light coral (240,128,128)
    'crosses' : (0.1, 0.5, 0.1, 0.8), # forest green (34,139,34)
    'overlaps' : (1.0, 0.0, 0.5, 0.8), # deep pink (255,20,147)
    'intersects' : (0.0, 0.7, 1.0, 0.8),  # deep sky blue (0,191,255)
    'disjointed' : (0.1, 0.1, 0.1, 0.3) # light grey
}

def plot_polygon(ax, poly, **kwargs):
    '''
    # Plots a Polygon to pyplot `ax`
    https://stackoverflow.com/questions/55522395/how-do-i-plot-shapely-polygons-and-objects-using-matplotlib
    '''
    path = Path.make_compound_path(
        Path(np.asarray(poly.exterior.coords)[:, :2]),
        *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)
    
    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection

plotPolygonData = namedtuple('plotPolygonData', 'polygon foreGroundColour edgecolor, lineWeight')

# polygons                  named tuple with properties
#       polygon            shapely polygons
#       foreGroundColour    forground colour
def plotPolygons(polygons, fileName = ''):
    '''
    prints polygons
    '''
    multiPolygons = []
    for p in polygons:
        multiPolygons.append(p.polygon)
    new_shape = sg.MultiPolygon(multiPolygons)
    fig, axs = plt.subplots()
    axs.set_aspect('equal', 'datalim')

    counter = 0
    for geom in new_shape:
        plot_polygon(axs, geom, facecolor=polygons[counter].foreGroundColour, edgecolor=polygons[counter].edgecolor, linewidth=polygons[counter].lineWeight)
        counter += 1
    if(fileName == ''):
        plt.show()
    else:
        plt.savefig(fileName)

# --------------- generics shape creation ------------------

# geoObject         data geometry object
def GetTranslationMatrix(geoObject):
    '''
    returns the rotation/ translation matrix from the geometry object
    '''
    transM = [] # translation only matrix
    # note numpy creates arrays by row!
    # need to append one more row since matrix dot multiplication rule:
    # number of coulmns in first matrix must match number of rows in second matrix (point later on)
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

# geoObject         data geometry object
# translationM      numpy matrix
def GetOuterLoopAsShape(geoObject, translationM):
    '''
    returns the boundary loop of an object as list of shapely points. 
    Points are translated with passed in matrix 
    '''
    singlePolygonLoop = []
    if(geoObject.dataType == 'polygons'):
        for pdouble in geoObject.outerLoop:
            # need to add 1 to list for matric multiplication
            # number of columns in first matrix (translation) must match number of rows in second matrix (point)
            translatedPoint = np.dot(translationM,[pdouble[0], pdouble[1], pdouble[2], 1.0])
            p = sg.Point(translatedPoint[0],translatedPoint[1],translatedPoint[2])
            singlePolygonLoop.append(p)
    # ignore any poly loops with less then 3 sides (less then 3 points)
    if(len(singlePolygonLoop) > 2):
        return singlePolygonLoop
    else:
        return []

# geoObject         data geometry object
# translationM      numpy matrix
def GetInnerLoopsAsShape(geoObject, translationM):
    '''
    returns the inner loops (holes) of an object as list of shapely points. 
    Points are translated with passed in matrix 
    loops within inner loops will be ignored
    '''
    shapeS = []
    # get inner loops
    if(len(geoObject.innerLoops) > 0):
        # there might be more then one inner loop
        for innerLoop in geoObject.innerLoops:
            singlePolygonLoop = []
            for pdouble in innerLoop:
                # need to add 1 to list for matric multiplication
                # number of columns in first matrix (translation) must match number of rows in second matrix (point)
                translatedPoint = np.dot(translationM,[pdouble[0], pdouble[1], pdouble[2], 1.0])
                p = sg.Point(translatedPoint[0],translatedPoint[1],translatedPoint[2])
                singlePolygonLoop.append(p)
            # ignore any poly loops with less then 3 sides ( less then 3 points)
            if(len(singlePolygonLoop)>2):
                shapeS.append(singlePolygonLoop)
    return shapeS

# shapeS            list of polygons (each polygon is descirbed as a list of shapely points)
def buildShapelyPolygon(shapeS):
    '''
    creates shapely polygons from list of polygons passt in
    assumptions is first polygone describes the boundary loop 
    any subsequent polygons are describing holes within the boundary 
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

# dataInstance          a ceiling type data instance
def GetShapelyPolygonsFromDataInstance(dataInstance):
    '''
    returns a list of of shapely polygons from data instances passt in.
    Polygons may contain holes
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

# list of available geometry (from revit to shapely ) converters
geometryConverter_ = {
    dr.DataRoom.dataType : GetShapelyPolygonsFromDataInstance,
    dc.DataCeiling.dataType: GetShapelyPolygonsFromDataInstance
}

# filePath          path to json formatted text file to be read (one json entry per row)
def ReadData(filePath):
    '''
    reads text files into data objects within data reader class which is returned
    '''
    # read json file and convert into data objects
    dataReader = dReader.ReadDataFromFile(filePath)
    dataReader.load_Data()
    return dataReader

# --------------- data processing ------------------


# method writing out report information
# fileName:         fully qualified file path
# header:           list of column headers, provide empty list if not required!
# data:             list of list of strings representing row data
# writeType         w: new file, a: append to existing file...
def writeReportData(fileName, header, data, writeType = 'w'):
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
    dic = {}
    for dObject in dataReader.data:
        if(dObject.levelName not in dic):
            roomsByLevel = dataReader.get_data_by_level_and_dataType(dObject.levelName, dr.DataRoom.dataType)
            ceilingsByLevel = dataReader.get_data_by_level_and_dataType(dObject.levelName, dc.DataCeiling.dataType)
            dic[dObject.levelName] = (roomsByLevel, ceilingsByLevel)
    return dic




def GetShapelyPolygonsFromGeoObject(geoObjects, dataType):

    multiPolygons = {}
    for i in range (len(geoObjects)):
        multiPolygons[geoObjects[i].id] = []
        poly = geometryConverter_[dataType](geoObjects[i])
        for p in poly:
            if(p != None):
                multiPolygons[geoObjects[i].id].append(p)
    return multiPolygons

def GetReportData(dicObject):
    data = []
    for levelName in dicObject:
        for room in dicObject[levelName][0]:
            datarow = [room.functionNumber, room.number, room.name, room.levelName, str(room.id)]
            associatedDataRows = []
            for associatedElement in room.associatedElements:
                # only add ceiling data for now
                if(associatedElement.dataType == dc.DataCeiling.dataType):
                    associatedDataRow = [associatedElement.typeMark, associatedElement.typeName, str(associatedElement.offsetFromLevel), associatedElement.levelName, str(associatedElement.id)]
                    associatedDataRows.append(associatedDataRow)
            if(len(associatedDataRows) > 1):
                # multiple ceilings found
                for d in associatedDataRows:
                    newDataRow = list(datarow)
                    for entry in d:
                        newDataRow.append(entry)
                    data.append(newDataRow)
            else:
                # single ceiling entry found
                for d in associatedDataRows:
                    for entry in d:
                        datarow.append(entry)
                data.append(datarow)
    return data
        
            


# dataSourcePath            (fully qualified file path) of json formatted data file containing room and ceiling data
# outputFilePath            (fully qualified file path) of output report 
def GetCeilingsByRoom (dataSourcePath, outputFilePath):
    '''
    reads geo data from json formatted text file and does an intersection check between rooms and ceilings
    writes a report to provided path containing a row per room and ceiling within room
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
                                                # debug output
                                                if(areaIntersectionPercentageOfCeilingVsRoom < 0.1):
                                                    # ceiling is within the room
                                                    if('toSmall' in intersections):
                                                        intersections['toSmall'].append(cPolygon)
                                                    else:
                                                        intersections['toSmall']= [cPolygon]
                                                else:
                                                    # ceiling is within the room
                                                    if('intersects' in intersections):
                                                        intersections['intersects'].append(cPolygon)
                                                    else:
                                                        intersections['intersects']= [cPolygon]
                                                # debug
                                                match = True
                                            # debug
                                            if(match == False):
                                                if('disjointed' in intersections):
                                                    intersections['disjointed'].append(cPolygon)
                                                else:
                                                    intersections['disjointed']= [cPolygon]
                                        except Exception as e:
                                            # get the offending elements:
                                            dataObjectRoom =  list(filter(lambda x: (x.id == roomPolyId ) , dicObjects[levelName][0]))[0]
                                            dataObjectCeiling =  list(filter(lambda x: (x.id == ceilingPolyId ) , dicObjects[levelName][1]))[0]
                                            result.AppendMessage(
                                                'Exception: ' + str(e) + '\n' +
                                                'offending room: room name '+ dataObjectRoom.name+ ' room number '+ dataObjectRoom.number + ' room id ' + str(dataObjectRoom.id) + ' is valid polytgon ' + str(rPolygon.is_valid) +  '\n' +
                                                'offending ceiling id ' + str(dataObjectCeiling.id) + ' is valid polytgon ' + str(cPolygon.is_valid)
                                                )
                                # plot room and all intersectiong ceilings into a single diagram
                                
                                if(len(intersections) > 0):
                                    pass
                                    poly = []
                                    for i in intersections:
                                        for polyLoop in intersections[i]:
                                            poly.append(plotPolygonData(polyLoop,  colourKeysInterSectTypes[i], 'grey', 1))
                                    # add room last
                                    poly.append(plotPolygonData(rPolygon,'none', 'red', 2))
                                    try:
                                        #plotPolygons(poly, r'C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\SamplePLT' + '\\' + levelName + '_' + str(roomPolyId))
                                        #plotPolygons(poly)
                                        pass
                                    except Exception as e:
                                        print(e)
                else:
                    result.AppendMessage('No ceilings found for level: ' + str(dicObjects[levelName][0][0].levelName))
            else:
                result.AppendMessage('No rooms found for level: ' + str(dicObjects[levelName]))
        # write data out:
        # loop over dic
        # write single row for room and matching ceiling ( multiple rows for single rrom if multiple ceilings)
        reportData = GetReportData(dicObjects)
        writeReportData(outputFilePath, ['room function nuber', 'room number','room name', 'room level name', 'room revit id','eiling type mark', 'ceiling type name', 'offset from level', 'ceiling level name', 'ceiling revit id'], reportData)
        result.UpdateSep(True, 'Wrote data to file: ' + outputFilePath)
    else:
        result.UpdateSep(False, 'No data was fond in: ' + dataSourcePath)
    return result