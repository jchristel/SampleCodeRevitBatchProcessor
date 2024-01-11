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
            instance_geometry = geometry_obj.GetInstanceGeometry()
            if instance_geometry is not None:
                for element in instance_geometry:
                    # find solids
                    if type(element) is Solid:
                        # check if solid is valid
                        if element.Id == ElementId.InvalidElementId.IntegerValue:
                            continue
                        # get the solids bounding box
                        solid_bounding_box = element.GetBoundingBox()

                        # transform the bounding box to the solids transform
                        # which is different from the family instance transform!!
                        solid_transform_min = solid_bounding_box.Transform.OfPoint(
                            solid_bounding_box.Min
                        )
                        solid_transform_max = solid_bounding_box.Transform.OfPoint(
                            solid_bounding_box.Max
                        )

                        # create a new bounding box from the transformed points
                        solid_transform_bb = BoundingBoxXYZ()
                        solid_transform_bb.Min = solid_transform_min
                        solid_transform_bb.Max = solid_transform_max

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
