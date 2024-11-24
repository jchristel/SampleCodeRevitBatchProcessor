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

from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_polygon_2 as dGeometryPoly
from duHast.Geometry.bounding_box_2 import BoundingBox2
from duHast.Geometry.point_2 import Point2
from duHast.Revit.Common.Geometry import geometry as rGeo, solids as rSolid
from duHast.Revit.Common.Geometry.points import get_point_as_doubles
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

from Autodesk.Revit.DB import XYZ


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

    data_geometry = dGeometryPoly.DataGeometryPolygon2()
    outer_loop = []
    for xyz_point in dgObject.outer_loop:
        point_as_double = get_point_as_doubles(xyz_point)
        outer_loop.append(point_as_double)
    inner_loops = []
    for inner_loop in dgObject.inner_loops:
        inner_loop_points = []
        for xyz_point in inner_loop:
            point_as_double = get_point_as_doubles(xyz_point)
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


def convert_bounding_box_to_flattened_2d_points(bounding_box):
    """
    Converts a bounding box into a 2D polygon by projecting it onto a plane.( Removes Z values...)
    :param bounding_box: A bounding box.
    :type bounding_box: Autodesk.Revit.DB.BoundingBoxXYZ
    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometryPolygon`
    """
    # get points from bounding box and project them onto a plane ( Z value of bounding box min point)
    bounding_box_points = [
        bounding_box.Min,
        XYZ(bounding_box.Max.X, bounding_box.Min.Y, bounding_box.Min.Z),
        XYZ(bounding_box.Max.X, bounding_box.Max.Y, bounding_box.Min.Z),
        XYZ(bounding_box.Min.X, bounding_box.Max.Y, bounding_box.Min.Z),
    ]
    # set up data class object and store points in outer loop property
    dataGeometry = dGeometryPoly.DataGeometryPolygon2()
    dataGeometry.outer_loop = bounding_box_points
    return dataGeometry


def get_2d_points_from_revit_element_type_in_model(doc, element_instance_getter):
    """
    Returns a list of lists of points representing the flattened(2D geometry) of the elements
    List of Lists because a elements can be made up of multiple solids. Each nested list represents one solid within the elements geometry.
    Does not work with in place elements.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_instance_getter: Function returning all element instances of a particular category in the model as an element collector
    :type element_instance_getter: func(doc)

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    """

    element_instances = element_instance_getter(doc)
    all_element_points = []
    for element_instance in element_instances:
        element_points = rSolid.get_2d_points_from_solid(element_instance)
        if len(element_points) > 0:
            all_element_points.append(element_points)
    return all_element_points


def convert_revit_bounding_box_to_geometry2_bounding_box(bounding_box):
    
    point1 = Point2(
        x=convert_imperial_feet_to_metric_mm(bounding_box.Min.X),
        y=convert_imperial_feet_to_metric_mm(bounding_box.Min.Y),
    )
    point2 = Point2(
        x=convert_imperial_feet_to_metric_mm(bounding_box.Max.X),
        y=convert_imperial_feet_to_metric_mm(bounding_box.Max.Y),
    )
    bbox = BoundingBox2(point1=point1, point2=point2)
    return bbox
