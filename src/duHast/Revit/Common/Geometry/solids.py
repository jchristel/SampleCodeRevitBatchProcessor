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

from Autodesk.Revit.DB import BoundingBoxXYZ, ElementId, Options, Solid, XYZ

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


def get_solids_from_geometry(geometry_element, solids=None):
    """
    Collects the solids out of a geometry element, recursing into geometry instances.

    Solids only: a geometry element also holds curves (a door family's plan swing
    arc, for instance), and including those in a bounding box measures the
    annotation rather than the object.

    :param geometry_element: The geometry element to walk.
    :type geometry_element: Autodesk.Revit.DB.GeometryElement
    :param solids: Accumulator, used when recursing.
    :type solids: list

    :return: A list of solids with a volume greater than zero.
    :rtype: list of Autodesk.Revit.DB.Solid
    """

    if solids is None:
        solids = []

    for geometry_obj in geometry_element:
        if geometry_obj is None:
            continue

        # a solid sitting directly in the element
        if isinstance(geometry_obj, Solid):
            if geometry_obj.Id == ElementId.InvalidElementId.Value:
                continue
            if geometry_obj.Volume > 0:
                solids.append(geometry_obj)
            continue

        # a geometry instance: recurse into its placed geometry. Deliberately
        # GetInstanceGeometry and not GetSymbolGeometry - the symbol version is
        # the family as authored, before its host cuts it, which measures larger
        # than the object actually in the model.
        get_instance_geometry = getattr(geometry_obj, "GetInstanceGeometry", None)
        if get_instance_geometry is None:
            continue  # a curve, a line, a mesh - nothing with a volume
        instance_geometry = get_instance_geometry()
        if instance_geometry is not None:
            get_solids_from_geometry(instance_geometry, solids)

    return solids


def get_solid_bounding_box(solid):
    """
    Returns the solid's bounding box in WORLD coordinates, axis aligned to the
    model's axes.

    Axis aligned by design, not by accident: the returned box carries an
    identity transform and its Min/Max are world coordinates, which is what
    callers comparing, merging or filtering by extents want. A solid placed at
    an angle therefore yields a box LARGER than the solid - that is the correct
    answer to "what world extents does this occupy", and the wrong one for
    "what shape is this". For the latter use
    get_oriented_bounding_box_from_family_instance, which keeps the rotation on
    the box transform.

    All EIGHT corners of the solid's own box are transformed before the world
    extents are taken. Transforming only Min and Max is not enough: they are
    opposite corners of an oriented box, so once it is rotated they are no
    longer the axis aligned extremes. That yields a box which is neither the
    oriented box nor its correct hull - too small in general, and past ninety
    degrees of rotation inverted, with the transformed "min" exceeding the
    transformed "max".

    :param solid: The solid to get the bounding box from.
    :type solid: Autodesk.Revit.DB.Solid

    :return: The world axis aligned bounding box of the solid.
    :rtype: Autodesk.Revit.DB.BoundingBoxXYZ
    """

    # get the solids bounding box
    solid_bounding_box = solid.GetBoundingBox()

    minimum = solid_bounding_box.Min
    maximum = solid_bounding_box.Max

    # the box is expressed in the solid's own coordinate system,
    # which is different from the family instance transform!
    transform = solid_bounding_box.Transform

    corners = []
    for x in (minimum.X, maximum.X):
        for y in (minimum.Y, maximum.Y):
            for z in (minimum.Z, maximum.Z):
                corners.append(transform.OfPoint(XYZ(x, y, z)))

    solid_transform_bb = BoundingBoxXYZ()
    solid_transform_bb.Min = XYZ(
        min(point.X for point in corners),
        min(point.Y for point in corners),
        min(point.Z for point in corners),
    )
    solid_transform_bb.Max = XYZ(
        max(point.X for point in corners),
        max(point.Y for point in corners),
        max(point.Z for point in corners),
    )

    return solid_transform_bb


def get_bounding_box_from_family_geometry(geometry_element):
    """
    Returns a WORLD axis aligned bounding box covering the family's SOLIDS only.

    Two things make this different from the family instance bounding box
    (Element.get_BoundingBox), and they are different kinds of difference:

    - Content. Only solids are measured. Curves and symbolic geometry - a door
      family's plan swing arc, say - are ignored, so this is tighter than
      Revit's own box on any family that draws them.
    - Orientation. This is NOT tighter. Like Revit's box it is aligned to the
      model axes, so a family placed at an angle yields a box larger than the
      family, and the rotation is not recoverable from the result. Where that
      matters use get_oriented_bounding_box_from_family_instance.

    :param geometry_element: The geometry element of a family instance.
    :type geometry_element: Autodesk.Revit.DB.GeometryElement

    :return: The world axis aligned bounding box of the family's solids, or
        None when it holds no solids.
    :rtype: Autodesk.Revit.DB.BoundingBoxXYZ
    """

    merged_result = None
    for solid in get_solids_from_geometry(geometry_element):
        merged_result = merge_bounding_box_xyz(
            merged_result, get_solid_bounding_box(solid)
        )

    # return the merged bounding box
    return merged_result


def get_oriented_bounding_box_from_family_instance(family_instance, options=None):
    """
    Returns a bounding box of a family instance's solids that KEEPS the
    instance's rotation, by measuring it in the instance's own coordinate system
    and carrying the placement on the box transform.

    The axis aligned alternative cannot be un-rotated afterwards: an axis
    aligned box of a rotated object no longer records the angle, and recovering
    it would mean solving for two extents and a rotation from two measurements -
    degenerate at forty five degrees. An object placed at an angle has to be
    measured in its own frame in the first place.

    To read the footprint back, transform the corners built from Min/Max by the
    box's Transform. Anything that only wants world extents should keep using
    get_bounding_box_from_family_geometry instead.

    :param family_instance: The family instance to measure.
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :param options: Geometry options; a default Options() is used when omitted.
    :type options: Autodesk.Revit.DB.Options

    :return: A bounding box in the instance's coordinate system, with its
        Transform set to the instance transform, or None when the instance has
        no solid geometry.
    :rtype: Autodesk.Revit.DB.BoundingBoxXYZ
    """

    geometry_element = family_instance.get_Geometry(
        options if options is not None else Options()
    )
    if geometry_element is None:
        return None

    solids = get_solids_from_geometry(geometry_element)
    if len(solids) == 0:
        # a real state rather than a failure: some families carry no 3D geometry
        return None

    transform = family_instance.GetTransform()
    # world -> instance local, so the extents below are measured along the
    # instance's own axes rather than the model's
    inverse = transform.Inverse

    minimum_x = minimum_y = minimum_z = None
    maximum_x = maximum_y = maximum_z = None

    for solid in solids:
        for edge in solid.Edges:
            for point in edge.Tessellate():
                local = inverse.OfPoint(point)
                if minimum_x is None:
                    minimum_x = maximum_x = local.X
                    minimum_y = maximum_y = local.Y
                    minimum_z = maximum_z = local.Z
                    continue
                if local.X < minimum_x:
                    minimum_x = local.X
                if local.X > maximum_x:
                    maximum_x = local.X
                if local.Y < minimum_y:
                    minimum_y = local.Y
                if local.Y > maximum_y:
                    maximum_y = local.Y
                if local.Z < minimum_z:
                    minimum_z = local.Z
                if local.Z > maximum_z:
                    maximum_z = local.Z

    if minimum_x is None:
        return None

    oriented_bounding_box = BoundingBoxXYZ()
    oriented_bounding_box.Transform = transform
    oriented_bounding_box.Min = XYZ(minimum_x, minimum_y, minimum_z)
    oriented_bounding_box.Max = XYZ(maximum_x, maximum_y, maximum_z)

    return oriented_bounding_box


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