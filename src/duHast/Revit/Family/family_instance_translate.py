"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit family instance translation functions.
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


from math import pi

# class used for stats reporting
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import Element, ElementTransformUtils, Line,  LocationPoint, Transaction, XYZ

# Constants
RADIAN_ANGLE_45DEGREES = pi / 4
RADIAN_ANGLE_90DEGREES = pi / 2


def get_family_location_point(element):
    """
    Returns the location point of the family instance.

    :param element: The family instance to get the location point of.
    :type element: Autodesk.Revit.DB.FamilyInstance
    :return: The location point of the family instance.
    :rtype: Autodesk.Revit.DB.XYZ
    """

    if element is not None and element.Location is not None:
        location_point = element.Location
        if isinstance(location_point, LocationPoint):
            return location_point.Point
    return None


def get_element_location_curve(element):
    """
    Returns the location curve of the element.

    :param element: The element to get the location curve of.
    :type element: Autodesk.Revit.DB.Element
    :return: The location curve of the element.
    :rtype: Autodesk.Revit.DB.Curve
    """

    location_curve = None

    if element.Location is not None:
        location_curve = element.Location.Curve

    return location_curve


def rotate_around_transform_origin(element, angle, transaction_manager =None):
    """
    Rotates an element around its origin.

    :param element: The element to rotate.
    :type element: Autodesk.Revit.DB.Element
    :param angle: The angle to rotate the element by in radians.
    :type angle: float
    """

    return_value = res.Result()

    # Get the element's transform
    transform = element.GetTotalTransform()

    # Create a line from the transform's origin and basis Z
    line = Line.CreateUnbound(transform.Origin, transform.BasisZ)

    try:
        def action():
            try:
                action_return_value = res.Result()
                ElementTransformUtils.RotateElement(element.Document, element.Id, line, angle)
                return_value.append_message( "Element rotated around origin.") 
            except Exception as e:
                action_return_value.update_sep(False, "Failed to rotate element around origin. {}".format(e))
            return action_return_value
       
        if transaction_manager is None:
            # assume there is an transaction already going on
            return_value = action()
        else:
            # create a transaction
            transaction = Transaction(element.Document, "rotated element around origin: {}".format(Element.Name.GetValue(element)))
            return_value = in_transaction(transaction, action)

    except Exception as e:
        return_value.update_sep(False, "Failed to rotate element around origin. {}".format(e))


    return return_value


def rotate_around_origin(element, angle, transaction_manager =None):
    """
    Rotates an element around its origin.

    :param element: The element to rotate.
    :type element: Autodesk.Revit.DB.Element
    :param angle: The angle to rotate the element by in radians.
    :type angle: float
    """

    return_value = res.Result()

    # get the family location point
    location_point = get_family_location_point(element)

    # Create a line from the transform's origin and basis Z
    line = Line.CreateBound(location_point, XYZ(location_point.X, location_point.Y,  location_point.Z +1000))

    try:
        def action():
            try:
                action_return_value = res.Result()
                ElementTransformUtils.RotateElement(element.Document, element.Id, line, angle)
                return_value.append_message( "Element rotated around origin.") 
            except Exception as e:
                action_return_value.update_sep(False, "Failed to rotate element around origin. {}".format(e))
            return action_return_value
       
        if transaction_manager is None:
            # assume there is an transaction already going on
            return_value = action()
        else:
            # create a transaction
            transaction = Transaction(element.Document, "rotated element around origin: {}".format(Element.Name.GetValue(element)))
            return_value = transaction_manager(transaction, action)

    except Exception as e:
        return_value.update_sep(False, "Failed to rotate element around origin. {}".format(e))


    return return_value


def move_from_point_to_point(element, start_point, end_point, transaction_manager =None):
    """
    Moves an element from a start point to an end point. (assume same Z value)

    :param element: The element to move.
    :type element: Autodesk.Revit.DB.Element
    :param start_point: The start point of the move.
    :type start_point: Autodesk.Revit.DB.XYZ
    :param end_point: The end point of the move.
    :type end_point: Autodesk.Revit.DB.XYZ
    """

    return_value = res.Result()

    try:
        def action():
            try:
                action_return_value = res.Result()
                ElementTransformUtils.MoveElement(element.Document, element.Id, end_point - start_point)
                return_value.append_message( "Element moved from point to point.") 
            except Exception as e:
                action_return_value.update_sep(False, "Failed to move element from point to point. {}".format(e))
            return action_return_value
       
        if transaction_manager is None:
            # assume there is an transaction already going on
            return_value = action()
        else:
            # create a transaction
            transaction = Transaction(element.Document, "moved element from point to point: {}".format(Element.Name.GetValue(element)))
            return_value = transaction_manager(transaction, action)

    except Exception as e:
        return_value.update_sep(False, "Failed to move element from point to point. {}".format(e))

    return return_value