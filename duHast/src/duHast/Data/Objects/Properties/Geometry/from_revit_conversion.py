"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit Geometry to data geometry conversion helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

from duHast.Data.Objects.Properties.Geometry import geometry_polygon as dGeometryPoly
from duHast.Revit.Common.Geometry import geometry as rGeo
from collections import namedtuple


def convert_xyz_in_data_geometry_polygons(doc, dgObject):
    """
    Converts Revit XYZ objects stored in a data geometry object into groups of doubles for inner and outer loops\
        and stores them in new data geometry object. It also populates translation and rotation matrix data of\
            coordinate system information.
    :param doc: _description_
    :type doc: _type_
    :param dgObject: A data geometry object.
    :type dgObject: :class:`.DataGeometryPolygon`
    :return: A data geometry object.
    :rtype: :class:`.DataGeometryPolygon`
    """

    data_geometry = dGeometryPoly.DataPolygon()
    outer_loop = []
    for xyz_point in dgObject.outer_loop:
        point_as_double = rGeo.get_point_as_doubles(xyz_point)
        outer_loop.append(point_as_double)
    inner_loops = []
    for inner_loop in dgObject.inner_loops:
        inner_loop_points = []
        for xyz_point in inner_loop:
            point_as_double = rGeo.get_point_as_doubles(xyz_point)
            inner_loop_points.append(point_as_double)
        inner_loops.append(inner_loop_points)
    data_geometry.outer_loop = outer_loop
    data_geometry.inner_loops = inner_loops
    # add coordinate system translation and rotation data
    (
        data_geometry.rotation_coord,
        data_geometry.translation_coord,
    ) = rGeo.get_coordinate_system_translation_and_rotation(doc)
    return data_geometry


def convert_solid_to_flattened_2d_points(solid):
    """
    Converts a solid into a 2D polygon by projecting it onto a plane.( Removes Z values...)
    First nested list is the outer loop, any other following lists describe holes within the area of the polygon defined be points in first list.
    Arcs, circles will be tessellated to polygons.
    :param solid: A solid.
    :type solid: Autodesk.Revit.DB.Solid
    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometryPolygon`
    """

    """
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
    """

    ceilingGeos = []
    # sort faces by size
    sortedBySizeFaces = rGeo.get_faces_sorted_by_area_from_solid(solid)
    # get all faces which are horizontal only
    horizontalFaces = rGeo.get_unique_horizontal_faces(sortedBySizeFaces)
    # loop of all horizontal faces and extract loops
    for hf in horizontalFaces:
        edgeLoops = rGeo.convert_edge_arrays_into_list_of_points(hf.EdgeLoops)
        # convert in UV coordinates
        edgeLoopsFlattened = rGeo.flatten_xyz_point_list_of_lists(edgeLoops)
        # set up a named tuple to store data in it
        uvLoops = []
        uvLoop = namedtuple("uvLoop", "loop area id threeDPoly")
        counter = 0
        for edgeLoopFlat in edgeLoopsFlattened:
            areaLoop = rGeo.get_signed_polygon_area(edgeLoopFlat)
            uvTuple = uvLoop(edgeLoopFlat, abs(areaLoop), counter, edgeLoops[counter])
            uvLoops.append(uvTuple)
            counter += 1
        uvLoops = sorted(uvLoops, key=lambda x: x.area, reverse=True)
        # sort loops into exterior and hole loops
        loopDic = rGeo.build_loops_dictionary(uvLoops)
        for key in loopDic:
            dataGeometry = dGeometryPoly.DataPolygon()
            keyList = []
            # find matching loop by id
            for x in uvLoops:
                if x.id == key:
                    keyList = x
                    break
            dataGeometry.outer_loop = keyList.threeDPoly
            if len(loopDic[key]) > 0:
                for hole in loopDic[key]:
                    dataGeometry.inner_loops.append(hole.threeDPoly)
            else:
                dataGeometry.inner_loops = []
            ceilingGeos.append(dataGeometry)
    return ceilingGeos
