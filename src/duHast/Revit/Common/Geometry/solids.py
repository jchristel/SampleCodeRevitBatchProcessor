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


import Autodesk.Revit.DB as rdb
from duHast.Data.Objects.Properties.Geometry import from_revit_conversion as rCon


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
    opt = rdb.Options()
    fr1_geom = element.get_Geometry(opt)
    solids = []
    # check geometry for Solid elements
    # todo check for FamilyInstance geometry ( in place families!)
    for item in fr1_geom:
        if type(item) is rdb.Solid:
            solids.append(item)

    # process solids to points
    # in place families may have more then one solid
    for s in solids:
        points_per_solid = rCon.convert_solid_to_flattened_2d_points(s)
        if len(points_per_solid) > 0:
            for points_lists in points_per_solid:
                all_element_points.append(points_lists)
    return all_element_points
