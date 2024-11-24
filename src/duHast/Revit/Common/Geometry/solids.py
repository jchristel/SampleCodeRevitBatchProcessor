"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit solids helper functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from collections import namedtuple

from Autodesk.Revit.DB import BoundingBoxXYZ, ElementId, Options, Solid

from duHast.Revit.Common.Geometry.geometry import merge_bounding_box_xyz, get_faces_sorted_by_area_from_solid, get_unique_horizontal_faces, convert_edge_arrays_into_list_of_points,flatten_xyz_point_list_of_lists,get_signed_polygon_area,build_loops_dictionary
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_polygon_2 as dGeometryPoly


def get_2d_points_from_solid(element):
    """
    Returns a list of lists of data geometry instances representing the flattened (2D geometry) of the Element
    List of Lists because an element can be made up of multiple solids. Each nested list represents one element solid.
    Does not work with in place elements.

    :param element: A revit element instance.
    :type element: Autodesk.Revit.DB.Element

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    """

    all_element_points = []
    # get geometry from element
    opt = Options()
    fr1_geom = element.get_Geometry(opt)
    solids = []
    # check geometry for Solid elements
    # todo check for FamilyInstance geometry ( in place families!)
    for item in fr1_geom:
        if type(item) is Solid:
            solids.append(item)

    # process solids to points
    # in place families may have more then one solid
    for s in solids:
        points_per_solid = convert_solid_to_flattened_2d_points(s)
        if len(points_per_solid) > 0:
            for points_lists in points_per_solid:
                all_element_points.append(points_lists)
    return all_element_points


def get_solid_bounding_box(solid):
    """
    Returns a bounding box from a solid.

    :param solid: The solid to get the bounding box from.
    :type solid: Autodesk.Revit.DB.Solid

    :return: The bounding box of the solid.
    :rtype: Autodesk.Revit.DB.BoundingBoxXYZ
    """

    # get the solids bounding box
    solid_bounding_box = solid.GetBoundingBox()

    # transform the bounding box to the solids transform
    # which is different from the family instance transform!!
    solid_transform_min = solid_bounding_box.Transform.OfPoint(solid_bounding_box.Min)
    solid_transform_max = solid_bounding_box.Transform.OfPoint(solid_bounding_box.Max)

    # create a new bounding box from the transformed points
    solid_transform_bb = BoundingBoxXYZ()
    solid_transform_bb.Min = solid_transform_min
    solid_transform_bb.Max = solid_transform_max

    return solid_transform_bb


def get_bounding_box_from_family_geometry(geometry_element):
    """
    Returns a bounding box from the families solid elements geometry only.
    This is different from the family instance bounding box!

    :param geometry_element: The geometry element of a family instance.
    :type geometry_element: Autodesk.Revit.DB.GeometryElement

    :return: The bounding box of the family geometry.
    :rtype: Autodesk.Revit.DB.BoundingBoxXYZ
    """

    merged_result = None
    for geometry_obj in geometry_element:
        if geometry_obj is not None:
            # Instance geometry can also be a Solid
            if isinstance(geometry_obj, Solid):
                return get_solid_bounding_box(instance_geometry)
            # If not a solid, it is a list of geometry objects
            instance_geometry = geometry_obj.GetInstanceGeometry()
            if instance_geometry is not None:
                for element in instance_geometry:
                    # find solids
                    if type(element) is Solid:
                        # check if solid is valid
                        if element.Id == ElementId.InvalidElementId.IntegerValue:
                            continue
                        # get the solids bounding box
                        solid_transform_bb = get_solid_bounding_box(element)

                        # check if this is the first bounding box
                        if merged_result == None:
                            merged_result = solid_transform_bb
                            continue

                        # merge the bounding boxes
                        merged_result = merge_bounding_box_xyz(
                            merged_result, solid_transform_bb
                        )

    # return the merged bounding box
    return merged_result

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
    sortedBySizeFaces = get_faces_sorted_by_area_from_solid(solid)
    # get all faces which are horizontal only
    horizontalFaces = get_unique_horizontal_faces(sortedBySizeFaces)
    # loop of all horizontal faces and extract loops
    for hf in horizontalFaces:
        edgeLoops = convert_edge_arrays_into_list_of_points(hf.EdgeLoops)
        # convert in UV coordinates
        edgeLoopsFlattened = flatten_xyz_point_list_of_lists(edgeLoops)
        # set up a named tuple to store data in it
        uvLoops = []
        uvLoop = namedtuple("uvLoop", "loop area id threeDPoly")
        counter = 0
        for edgeLoopFlat in edgeLoopsFlattened:
            areaLoop = get_signed_polygon_area(edgeLoopFlat)
            uvTuple = uvLoop(edgeLoopFlat, abs(areaLoop), counter, edgeLoops[counter])
            uvLoops.append(uvTuple)
            counter += 1
        uvLoops = sorted(uvLoops, key=lambda x: x.area, reverse=True)
        # sort loops into exterior and hole loops
        loopDic = build_loops_dictionary(uvLoops)
        for key in loopDic:
            dataGeometry = dGeometryPoly.DataGeometryPolygon2()
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