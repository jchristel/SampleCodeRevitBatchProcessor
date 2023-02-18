'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit geometry extraction helper functions
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

from collections import namedtuple
import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

import Autodesk.Revit.DB as rdb

from duHast.DataSamples import DataGeometry as dGeometry

# ---------------------------- debug ----------------------------
def GetPointAsString (point):
    '''
    Returns Revit point as a string.

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: String in format 'X:Y:Z'
    :rtype: str
    '''

    return str(point.X) + ' : ' + str(point.Y) + ' : ' + str(point.Z)
    
def GetEdgeAsString(edge):
    '''
    Returns a revit edge as a string.

    :param edge: A revit edge.
    :type edge: Autodesk.Revit.DB.Edge 

    :return: String where each row represents a point on the edge. 
    :rtype: str
    '''

    returnValue = ''
    for p in edge.Tessellate():
        returnValue = returnValue + '\n' + GetPointAsString (p)
    return returnValue

# ---------------------------- math utility ----------------------------

def IsClose(a, b, rel_tol=1e-09, abs_tol=0.0):
    '''
    Compares two floats with a tolerance. Returns True if they are close enough, otherwise False
    
    refer to: https://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python

    :param a: A float
    :type a: float
    :param b: A float
    :type b: float
    :param rel_tol: Relative tolerance used to compare the two floats, defaults to 1e-09
    :type rel_tol: float, optional
    :param abs_tol: Absolute tolerance used to compare the two floats, defaults to 0.0
    :type abs_tol: float, optional

    :return: Returns True if they are close enough to be considered equal, otherwise False
    :rtype: bool
    '''

    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def ArePointsIdentical(p1, p2):
    '''
    Compares the X,Y,Z values of two revit point and returns True if they are the same, otherwise False
    
    :param p1: A revit point.
    :type p1: Autodesk.Revit.DB.XYZ
    :param p2: A revit point.
    :type p2: Autodesk.Revit.DB.XYZ

    :return: True if they are the same, otherwise False.
    :rtype: bool
    '''

    if (IsClose(p1.X,p2.X) and IsClose(p1.Y, p2.Y) and IsClose(p1.Z,p2.Z)):
        return True
    else:
        return False

def CheckDuplicatePoint(points, point):
    '''
    Checks whether a collection of points contains another given point and returns True if that is the case.

    :param points: List of revit points
    :type points: list Autodesk.Revit.DB.XYZ
    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: True if point is in collection, otherwise False.
    :rtype: bool
    '''

    for p1 in points:
        if(ArePointsIdentical(p1, point)):
            return True
    return False

def GetPointAsDoubles(point):
    '''
    Converts a revit XYZ to a list of doubles in order x,y,z.

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: List of doubles in order of x,y,z
    :rtype: list double
    '''

    return [point.X, point.Y, point.Z]

def FlattenXYZPoint(point):
    '''
    Flattens a XYZ point to a UV by omitting the Z value of the XYZ.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: A 2D point (UV)
    :rtype:  Autodesk.Revit.DB.UV
    '''

    return rdb.UV( point.X, point.Y )

def FlattenXYZPointList(polygon):
    '''
    Flattens a list of XYZ points to a list of UV points by omitting the Z value of each XYZ.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param polygon: list of XYZ points
    :type polygon: list Autodesk.Revit.DB.XYZ
    
    :return: list of UV points
    :rtype: list Autodesk.Revit.DB.UV
    '''

    z = polygon[0].Z;
    a = []
    for p in polygon :
        if(IsClose(p.Z, z)):
            #print("expected horizontal polygon" )
            pass
        a.append( FlattenXYZPoint( p ) )
    return a

def FlattenXYZPointListOfLists(  polygons ):
    '''
    Flattens a list lists of XYZ points to a list of lists of UV points by omitting the Z value of each XYZ.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param polygon: list of lists of XYZ points
    :type polygon: list [list Autodesk.Revit.DB.XYZ]
    
    :return: list of lists of UV points
    :rtype: list [list Autodesk.Revit.DB.UV]
    '''
    
    z = polygons[0][0].Z
    a = []
    for polygon in polygons:
        if IsClose(polygon[0].Z, z ):
            #print("expected horizontal polygon" )
            pass
        a.append( FlattenXYZPointList( polygon ) )
    return a


def GetCoordinateSystemTranslationAndRotation(doc):
    '''
    Returns the rotation as a 3 x 3 matrix and the translation as a 1 x 3 matrix of the shared coordinate system active in document.

    :param doc: _description_
    :type doc: _type_

    :return: 3 x 3 matrix describing rotation, 1 x 3 matrix describing translation  
    :rtype: list (3) [list(3) int], list [int]
    '''

    projectLocationActive = doc.ActiveProjectLocation
    # get the inverse because we need to go back to origin
    totalTransform = projectLocationActive.GetTotalTransform().Inverse
    nBasisX = GetPointAsDoubles(totalTransform.BasisX)
    nBasisY = GetPointAsDoubles(totalTransform.BasisY)
    nBasisZ = GetPointAsDoubles(totalTransform.BasisZ)
    nOrigin = GetPointAsDoubles(totalTransform.Origin)
    return [nBasisX, nBasisY, nBasisZ],nOrigin

# --------------------------------------- is point in polygon ---------------------------------------
# from  https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
# ---------------------------------------------------------------------------------------------------

def GetQuadrant(vertex,  p ):
    '''
    Determines the quadrant of a polygon vertex relative to the test point.

    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html

    :param vertex: Revit UV element describing a vertex
    :type vertex: Autodesk.Revit.DB.UV
    :param p: Revit UV point
    :type p: Autodesk.Revit.DB.UV

    :return: An integer of range 0 - 4 describing the quadrant.
    :rtype: int
    '''

    returnValue = None
    if(vertex.U > p.U):
        if( vertex.V > p.V ):
            returnValue = 0
        else:
            returnValue = 3
    else:
        if( vertex.V > p.V ):
            returnValue = 1
        else:
            returnValue = 2
    return returnValue

def X_intercept(p, q, y ):
    '''
    Determine the X intercept of a polygon edge with a horizontal line at the Y value of the test point.

    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html

    :param p: Revit UV point
    :type p: Autodesk.Revit.DB.UV
    :param q: Revit UV point
    :type q: Autodesk.Revit.DB.UV
    :param y: _description_
    :type y: double

    :return: _description_
    :rtype: double
    '''
    if(0 != ( p.V - q.V )):
        #print('unexpected horizontal segment')
        pass
    
    return q.U - ( ( q.V - y ) * ( ( p.U - q.U ) / ( p.V - q.V ) ) )


def AdjustDelta(delta, vertex, next_vertex, p ):
    '''
    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html

    :param delta: _description_
    :type delta: _type_
    :param vertex: _description_
    :type vertex: _type_
    :param next_vertex: _description_
    :type next_vertex: _type_
    :param p: _description_
    :type p: _type_
    :return: _description_
    :rtype: _type_
    '''

    returnValue = delta
    # make quadrant deltas wrap around:
    if( delta == 3):
        returnValue = -1
    elif(delta == -3):
        returnValue = 1
    # check if went around point cw or ccw:
    elif(delta == 2):
        returnValue = 2
    elif(delta == -2):
        if( X_intercept( vertex, next_vertex, p.V ) > p.U ):
            returnValue = -delta
    return returnValue
      
def IsPointWithinPolygon(polygon, point):
    '''
    Checks whether a point is within a polygon.

    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
    odd number of windings rule:
    if (angle & 4) return INSIDE else return OUTSIDE
    non-zero winding rule:
    if (angle != 0) return INSIDE else return OUTSIDE

    :param polygon: A polygon
    :type polygon: list of Autodesk.Revit.DB.UV
    :param point: A point
    :type point: Autodesk.Revit.DB.UV

    :return: Refer winding rules above.
    :rtype: bool
    '''

    # initialize
    quad = GetQuadrant(polygon[ 0 ], point )
    angle = 0

    # loop on all vertices of polygon
    next_quad = 0
    delta = 0
    n = len(polygon)
    for i in range(n):
        vertex = polygon[ i ]
        next_vertex = None
        if(i + 1 < n):
            next_vertex = polygon[ i + 1 ]
        else:
            next_vertex = polygon[0]
        # calculate quadrant and delta from last quadrant
        next_quad = GetQuadrant( next_vertex, point )
        delta = next_quad - quad
        delta = AdjustDelta(delta, vertex, next_vertex, point )
        # add delta to total angle sum
        angle = angle + delta
        # increment for next step
        quad = next_quad
    ''' 
    odd number of windings rule:
    if (angle & 4) return INSIDE; else return OUTSIDE;
    non-zero winding rule:
    if (angle != 0) return INSIDE; else return OUTSIDE;
    '''
    # complete 360 degrees (angle of + 4 or -4 ) means inside
    return ( angle == +4 ) or ( angle == -4 )

# --------------------------------------- END --------------------------------------------------

def GetSignedPolygonArea( UVpoints ):
    '''
    Calculates the area of a signed UV polygon.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param UVpoints: list of points defining the polygon.
    :type UVpoints: list Autodesk.Revit.DB.UV

    :return: The area of the polygon.
    :rtype: double
    '''

    n = len(UVpoints)
    sum = UVpoints[0].U * ( UVpoints[1].V - UVpoints[n - 1].V )
    for i in range(1, n - 1):
        sum += UVpoints[i].U * ( UVpoints[i + 1].V - UVpoints[i - 1].V )
    sum += UVpoints[n - 1].U * ( UVpoints[0].V - UVpoints[n - 2].V );
    return 0.5 * sum

def ConvertEdgeArraysIntoListOfPoints(edgeArrays):
    '''
    Converts an edge array into a list of list of revit XYZ points.

    :param edgeArrays: A revit edge array.
    :type edgeArrays: Autodesk.Revit.DB.EdgeArrayArray ( no not a spelling mistake :) )

    :return: A List of list of revit XYZ points.
    :rtype: list of list Autodesk.Revit.DB.XYZ
    '''

    polygons = []
    for loop in edgeArrays:
        vertices = []
        q = None
        firstPoint = True
        for edge in loop:
            points = edge.Tessellate()
            if(firstPoint):
                q = points[0]
            n = len(points)
            for i in range (n-1):
                vertices.append( points[ i ] )
            firstPoint = False
        # close the loop by ending with first point...not required(?)
        # vertices.append(q)
        polygons.append(vertices)
    return polygons

def GetEdgePoints(edge):
    '''
    Retrieves the revit XYZ points defining an edge (curves get tessellated!)

    :param edge: An edge of a solid.
    :type edge: Autodesk.Revit.DB.Edge 

    :return: A list of revit XYZ points.
    :rtype: list Autodesk.Revit.DB.XYZ
    '''

    points = []
    for p in  edge.Tessellate():
        points.append(p)
    return points

def ConvertXYZInDataGeometry(doc, dgObject):
    '''
    Converts revit XYZ objects stored in a data geometry object into groups of doubles for inner and outer loops\
        and stores them in new data geometry object. It also populates translation and rotation matrix data of\
            coordinate system information.

    :param doc: _description_
    :type doc: _type_
    :param dgObject: A data geometry object.
    :type dgObject: :class:`.DataGeometry`
    
    :return: A data geometry object.
    :rtype: :class:`.DataGeometry`
    '''

    dataGeometry = dGeometry.DataGeometry()
    outerLoop = []
    for xyzPoint in dgObject.outerLoop:
        pointDouble = GetPointAsDoubles(xyzPoint)
        outerLoop.append(pointDouble)
    innerLoops = []
    for innerLoop in dgObject.innerLoops:
        innerLoopPoints = []
        for xyzPoint in innerLoop:
            pointDouble = GetPointAsDoubles(xyzPoint)
            innerLoopPoints.append(pointDouble)
        innerLoops.append(innerLoopPoints)
    dataGeometry.outerLoop = outerLoop
    dataGeometry.innerLoops = innerLoops
    # add coordinate system translation and rotation data
    dataGeometry.rotationCoord, dataGeometry.translationCoord = GetCoordinateSystemTranslationAndRotation(doc)
    return dataGeometry

def CheckDuplicateEdge(edges, edge):
    '''
    Checks whether a collection contains a given edge and returns True if that is the case.

    :param edges: List of edges toi check against.
    :type edges: list of Autodesk.Revit.DB.Edge
    :param edge: An edge
    :type edge: Autodesk.Revit.DB.Edge

    :return: True if edge is already in collection, otherwise False.
    :rtype: bool
    '''

    flagOverAll = False
    compPoints = GetEdgePoints(edge)
    if(len(edges) > 0):
        for e in edges:
            listPoints = GetEdgePoints(e)
            if (len(compPoints) == len(listPoints)):
                edgeSameFlag = True
                for p1 in compPoints:
                    if(CheckDuplicatePoint(listPoints, p1) == False):
                        edgeSameFlag = False
                if(edgeSameFlag):
                    flagOverAll = True
                    break
            else:
              pass
    else:
        pass # flag is already False
    return flagOverAll
        
def CheckSolidIsZeroHeight(solid):
    '''
    Checks if points making up a solid have multiple Z values.

    :param solid: A revit solid object.
    :type solid: Autodesk.Revit.DB.Solid

    :return: False if points collection of a solid has multiple z values, True if only one Z value in points collection (2D solid...??)
    :rtype: bool
    '''
    
    return  CheckEdgesAreZeroHeight(solid.Edges)

def CheckEdgesAreZeroHeight(edges):
    '''
    Checks if points making up a edges have multiple Z values.

    :param edges: A list of edges.
    :type edges: list Autodesk.Revit.DB.Edge

    :return: False if points collection of a edges has multiple z values, True if only one Z value in points collection (2D edges...??)
    :rtype: bool
    '''

    lowestZ = 0.0
    counter = 0
    for edge in edges:
        for p in edge.Tessellate():
            if (counter == 0):
                lowestZ = p.Z
            else:
                if(IsClose(p.Z, lowestZ) == False):
                    # found multiple z
                    return False
            counter = counter + 1
    return True

def GetLowestZFromSolidsPointCollection(solid):
    '''
    Gets the lowest Z value in a solids point collection.

    :param solid: A solid.
    :type solid: Autodesk.Revit.DB.Solid

    :return: The lowest Z value of any point in the solids vertex collection.
    :rtype: double
    '''
    
    return GetLowestZFromSolidsPointCollection(solid.Edges)

def GetLowestZFromEdgesPointCollection(edges):
    '''
    Gets the lowest Z value in a edges collection

    :param edges: A list of edges.
    :type edges: list Autodesk.Revit.DB.Edge

    :return: The lowest Z value of any point in the edges vertex collection.
    :rtype: double
    '''

    lowestZ = 0.0
    counter = 0
    for edge in edges:
        for p in edge.Tessellate():
            # make sure lowest z is initialized with the first point z values
            if (counter == 0):
                lowestZ = p.Z
            else:
                if(IsClose(p.Z, lowestZ) == False and p.Z < lowestZ):
                    lowestZ = p.Z
            counter = counter + 1 
    return lowestZ

def EdgesAreConnected(edge1, edge2):
    '''
    Checks whether edges are connected by comparing their points. If there is an identical point in both\
        then they are connected.

    Revit solids dont have crossing edges!

    :param edge1: An edge.
    :type edge1: Autodesk.Revit.DB.Edge
    :param edge2: Another edge.
    :type edge2: Autodesk.Revit.DB.Edge

    :return: _description_
    :rtype: bool
    '''

    for p1 in edge1.Tessellate():
        for p2 in edge2.Tessellate():
            if (ArePointsIdentical(p1, p2)):
                return True
    return False

def GetFacesSortedByAreaFromSolid(solid):
    '''
    Returns all faces from a solid sorted descending from biggest to smallest by area.

    :param solid: A solid.
    :type solid: Autodesk.Revit.DB.Solid

    :return: A list of faces, sorted biggest to smallest by area.
    :rtype: list Autodesk.Revit.DB.Face
    '''

    fl = []
    for face in solid.Faces:
        fl.append(face)
    return sorted(fl, key=lambda x: x.Area, reverse=True)

def PairFacesByArea(faces):
    '''
    Returns a list of lists of face pairs, where a nested list contains faces with the same measured area.
    
    Sample would be a ceiling solid. The top and bottom face of that ceiling would be an area pair.

    :param faces: A list of faces.
    :type faces: list Autodesk.Revit.DB.Face

    :return: A list of lists of faces.
    :rtype: list of list Autodesk.Revit.DB.Face
    '''

    returnValue = []
    # duplicate faces list since it will be manipulated
    copyFaces = list(faces)
    flag = True
    while flag:
        # loop over faces and try to find some with the same area measured
        sameArea = [copyFaces[0]]
        f = copyFaces[0]
        for i in range (1, len(copyFaces)):
            if (IsClose(f.Area, copyFaces[i].Area)):
                sameArea.append(copyFaces[i])
        returnValue.append(sameArea)
        # removes faces accounted for
        for a in sameArea:
            copyFaces.remove(a)
        if(len(copyFaces) < 2):
            flag = False
    return returnValue
                    
def GetFacesWithLowestZFromPairs(facePairs):
    '''
    Gets the face with the lowest Z value from list of faces.

    :param facePairs: A list of lists of face pairs, where a nested list contains faces with the same measured area.
    :type facePairs: list of list Autodesk.Revit.DB.Face

    :return: A list of faces.
    :rtype: list Autodesk.Revit.DB.Face
    '''

    faces = []
    for faceP in facePairs:
        lowestZ = 0.0
        counter = 0
        currentFace = None
        for face in faceP:
            currentZ = GetLowestZFromEdgesPointCollection(face.EdgeLoops[0])
            if(counter == 0):
                currentFace = face
                lowestZ = currentZ
                counter = counter + 1
            else:
                if(currentZ < lowestZ):
                    currentFace = face
                    lowestZ = currentZ
        faces.append(currentFace)
    return faces

def GetUniqueHorizontalFaces(faces):
    '''
    Filters out any horizontal faces from list of faces past in.
    
    Will also further filter by: faces with the same area only the face with the lower Z value will be returned.
    Note: works only on planar faces
    
    TODO: It could be way simpler just to check for the face with a negative face normal Z value...

    :param faces: A list of faces.
    :type faces: list Autodesk.Revit.DB.Face

    :return: A list of faces.
    :rtype: list Autodesk.Revit.DB.Face
    '''

    facesHorizontal = []
    for f in faces:
        # non planar faces are ignored for the moment...
        if(type(f) is rdb.PlanarFace):
            if (f.FaceNormal.Z != 0.0):
                facesHorizontal.append(f)
    
    facesFiltered = []
    if(len(facesHorizontal) > 1):
        # pair faces by area
        pairedFaces = PairFacesByArea(facesHorizontal)
        # get faces with lowest Z value for each pair
        facesFiltered =  GetFacesWithLowestZFromPairs(pairedFaces)
    return facesFiltered

def IsLoopWithinOtherLoopButNotReferenceLoops(exteriorLoop, otherLoop, holeLoops):
    '''
    Checks whether any of the other loops is within the exterior loop and if so\
        if it is not also within one of the holeLoops ...that would be an island
    
    :param exteriorLoop: A polygon loop describing the external boundary of a face.
    :type exteriorLoop: list of Autodesk.Revit.DB.UV
    :param otherLoop: A polygon loop which is to be checked as to whether it is within the exterior loop and the any hole loops.
    :type otherLoop: list of Autodesk.Revit.DB.UV
    :param holeLoops: A list of named tuples containing .loop property which is a list of UV points forming a polygon which have been identified\
         as creating a hole in the exteriorLoop.
    :type holeLoops: namedtuple('uvLoop', 'loop area id threeDPoly')\
        .Loop is a list of UV points defining a polygon loop
        .area is a double describing the polygon area
        .id is an integer
        .threeDPoly is an edge loop
    
    :return: True if within exterior loop but not within hole loops, otherwise False.
    :rtype: bool
    '''

    returnValue = False
    # get any point on the loop to check...if it is within the other loop then the entire loop is within the other loop
    # since revit does not allow for overlapping sketches
    point = otherLoop[0]
    # check whether point is within the other polygon loop
    if (IsPointWithinPolygon(exteriorLoop, point)):
        returnValue = True
        # check whether this point is within the polygon loops identified as holes
        # if so it is actually an island and will be accounted for separately
        if(len(holeLoops) > 0):
            for hLoop in holeLoops:
                if (IsPointWithinPolygon(hLoop.loop, point)):
                    returnValue = False
                    break
    return returnValue

def BuildLoopsDictionary(loops):
    '''
    Will return a dic where:

    - key is the outer loop of a polygon id
    - values is a list of tuples describing holes in the key polygon

    :param loops: A list of named tuples describing polygons.\
        .Loop is a list of UV points defining a polygon loop
        .area is a double describing the polygon area
        .id is an integer
        .threeDPoly is an edge loop
    :type loops: list[namedtuple('uvLoop', 'loop area id threeDPoly')]

    :return: A dictionary.
    :rtype: dic {int: list[namedtuple('uvLoop', 'loop area id threeDPoly')]}
    '''

    # duplicate list since I'am about to manipulate it...
    copyLoops = list(loops)
    flag = False
    returnValue = {}
    counter = 0
    # check if there is more then one loop  to start with
    if(len(copyLoops) > 1):
        loopFlag = True
        while loopFlag:
            # add the biggest loop as exterior to dictionary (first one in list)
            key = copyLoops[0].id
            returnValue[key] = []
            # assign loop to be checked for holes
            refLoop = copyLoops[0]
            # remove the first exterior loop from list of loops
            copyLoops.pop(0)
            # loop over remaining loops and work out which ones are holes ... if any
            for loop in copyLoops:
                # build list of hole loops already known belonging to this exterior loop
                holeLoops = []
                for geoLoop in returnValue[key]:
                    holeLoops.append(geoLoop)
                # check whether this is another hole loop
                flag = IsLoopWithinOtherLoopButNotReferenceLoops(refLoop.loop, loop.loop, holeLoops)
                if(flag):
                    returnValue[key].append(loop)
            # remove loops identified as holes from overall list as to avoid double counting
            for hole in returnValue[key]:
                counter = counter + 1
                copyLoops.remove(hole)
            # check whether all loops are accounted for
            if(len(copyLoops) == 0):
                loopFlag = False
    elif(len(copyLoops) == 1):
        key = copyLoops[0].id
        # only one exterior loop exists, no interior loops
        returnValue[key]=[]
    return returnValue


def ConvertSolidToFlattened2DPoints(solid):
    '''
    Converts a solid into a 2D polygon by projecting it onto a plane.( Removes Z values...)

    First nested list is the outer loop, any other following lists describe holes within the area of the polygon defined be points in first list.
    Arcs, circles will be tessellated to polygons.

    :param solid: A solid.
    :type solid: Autodesk.Revit.DB.Solid

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    '''

    '''
    sample for a sold with multiple sketches:
    [
        [
            [external poly line],[hole],[hole]
        ],
        [
            [external poly line] # without any holes
        ]
    ]
    
    sort faces into groups by volume:
    This may be required because a solid can be made up of multiple volumes (extrusion, sweeps etc)
    Turns out a solid returns a single face for multiple sketches. In order to work out whether these are multiple non overlapping polygons I will need to check
    whether a point from one polygon is within the other if so it may represents a hole or an island within a hole...to avoid misreading an island for a whole I will need to sort the faces by area
    and check from largest down to smallest.
    Also poly lines send back will always only represent: first list: exterior boundary as polygon any follow list is a hole within the polygon. Any islands in those holes will get their own top level representation
    i.e. no further list nesting!

    Within the faces groups: identify faces which are horizontal: its normal is facing up or down
    select the face with the lower Z coordinates and
    group all edges of the above face which form a closed loop (first loop of edges to describe the extend of that face, any secondary loops define holes in face)
    
    - > sort all edges by their connections (need to be connected by a point) so they describe a loop <- seems to be ok as revit provides them
    
    extract points of edges
    '''

    ceilingGeos = []
    # sort faces by size
    sortedBySizeFaces = GetFacesSortedByAreaFromSolid(solid)
    # get all faces which are horizontal only
    horizontalFaces = GetUniqueHorizontalFaces(sortedBySizeFaces)
    # loop of all horizontal faces and extract loops
    for hf in horizontalFaces:
        edgeLoops = ConvertEdgeArraysIntoListOfPoints(hf.EdgeLoops)
        # convert in UV coordinates
        edgeLoopsFlattened = FlattenXYZPointListOfLists(edgeLoops)
        #set up a named tuple to store data in it
        uvLoops = []
        uvLoop = namedtuple('uvLoop', 'loop area id threeDPoly')
        counter = 0
        for edgeLoopFlat in edgeLoopsFlattened:
            areaLoop = GetSignedPolygonArea( edgeLoopFlat )
            uvTuple = uvLoop(edgeLoopFlat, abs(areaLoop), counter, edgeLoops[counter])
            uvLoops.append(uvTuple)
            counter += 1
        uvLoops = sorted(uvLoops, key=lambda x: x.area, reverse=True)
        # sort loops into exterior and hole loops
        loopDic = BuildLoopsDictionary(uvLoops)
        for key in loopDic:
            dataGeometry = dGeometry.DataGeometry()
            keyList =[]
            # find matching loop by id
            for x in uvLoops:
                if x.id == key:
                    keyList = x
                    break
            dataGeometry.outerLoop = keyList.threeDPoly
            if(len(loopDic[key])>0):
                for hole in loopDic[key]:
                    dataGeometry.innerLoops.append(hole.threeDPoly)
            else:
                dataGeometry.innerLoops = []
            ceilingGeos.append(dataGeometry)
    return ceilingGeos