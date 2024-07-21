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

from Autodesk.Revit.DB import (
    Transform,
    UV,
    XYZ,
)
from duHast.Utilities.compare import is_close


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

    # return point unchanged if angle is 0
    if angle_in_radians == 0:
        return point

    # get the axis of rotation
    rotation_axis = XYZ.BasisZ
    # Create a rotation transform around the Z-axis
    rotation_transform = Transform.CreateRotationAtPoint(
        rotation_axis, angle_in_radians, origin
    )

    # Apply the rotation transform to the point
    rotated_point = rotation_transform.OfPoint(point)

    return rotated_point


def transform_point_by_elem_transform(pt, transform):
    """
    Transforms a point by an element transform
    :param pt: The point to transform
    :type pt: XYZ
    :param transform: The transform to use
    :type transform: Transform
    :return: The transformed point
    :rtype: XYZ
    """

    x = pt.X
    y = pt.Y
    z = pt.Z

    b0 = transform.get_Basis(0)
    b1 = transform.get_Basis(1)
    b2 = transform.get_Basis(2)
    origin = transform.Origin

    x_new = x * b0.X + y * b1.X + z * b2.X + origin.X
    y_new = x * b0.Y + y * b1.Y + z * b2.Y + origin.Y
    z_new = x * b0.Z + y * b1.Z + z * b2.Z + origin.Z

    return XYZ(x_new, y_new, z_new)


def sort_points_by_min_and_max(min_pt, max_pt):
    """
    Takes BoundingBox or Outline Min and Max points and
    returns the true Min and Max points. This is to ensure
    no zero thickness geometries are created.
    :param min_pt: The minimum point
    :type min_pt: XYZ
    :param max_pt: The maximum point
    :type max_pt: XYZ
    :return: The sorted points
    :rtype: tuple
    """
    min_x = min_pt.X
    min_y = min_pt.Y
    min_z = min_pt.Z

    max_x = max_pt.X
    max_y = max_pt.Y
    max_z = max_pt.Z

    smin_x = min(min_x, max_x)
    smin_y = min(min_y, max_y)
    smax_x = max(min_x, max_x)
    smax_y = max(min_y, max_y)

    return (XYZ(smin_x, smin_y, min_z), XYZ(smax_x, smax_y, max_z))


def get_point_as_doubles(point, include_z=False):
    """
    Converts a revit XYZ to a list of doubles in order x,y,z.

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: List of doubles in order of x,y,z
    :rtype: list double
    """
    if include_z:
        return [point.X, point.Y, point.Z]
    else:
        return [point.X, point.Y]


def get_doubles_as_xyz(doubles, include_z=False):
    """
    Converts a list of doubles to a revit XYZ.

    :param doubles: List of doubles in order of x,y,z
    :type doubles: list double

    :return: A revit point.
    :rtype: Autodesk.Revit.DB.XYZ
    """
    if include_z:
        return XYZ(doubles[0], doubles[1], doubles[2])
    else:
        return XYZ(doubles[0], doubles[1], 0)


def get_rotation_around_z_as_xyz(doubles):
    """
    Converts a list of doubles to a revit XYZ.
    The first two doubles are the x,y coordinates of the point.
    The third double is the z coordinate of the point to which 1 is added.

    :param doubles: List of doubles in order of x,y,z
    :type doubles: list double

    :return: A revit point.
    :rtype: Autodesk.Revit.DB.XYZ
    """

    return XYZ(doubles[0], doubles[1], doubles[2] + 1)


def flatten_xyz_point(point):
    """
    Flattens a XYZ point to a UV by omitting the Z value of the XYZ.

    https://thebuildingcoder.typepad.com/blog/2008/12/2d-polygon-areas-and-outer-loop.html

    :param point: A revit point.
    :type point: Autodesk.Revit.DB.XYZ

    :return: A 2D point (UV)
    :rtype:  Autodesk.Revit.DB.UV
    """

    return UV(point.X, point.Y)


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


def on_which_side_of_line_is_point(line, point):
    """
    If d<0 then the point lies on one side of the line, and if d>0 then it lies on the other side.
    If d=0 then the point lies exactly line.

    Refer https://math.stackexchange.com/questions/274712/calculate-on-which-side-of-a-straight-line-is-a-given-point-located

    :param line: Line to check which side a point is on.
    :type line: Autodesk.Revit.DB.Line
    :param point: The point to check;
    :type point: Autodesk.Revit.DB.XYZ

    :return: double
    :rtype: double
    """

    d = (point.X - line.GetEndPoint(0).X) * (
        line.GetEndPoint(1).Y - line.GetEndPoint(0).Y
    ) - (point.Y - line.GetEndPoint(0).Y) * (
        line.GetEndPoint(1).X - line.GetEndPoint(0).X
    )
    return d


def distance_between_two_points(p1, p2):
    """
    Returns the distance between two points.

    :param p1: First point.
    :type p1: Autodesk.Revit.DB.XYZ
    :param p2: Second point.
    :type p2: Autodesk.Revit.DB.XYZ
    :return: The distance between points
    :rtype: double
    """
    return p1.DistanceTo(p2)


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
