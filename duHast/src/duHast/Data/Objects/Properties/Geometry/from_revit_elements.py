"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility function getting 2D points from element solids.
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

from duHast.Revit.Common.Geometry import solids as rSolid


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
