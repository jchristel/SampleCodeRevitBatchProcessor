"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit geometry extraction helper functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

import Autodesk.Revit.DB as rdb


# ---------------------------- debug ----------------------------
def get_point_as_string(point):
    """
    Returns Revit point as a string.

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: String in format 'X:Y:Z'
    :rtype: str
    """

    return str(point.X) + " : " + str(point.Y) + " : " + str(point.Z)


def get_edge_as_string(edge):
    """
    Returns a revit edge as a string.

    :param edge: A revit edge.
    :type edge: Autodesk.Revit.DB.Edge

    :return: String where each row represents a point on the edge.
    :rtype: str
    """

    returnValue = ""
    for p in edge.Tessellate():
        returnValue = returnValue + "\n" + get_point_as_string(p)
    return returnValue


# ---------------------------- math utility ----------------------------


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    """
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
    """

    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def are_points_identical(p1, p2):
    """
    Compares the X,Y,Z values of two revit point and returns True if they are the same, otherwise False

    :param p1: A revit point.
    :type p1: Autodesk.Revit.DB.XYZ
    :param p2: A revit point.
    :type p2: Autodesk.Revit.DB.XYZ

    :return: True if they are the same, otherwise False.
    :rtype: bool
    """

    if is_close(p1.X, p2.X) and is_close(p1.Y, p2.Y) and is_close(p1.Z, p2.Z):
        return True
    else:
        return False


def check_duplicate_point(points, point):
    """
    Checks whether a collection of points contains another given point and returns True if that is the case.

    :param points: List of revit points
    :type points: list Autodesk.Revit.DB.XYZ
    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: True if point is in collection, otherwise False.
    :rtype: bool
    """

    for p1 in points:
        if are_points_identical(p1, point):
            return True
    return False


def get_point_as_doubles(point):
    """
    Converts a revit XYZ to a list of doubles in order x,y,z.

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: List of doubles in order of x,y,z
    :rtype: list double
    """

    return [point.X, point.Y, point.Z]


def flatten_xyz_point(point):
    """
    Flattens a XYZ point to a UV by omitting the Z value of the XYZ.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: A 2D point (UV)
    :rtype:  Autodesk.Revit.DB.UV
    """

    return rdb.UV(point.X, point.Y)


def flatten_xyz_point_list(polygon):
    """
    Flattens a list of XYZ points to a list of UV points by omitting the Z value of each XYZ.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param polygon: list of XYZ points
    :type polygon: list Autodesk.Revit.DB.XYZ

    :return: list of UV points
    :rtype: list Autodesk.Revit.DB.UV
    """

    z = polygon[0].Z
    a = []
    for p in polygon:
        if is_close(p.Z, z):
            # print("expected horizontal polygon" )
            pass
        a.append(flatten_xyz_point(p))
    return a


def flatten_xyz_point_list_of_lists(polygons):
    """
    Flattens a list lists of XYZ points to a list of lists of UV points by omitting the Z value of each XYZ.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param polygon: list of lists of XYZ points
    :type polygon: list [list Autodesk.Revit.DB.XYZ]

    :return: list of lists of UV points
    :rtype: list [list Autodesk.Revit.DB.UV]
    """

    z = polygons[0][0].Z
    a = []
    for polygon in polygons:
        if is_close(polygon[0].Z, z):
            # print("expected horizontal polygon" )
            pass
        a.append(flatten_xyz_point_list(polygon))
    return a


def get_coordinate_system_translation_and_rotation(doc):
    """
    Returns the rotation as a 3 x 3 matrix and the translation as a 1 x 3 matrix of the shared coordinate system active in document.

    :param doc: _description_
    :type doc: _type_

    :return: 3 x 3 matrix describing rotation, 1 x 3 matrix describing translation
    :rtype: list (3) [list(3) int], list [int]
    """

    projectLocationActive = doc.ActiveProjectLocation
    # get the inverse because we need to go back to origin
    totalTransform = projectLocationActive.GetTotalTransform().Inverse
    nBasisX = get_point_as_doubles(totalTransform.BasisX)
    nBasisY = get_point_as_doubles(totalTransform.BasisY)
    nBasisZ = get_point_as_doubles(totalTransform.BasisZ)
    nOrigin = get_point_as_doubles(totalTransform.Origin)
    return [nBasisX, nBasisY, nBasisZ], nOrigin


# --------------------------------------- is point in polygon ---------------------------------------
# from  https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html
# ---------------------------------------------------------------------------------------------------


def get_quadrant(vertex, p):
    """
    Determines the quadrant of a polygon vertex relative to the test point.

    https://thebuildingcoder.typepad.com/blog/2010/12/point-in-polygon-containment-algorithm.html

    :param vertex: Revit UV element describing a vertex
    :type vertex: Autodesk.Revit.DB.UV
    :param p: Revit UV point
    :type p: Autodesk.Revit.DB.UV

    :return: An integer of range 0 - 4 describing the quadrant.
    :rtype: int
    """

    returnValue = None
    if vertex.U > p.U:
        if vertex.V > p.V:
            returnValue = 0
        else:
            returnValue = 3
    else:
        if vertex.V > p.V:
            returnValue = 1
        else:
            returnValue = 2
    return returnValue


def x_intercept(p, q, y):
    """
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
    """
    if 0 != (p.V - q.V):
        # print('unexpected horizontal segment')
        pass

    return q.U - ((q.V - y) * ((p.U - q.U) / (p.V - q.V)))


def adjust_delta(delta, vertex, next_vertex, p):
    """
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
    """

    returnValue = delta
    # make quadrant deltas wrap around:
    if delta == 3:
        returnValue = -1
    elif delta == -3:
        returnValue = 1
    # check if went around point cw or ccw:
    elif delta == 2:
        returnValue = 2
    elif delta == -2:
        if x_intercept(vertex, next_vertex, p.V) > p.U:
            returnValue = -delta
    return returnValue


def is_point_within_polygon(polygon, point):
    """
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
    """

    # initialize
    quad = get_quadrant(polygon[0], point)
    angle = 0

    # loop on all vertices of polygon
    next_quad = 0
    delta = 0
    n = len(polygon)
    for i in range(n):
        vertex = polygon[i]
        next_vertex = None
        if i + 1 < n:
            next_vertex = polygon[i + 1]
        else:
            next_vertex = polygon[0]
        # calculate quadrant and delta from last quadrant
        next_quad = get_quadrant(next_vertex, point)
        delta = next_quad - quad
        delta = adjust_delta(delta, vertex, next_vertex, point)
        # add delta to total angle sum
        angle = angle + delta
        # increment for next step
        quad = next_quad
    """ 
    odd number of windings rule:
    if (angle & 4) return INSIDE; else return OUTSIDE;
    non-zero winding rule:
    if (angle != 0) return INSIDE; else return OUTSIDE;
    """
    # complete 360 degrees (angle of + 4 or -4 ) means inside
    return (angle == +4) or (angle == -4)


# --------------------------------------- END --------------------------------------------------


def get_signed_polygon_area(uv_points):
    """
    Calculates the area of a signed UV polygon.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param uv_points: list of points defining the polygon.
    :type uv_points: list Autodesk.Revit.DB.UV

    :return: The area of the polygon.
    :rtype: double
    """

    n = len(uv_points)
    sum = uv_points[0].U * (uv_points[1].V - uv_points[n - 1].V)
    for i in range(1, n - 1):
        sum += uv_points[i].U * (uv_points[i + 1].V - uv_points[i - 1].V)
    sum += uv_points[n - 1].U * (uv_points[0].V - uv_points[n - 2].V)
    return 0.5 * sum


def convert_edge_arrays_into_list_of_points(edge_arrays):
    """
    Converts an edge array into a list of list of revit XYZ points.

    :param edge_arrays: A revit edge array.
    :type edge_arrays: Autodesk.Revit.DB.EdgeArrayArray ( no not a spelling mistake :) )

    :return: A List of list of revit XYZ points.
    :rtype: list of list Autodesk.Revit.DB.XYZ
    """

    polygons = []
    for loop in edge_arrays:
        vertices = []
        q = None
        (first_point) = True
        for edge in loop:
            points = edge.Tessellate()
            if first_point:
                q = points[0]
            n = len(points)
            for i in range(n - 1):
                vertices.append(points[i])
            (first_point) = False
        # close the loop by ending with first point...not required(?)
        # vertices.append(q)
        polygons.append(vertices)
    return polygons


def get_edge_points(edge):
    """
    Retrieves the revit XYZ points defining an edge (curves get tessellated!)

    :param edge: An edge of a solid.
    :type edge: Autodesk.Revit.DB.Edge

    :return: A list of revit XYZ points.
    :rtype: list Autodesk.Revit.DB.XYZ
    """

    points = []
    for p in edge.Tessellate():
        points.append(p)
    return points


def check_duplicate_edge(edges, edge):
    """
    Checks whether a collection contains a given edge and returns True if that is the case.

    :param edges: List of edges toi check against.
    :type edges: list of Autodesk.Revit.DB.Edge
    :param edge: An edge
    :type edge: Autodesk.Revit.DB.Edge

    :return: True if edge is already in collection, otherwise False.
    :rtype: bool
    """

    flag_over_all = False
    comp_points = get_edge_points(edge)
    if len(edges) > 0:
        for e in edges:
            list_points = get_edge_points(e)
            if len(comp_points) == len(list_points):
                edge_same_flag = True
                for p1 in comp_points:
                    if check_duplicate_point(list_points, p1) == False:
                        edge_same_flag = False
                if edge_same_flag:
                    flag_over_all = True
                    break
            else:
                pass
    else:
        pass  # flag is already False
    return flag_over_all


def check_solid_is_zero_height(solid):
    """
    Checks if points making up a solid have multiple Z values.

    :param solid: A revit solid object.
    :type solid: Autodesk.Revit.DB.Solid

    :return: False if points collection of a solid has multiple z values, True if only one Z value in points collection (2D solid...??)
    :rtype: bool
    """

    return check_edges_are_zero_height(solid.Edges)


def check_edges_are_zero_height(edges):
    """
    Checks if points making up a edges have multiple Z values.

    :param edges: A list of edges.
    :type edges: list Autodesk.Revit.DB.Edge

    :return: False if points collection of a edges has multiple z values, True if only one Z value in points collection (2D edges...??)
    :rtype: bool
    """

    lowest_z = 0.0
    counter = 0
    for edge in edges:
        for p in edge.Tessellate():
            if counter == 0:
                lowest_z = p.Z
            else:
                if is_close(p.Z, lowest_z) == False:
                    # found multiple z
                    return False
            counter = counter + 1
    return True


def get_lowest_z_from_solid(solid):
    """
    Gets the lowest Z value in a solids point collection.

    :param solid: A solid.
    :type solid: Autodesk.Revit.DB.Solid

    :return: The lowest Z value of any point in the solids vertex collection.
    :rtype: double
    """

    return get_lowest_z_from_edges_point_collection(solid.Edges)


def get_lowest_z_from_edges_point_collection(edges):
    """
    Gets the lowest Z value in a edges collection

    :param edges: A list of edges.
    :type edges: list Autodesk.Revit.DB.Edge

    :return: The lowest Z value of any point in the edges vertex collection.
    :rtype: double
    """

    lowest_z = 0.0
    counter = 0
    for edge in edges:
        for p in edge.Tessellate():
            # make sure lowest z is initialized with the first point z values
            if counter == 0:
                lowest_z = p.Z
            else:
                if is_close(p.Z, lowest_z) == False and p.Z < lowest_z:
                    lowest_z = p.Z
            counter = counter + 1
    return lowest_z


def edges_are_connected(edge1, edge2):
    """
    Checks whether edges are connected by comparing their points. If there is an identical point in both\
        then they are connected.

    Revit solids dont have crossing edges!

    :param edge1: An edge.
    :type edge1: Autodesk.Revit.DB.Edge
    :param edge2: Another edge.
    :type edge2: Autodesk.Revit.DB.Edge

    :return: _description_
    :rtype: bool
    """

    for p1 in edge1.Tessellate():
        for p2 in edge2.Tessellate():
            if are_points_identical(p1, p2):
                return True
    return False


def get_faces_sorted_by_area_from_solid(solid):
    """
    Returns all faces from a solid sorted descending from biggest to smallest by area.

    :param solid: A solid.
    :type solid: Autodesk.Revit.DB.Solid

    :return: A list of faces, sorted biggest to smallest by area.
    :rtype: list Autodesk.Revit.DB.Face
    """

    fl = []
    for face in solid.Faces:
        fl.append(face)
    return sorted(fl, key=lambda x: x.Area, reverse=True)


def pair_faces_by_area(faces):
    """
    Returns a list of lists of face pairs, where a nested list contains faces with the same measured area.

    Sample would be a ceiling solid. The top and bottom face of that ceiling would be an area pair.

    :param faces: A list of faces.
    :type faces: list Autodesk.Revit.DB.Face

    :return: A list of lists of faces.
    :rtype: list of list Autodesk.Revit.DB.Face
    """

    return_value = []
    # duplicate faces list since it will be manipulated
    copy_faces = list(faces)
    flag = True
    while flag:
        # loop over faces and try to find some with the same area measured
        same_area = [copy_faces[0]]
        f = copy_faces[0]
        for i in range(1, len(copy_faces)):
            if is_close(f.Area, copy_faces[i].Area):
                same_area.append(copy_faces[i])
        return_value.append(same_area)
        # removes faces accounted for
        for a in same_area:
            copy_faces.remove(a)
        if len(copy_faces) < 2:
            flag = False
    return return_value


def get_faces_with_lowest_z_from_pairs(face_pairs):
    """
    Gets the face with the lowest Z value from list of faces.

    :param face_pairs: A list of lists of face pairs, where a nested list contains faces with the same measured area.
    :type face_pairs: list of list Autodesk.Revit.DB.Face

    :return: A list of faces.
    :rtype: list Autodesk.Revit.DB.Face
    """

    faces = []
    for faceP in face_pairs:
        lowestZ = 0.0
        counter = 0
        current_face = None
        for face in faceP:
            current_z = get_lowest_z_from_edges_point_collection(face.EdgeLoops[0])
            if counter == 0:
                current_face = face
                lowestZ = current_z
                counter = counter + 1
            else:
                if current_z < lowestZ:
                    current_face = face
                    lowestZ = current_z
        faces.append(current_face)
    return faces


def get_unique_horizontal_faces(faces):
    """
    Filters out any horizontal faces from list of faces past in.

    Will also further filter by: faces with the same area only the face with the lower Z value will be returned.
    Note: works only on planar faces

    TODO: It could be way simpler just to check for the face with a negative face normal Z value...

    :param faces: A list of faces.
    :type faces: list Autodesk.Revit.DB.Face

    :return: A list of faces.
    :rtype: list Autodesk.Revit.DB.Face
    """

    faces_horizontal = []
    for f in faces:
        # non planar faces are ignored for the moment...
        if type(f) is rdb.PlanarFace:
            if f.FaceNormal.Z != 0.0:
                faces_horizontal.append(f)

    faces_filtered = []
    if len(faces_horizontal) > 1:
        # pair faces by area
        paired_faces = pair_faces_by_area(faces_horizontal)
        # get faces with lowest Z value for each pair
        faces_filtered = get_faces_with_lowest_z_from_pairs(paired_faces)
    return faces_filtered


def is_loop_within_other_loop_but_not_reference_loops(
    exterior_loop, other_loop, hole_loops
):
    """
    Checks whether any of the other loops is within the exterior loop and if so\
        if it is not also within one of the holeLoops ...that would be an island
    
    :param exterior_loop: A polygon loop describing the external boundary of a face.
    :type exterior_loop: list of Autodesk.Revit.DB.UV
    :param other_loop: A polygon loop which is to be checked as to whether it is within the exterior loop and the any hole loops.
    :type other_loop: list of Autodesk.Revit.DB.UV
    :param hole_loops: A list of named tuples containing .loop property which is a list of UV points forming a polygon which have been identified\
         as creating a hole in the exteriorLoop.
    :type hole_loops: namedtuple('uvLoop', 'loop area id threeDPoly')\
        .Loop is a list of UV points defining a polygon loop
        .area is a double describing the polygon area
        .id is an integer
        .threeDPoly is an edge loop
    
    :return: True if within exterior loop but not within hole loops, otherwise False.
    :rtype: bool
    """

    return_value = False
    # get any point on the loop to check...if it is within the other loop then the entire loop is within the other loop
    # since revit does not allow for overlapping sketches
    point = other_loop[0]
    # check whether point is within the other polygon loop
    if is_point_within_polygon(exterior_loop, point):
        return_value = True
        # check whether this point is within the polygon loops identified as holes
        # if so it is actually an island and will be accounted for separately
        if len(hole_loops) > 0:
            for hole_loop in hole_loops:
                if is_point_within_polygon(hole_loop.loop, point):
                    return_value = False
                    break
    return return_value


def build_loops_dictionary(loops):
    """
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
    """

    # duplicate list since I'am about to manipulate it...
    copy_loops = list(loops)
    flag = False
    return_value = {}
    counter = 0
    # check if there is more then one loop  to start with
    if len(copy_loops) > 1:
        loop_flag = True
        while loop_flag:
            # add the biggest loop as exterior to dictionary (first one in list)
            key = copy_loops[0].id
            return_value[key] = []
            # assign loop to be checked for holes
            reference_loop = copy_loops[0]
            # remove the first exterior loop from list of loops
            copy_loops.pop(0)
            # loop over remaining loops and work out which ones are holes ... if any
            for loop in copy_loops:
                # build list of hole loops already known belonging to this exterior loop
                hole_loops = []
                for geo_loop in return_value[key]:
                    hole_loops.append(geo_loop)
                # check whether this is another hole loop
                flag = is_loop_within_other_loop_but_not_reference_loops(
                    reference_loop.loop, loop.loop, hole_loops
                )
                if flag:
                    return_value[key].append(loop)
            # remove loops identified as holes from overall list as to avoid double counting
            for hole in return_value[key]:
                counter = counter + 1
                copy_loops.remove(hole)
            # check whether all loops are accounted for
            if len(copy_loops) == 0:
                loop_flag = False
    elif len(copy_loops) == 1:
        key = copy_loops[0].id
        # only one exterior loop exists, no interior loops
        return_value[key] = []
    return return_value
