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
from Autodesk.Revit.DB import *

import DataGeometry as dGeometry

# ---------------------------- debug ----------------------------
def GetPointAsString (point):
    return str(point.X) + ' : ' + str(point.Y) + ' : ' + str(point.Z)
    
def GetEdgeAsString(edge):
    returnValue = ''
    for p in edge.Tessellate():
        returnValue = returnValue + '\n' + GetPointAsString (p)
    return returnValue

# ---------------------------- math utility ----------------------------

# a     float
# b     float
def IsClose(a, b, rel_tol=1e-09, abs_tol=0.0):
    '''
    compares two floats with a tolerance. Returns True if they are close enough, otherwise False
    refer to: https://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python
    '''
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# p1         Revit XYZ point
# p2         Revit XYZ point
def ArePointsIdentical(p1, p2):
    ''' 
    compares the X,Y,Z values of a revit point and returns True if they are the same
    returns False if they are not the same
    '''
    if (IsClose(p1.X,p2.X) and IsClose(p1.Y, p2.Y) and IsClose(p1.Z,p2.Z)):
        return True
    else:
        return False

# points        collection of Revit  XYZ points
# point         Revit XYZ point
def CheckDuplicatePoint(points, point):
    '''
    Checks whether a collection contains a given point and returns True if that is the case
    '''
    for p1 in points:
        if(ArePointsIdentical(p1, point)):
            return True
    return False

# point         Revit XYZ point
def GetPointAsDoubles(point):
    '''
    returns a revit XYZ as a list of doubles in order x,y,z
    '''
    return [point.X, point.Y, point.Z]

# point         Revit XYZ point
def FlattenXYZPoint(point):
    '''
    flattens a XYZ pint to a UV by just omitting the Z value
    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html
    '''
    return UV( point.X, point.Y )

# polygon         list of Revit XYZ points
def FlattenXYZPointList(polygon):
    '''
    flattens a list of XYZ pint to a list of UV points by just omitting the Z value
    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html
    '''
    z = polygon[0].Z;
    a = []
    for p in polygon :
        if(IsClose(p.Z, z)):
            #print("expected horizontal polygon" )
            pass
        a.append( FlattenXYZPoint( p ) )
    return a

# polygon         list of list of Revit XYZ points representing multiple polygons
def FlattenXYZPointListOfLists(  polygons ):
    '''
    flattens a list of lists of XYZ pint to a list of UV points by just omitting the Z value
    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html
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
    returns then translation as a 1 x 3 matrix and the rotation as a 3 x 3 matrix of the shared cordinate system active
    in document
    '''
    plAtive = doc.ActiveProjectLocation
    totalTransform = plAtive.GetTotalTransform().Inverse
    nBasisX = GetPointAsDoubles(totalTransform.BasisX)
    nBasisY = GetPointAsDoubles(totalTransform.BasisY)
    nBasisZ = GetPointAsDoubles(totalTransform.BasisZ)
    nOrigin = GetPointAsDoubles(totalTransform.Origin)
    return [nBasisX, nBasisY, nBasisZ],nOrigin
    pass

# --------------------------------------- is point in polygon ---------------------------------------
# from  https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
# ---------------------------------------------------------------------------------------------------

# vertex        Revit UV element
# p             Revit UV point
def GetQuadrant(vertex,  p ):
    '''
    Determine the quadrant of a polygon vertex relative to the test point.
    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
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

# p             Revit UV point
# q             Revit UV point
# y             double
def X_intercept(p, q, y ):
    '''
    Determine the X intercept of a polygon edge with a horizontal line at the Y value of the test point.
    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
    '''
    if(0 != ( p.V - q.V )):
        #print('unexpected horizontal segment')
        pass
    
    return q.U - ( ( q.V - y ) * ( ( p.U - q.U ) / ( p.V - q.V ) ) )


def AdjustDelta(delta, vertex, next_vertex, p ):
    '''
    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
    '''
    returnvalue = delta
    # make quadrant deltas wrap around:
    if( delta == 3):
        returnvalue = -1
    elif(delta == -3):
        returnvalue = 1
    # check if went around point cw or ccw:
    elif(delta == 2):
        returnvalue = 2
    elif(delta == -2):
        if( X_intercept( vertex, next_vertex, p.V ) > p.U ):
            returnvalue = -delta
    return returnvalue

# polygon       Revit UVArray element
# point         Revit UV element
def IsPointWithinPolygon(polygon, point):
    '''
    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
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

# UVpoints        list of UV points defining a polygon
def GetSignedPolygonArea( UVpoints ):
    '''
    returns the area of a signed UV polygon
    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html
    '''
    n = len(UVpoints)
    sum = UVpoints[0].U * ( UVpoints[1].V - UVpoints[n - 1].V )
    for i in range(1, n - 1):
        sum += UVpoints[i].U * ( UVpoints[i + 1].V - UVpoints[i - 1].V )
    sum += UVpoints[n - 1].U * ( UVpoints[0].V - UVpoints[n - 2].V );
    return 0.5 * sum

# edgeArrays      Revit EdgeArrayArray
def ConvertEdgeArraysIntoListOfPoints(edgeArrays):
    '''
    returns a list of list of revit XYZ points representing the edges passt in
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

# edge          Revit Edge objectS
def GetEdgePoints(edge):
    '''
    returns the Revit XYZ points defining an edge (curves get tesselated!)
    '''
    points = []
    for p in  edge.Tessellate():
        points.append(p)
    return points

# doc                   current revit document
# dgObject              a data geometry object
def ConvertXYZInDataGeometry(doc, dgObject):
    '''
    converts revit XYZ objects to groups of doubles and populates translation and rotation matrix data of coordinate system information
    '''
    dgeo = dGeometry.DataGeometry()
    outerLoop = []
    for xyzPoint in dgObject.outerLoop:
        pdouble = GetPointAsDoubles(xyzPoint)
        outerLoop.append(pdouble)
    innerLoops = []
    for innerLoop in dgObject.innerLoops:
        innerLoopPoints = []
        for xyzPoint in innerLoop:
            pdouble = GetPointAsDoubles(xyzPoint)
            innerLoopPoints.append(pdouble)
        innerLoops.append(innerLoopPoints)
    dgeo.outerLoop = outerLoop
    dgeo.innerLoops = innerLoops
    # add coordinate system translation and rotation data
    dgeo.rotationCoord, dgeo.translationCoord = GetCoordinateSystemTranslationAndRotation(doc)
    return dgeo

# edges         list of Revit Edge objects
# edge          Revit Edge objectS
def CheckDuplicateEdge(edges, edge):
    '''
    Checks whether a collection contains a given edge and returns True if that is the case
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
        
# solid         a Revit Solid object
def CheckSolidIsZeroHeight(solid):
    ''' 
    returns False if points collection of a solid has multiple z values, 
    returns True if only one Z value in points collection (2D solid...??)
    '''
    return  CheckEdgesAreZeroHeight(solid.Edges)

# edges         a list of Revit edge elements
def CheckEdgesAreZeroHeight(edges):
    ''' 
    returns False if points collection of a edges has multiple z values, 
    returns True if only one Z value in points collection (2D solid...??)
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

# solid         a Revit Solid element
def GetLowestZFromSolidsPointCollection(solid):
    ''' 
    returns the lowest Z value in a solids point collection
    '''
    return GetLowestZFromSolidsPointCollection(solid.Edges)

# edges         a list of Revit edge elements
def GetLowestZFromEdgesPointCollection(edges):
    ''' 
    returns the lowest Z value in a solids point collection
    '''
    lowestZ = 0.0
    counter = 0
    for edge in edges:
        for p in edge.Tessellate():
            # make sure lowest z is initialist with the first point z values
            if (counter == 0):
                lowestZ = p.Z
            else:
                if(IsClose(p.Z, lowestZ) == False and p.Z < lowestZ):
                    lowestZ = p.Z
            counter = counter + 1 
    return lowestZ

# edge1         Revit edge element
# edge2         Recit edge element
def EdgesAreConnected(edge1, edge2):
    '''
    returns true if the two edges passt in share at least one point
    '''
    for p1 in edge1.Tessellate():
        for p2 in edge2.Tessellate():
            if (ArePointsIdentical(p1, p2)):
                return True
    return False

# solid          a Revit solid element
def GetFacesSortedByAreaFromSolid(solid):
    '''
    returns all faces from a solid sorted descending from biggest to smallest by area
    '''
    fl = []
    for face in solid.Faces:
        fl.append(face)
    return sorted(fl, key=lambda x: x.Area, reverse=True)

# faces         a list of Revit faces
def PairFacesByArea(faces):
    '''
    returns a list of lists of area pairs
    where a pair are areas with the same measured area
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
                    
# facePairs     list of list of Revit faces
def GetFacesWithLowestZFromPairs(facePairs):
    '''
    returns the face with the lowest Z value from each pairing
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

# faces         a list of faces
def GetUniqueHorizontalFaces(faces):
    '''
    filters out any horizontal faces from list of faces past in
    will also further filter by: faces with the same area only the face with the lower Z value will be returned
    works only on planar faces
    '''
    
    '''
    note:
    It could be way simpler just to check for the face with a negative face normal Z value...
    '''
    facesHorizontal = []
    for f in faces:
        # non planar faces are ignored for the moment...
        if(type(f) is PlanarFace):
            if (f.FaceNormal.Z != 0.0):
                facesHorizontal.append(f)
    
    facesFiltered = []
    if(len(facesHorizontal) > 1):
        # pair faces by area
        pairedFaces = PairFacesByArea(facesHorizontal)
        # get faces with lowest Z value for each pair
        facesFiltered =  GetFacesWithLowestZFromPairs(pairedFaces)
    return facesFiltered

# exteriorLoop        a polygon loop describing the external boundary of a face
# otherLoop           a polygon loop which is to be checked as to whether it is within the exterioir loop and the any hole loops
# holeLoops           a list of named tuples containing .loop property which is a list of UV points formning a polygon which have been identified as creating a hole in the exteriorLoop 
def IsLoopWithinOtherLoopButNotReferenceLoops(exteriorLoop, otherLoop, holeLoops):
    '''
    checks whether any of the other loops is within the exterior loop and if so
    if it is not also within one of the holeLoops ...that would be an island
    returns true if within exterior loop but not within hole loops
    '''
    returnValue = False
    # get any point on the loop to check...if it is within the other loop then the entire loop is within the other loop
    # since revit does not allow for overlapping sketches
    point = otherLoop[0]
    # check whether point is within the other polygon loop
    if (IsPointWithinPolygon(exteriorLoop, point)):
        returnValue = True
        # check whether this point is within the polygon loops identified as holes
        # if so it is actually an island and will be accounted for seperately
        if(len(holeLoops) > 0):
            for hLoop in holeLoops:
                if (IsPointWithinPolygon(hLoop.loop, point)):
                    returnValue = False
                    break
    return returnValue

#loops      list of named tuples with properties loop, id and area.Loop is a list of UV points defining a polygon loop
def BuildLoopsDictionary(loops):
    '''
    will return a dic where:
    - key is the outer loop of a polygon id
    - values is a list of tuples describing holes in the key polygon
    '''
    # duplicate list since I'am about to manipulate it...
    copyLoops = list(loops)
    flag = False
    returnValue = {}
    counter = 0
    # check if there is more then one loop  to start with
    if(len(copyLoops) > 1):
        loopflag = True
        while loopflag:
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
                loopflag = False
    elif(len(copyLoops) == 1):
        key = copyLoops[0].id
        # only one exterior loop exists, no interior loops
        returnValue[key]=[]
    return returnValue


# solid         a Revit Solid element
def ConvertSolidToFlattened2DPoints(solid):
    '''
    returns a list of lists of Revit XYZ points describing the outline of a solid projected onto a plane
    first nested list is the outer loop, any other following lists describe holes within the area of the polygon defined be points in first list
    arcs, circles will be tesselated to polygons
    sample for a sold with mutltiple sketches:
    [
        [
            [external polyline],[hole],[hole]
        ],
        [
            [external polyline] # without any holes
        ]
    ]
    '''
    
    '''
    sort faces into groupes by volumne:
    This may be required because a solid can be made up of multiple volumnes (extrusion, sweeps etc)
    Turns out a solid returns a single face for multiple sketches. In order to work out whether these are multiple non overlapping polygons I will need to check
    whether a point from one polygon is within the other if so it may represents a hole or an island within a hole...to avoid misreading an island for a whole I will need to sort the faces by area
    and chjeck from largest down to smallest.
    Also polylines send back will always only represent: first list: exterior boundary as polygon any follow list is a hole within the polygon. Any islands in thoe holes will get their own top level represntation
    i.e. no further list nesting!

    Within the faces groups: identify faces which are horizontal: its normal is facing up or down
    select the face with the lower Z coordinates and
    group all edges of the above face which form a closed loop (first loop of edges to descibe the extend of that face, any secondary loops define holes in face)
    
    - > sort all edges by their connections (need to be connected by a point) so they descibe a loop <- seems to be ok as revit provides them
    
    extract points of edges
    '''
    ceilingGeos = []
    # sort faces by size
    sortedBySizeFaces = GetFacesSortedByAreaFromSolid(solid)
    # get all faces which are horizontal only
    hotizontalFaces = GetUniqueHorizontalFaces(sortedBySizeFaces)
    # loop of all horizontal faces and extract loops
    for hf in hotizontalFaces:
        edgeLoops = ConvertEdgeArraysIntoListOfPoints(hf.EdgeLoops)
        # convert in UV coordinates
        edgeLoopsFlattened = FlattenXYZPointListOfLists(edgeLoops)
        #set up a named tuple to store data in it
        uvloops = []
        uvLoop = namedtuple('uvLoop', 'loop area id threeDPoly')
        counter = 0
        for edgeloopF in edgeLoopsFlattened:
            areaLoop = GetSignedPolygonArea( edgeloopF )
            uvTuple = uvLoop(edgeloopF, abs(areaLoop), counter, edgeLoops[counter])
            uvloops.append(uvTuple)
            counter += 1
        uvloops = sorted(uvloops, key=lambda x: x.area, reverse=True)
        # sort loops into exterior and hole loops
        loopDic = BuildLoopsDictionary(uvloops)
        for key in loopDic:
            dgeo = dGeometry.DataGeometry()
            keyList =[]
            # find matching loop by id
            for x in uvloops:
                if x.id == key:
                    keyList = x
                    break
            dgeo.outerLoop = keyList.threeDPoly
            if(len(loopDic[key])>0):
                for hole in loopDic[key]:
                    dgeo.innerLoops.append(hole.threeDPoly)
            else:
                dgeo.innerLoops = []
            ceilingGeos.append(dgeo)
    return ceilingGeos