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


from Autodesk.Revit.DB import BoundingBoxXYZ, ElementId, Options, Solid
from duHast.Data.Objects.Properties.Geometry.from_revit_conversion import (
    convert_solid_to_flattened_2d_points,
)

from duHast.Revit.Common.Geometry.geometry import merge_bounding_box_xyz


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
