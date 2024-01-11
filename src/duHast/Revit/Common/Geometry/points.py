"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit points helper functions
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

from Autodesk.Revit.DB import (
    Transform,
    XYZ,
)

def rotate_point_around_z_with_origin(point, origin, angle_in_radians):
    """
    Rotates a point around the Z-axis with a given origin and angle in radians.
    Returns the rotated point.

    :param point: The point to rotate.
    :type point: Autodesk.Revit.DB.XYZ
    :param origin: The origin of the rotation.
    :type origin: Autodesk.Revit.DB.XYZ
    :param angle_in_radians: The angle in radians to rotate the point.
    :type angle_in_radians: float

    :return: The rotated point.
    :rtype: Autodesk.Revit.DB.XYZ
    """

    #return point unchanged if angle is 0
    if angle_in_radians == 0:
        return point
    
    # get the axis of rotation
    rotation_axis = XYZ.BasisZ
    # Create a rotation transform around the Z-axis
    rotation_transform = Transform.CreateRotationAtPoint(rotation_axis, angle_in_radians, origin)

    # Apply the rotation transform to the point
    rotated_point = rotation_transform.OfPoint(point)

    return rotated_point