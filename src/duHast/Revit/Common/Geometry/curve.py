"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit curve helper functions
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

import math

from Autodesk.Revit.DB import Arc, ElementId, Line, ModelCurve, Transform, XYZ

from duHast.Utilities.compare import is_close
from duHast.Utilities.Objects import result as res


def is_curve_is_within_curve(curve_one, curve_two):
    """
    Checks whether one curve is completely within another curve.

    Args:
        curve_one: The first curve to compare (can be an arc or a line).
        curve_two: The second curve to compare (can be an arc or a line).

    Returns:
        The curve that is completely within the other curve, or None if the curves are overlapping.

    Example Usage:
        curve_one = ...
        curve_two = ...
        result = check_curve_is_within_curve(curve_one, curve_two)
        print(result)

        Output:
        - If the curves are identical, it will return curve_one.
        - If curve_two is completely within curve_one, it will return curve_two.
        - If curve_one is completely within curve_two, it will return curve_one.
        - If the curves are overlapping, it will return None.
    """

    curve_one_end_zero_point = curve_one.curve.GetEndPoint(0)
    curve_one_end_one_point = curve_one.curve.GetEndPoint(1)
    curve_two_end_zero_point = curve_two.curve.GetEndPoint(0)
    curve_two_end_one_point = curve_two.curve.GetEndPoint(1)

    # distance of close to zero indicates point is on line!
    distance_one_end_zero_to_two = round(
        curve_two.curve.Distance(curve_one_end_zero_point), 4
    )
    distance_one_end_one_to_two = round(
        curve_two.curve.Distance(curve_one_end_one_point), 4
    )
    distance_two_end_zero_to_one = round(
        curve_one.curve.Distance(curve_two_end_zero_point), 4
    )
    distance_two_end_one_to_one = round(
        curve_one.curve.Distance(curve_two_end_one_point), 4
    )

    # possible out comes:
    # curves are equal in length and location ( all 4 tests return true )
    # one curve is fully inside another ( 1 pair test result is false, the other pair is true )
    # curves are overlapping ( both pairs return false )

    if (
        is_close(distance_one_end_zero_to_two, 0.000, 0.000)
        and is_close(distance_one_end_one_to_two, 0.000, 0.000)
        and is_close(distance_two_end_zero_to_one, 0.000, 0.000)
        and is_close(distance_two_end_one_to_one, 0.000, 0.000)
    ):
        # curves are identical
        return curve_one
    elif is_close(distance_two_end_zero_to_one, 0.000, 0.000) and is_close(
        distance_two_end_one_to_one, 0.000, 0.000
    ):
        # curve two is completely within curve one
        return curve_two
    elif is_close(distance_one_end_zero_to_two, 0.000, 0.000) and is_close(
        distance_one_end_one_to_two, 0.000, 0.000
    ):
        # curve one is completely within curve two
        return curve_one
    else:
        # curves are overlapping
        return None


def calculate_lengthened_curve_geometry(curve_one, curve_two):
    """
    Two options when lines are overlapping:

    - extend the longer line to the end of the shorter line not overlapping and delete the shorter line or
    - shorten shorter line to move the endpoint currently overlapping to the end point of the longer line, therefore removing the overlap

    First option will shorten number of room separation lines in model. However when multiple lines overlap a single long line this
    code will delete a shorter overlapping line still required!

    returns two values: first one is the curve to change in length, second one is the curve to delete!
    """

    # check first if this is a complete overlap (couldn't fixed in step one since smaller line is in group...)
    # if so dont make any changes here...
    check_complete_overlap = is_curve_is_within_curve(curve_one, curve_two)
    if check_complete_overlap == None:
        # which curve is the longer curve?
        # assume default
        longer_curve = curve_two
        shorter_curve = curve_one
        # check default was correct?
        if curve_one.curve.ApproximateLength > curve_two.curve.ApproximateLength:
            longer_curve = curve_one
            shorter_curve = curve_two

        # find the endpoint of the shorter line which is not within the longer line
        shorter_curve_end_zero = shorter_curve.curve.GetEndPoint(0)
        shorter_curve_end_one = shorter_curve.curve.GetEndPoint(1)

        # measure distance to other curve. Due to precision issues these
        # values are rounded. A distance of 0 indicates point is on curve
        distance_shorter_curve_end_zero_to_longer_curve = round(
            longer_curve.curve.Distance(shorter_curve_end_zero), 4
        )
        distance_shorter_end_one_to_longer_curve = round(
            longer_curve.curve.Distance(shorter_curve_end_one), 4
        )

        # check which end of the shorter curve is outside the longer curve
        is_shorter_curve_end_zero_on_longer_curve = is_close(
            distance_shorter_curve_end_zero_to_longer_curve, 0.000, 0.000
        )
        is_shorter_curve_end_one_on_longer_curve = is_close(
            distance_shorter_end_one_to_longer_curve, 0.000, 0.000
        )

        # check which end of the longer curve is outside the shorter curve ( that end will stay unchanged )
        # find the endpoint of the shorter line which is not within the longer line
        longer_curve_end_zero = longer_curve.curve.GetEndPoint(0)
        longer_curve_end_one = longer_curve.curve.GetEndPoint(1)

        # measure distance to other curve. Due to precision issues these
        # values are rounded. A distance of 0 indicates point is on curve
        distance_longer_curve_end_zero_to_shorter_curve = round(
            shorter_curve.curve.Distance(longer_curve_end_zero), 4
        )
        distance_longer_curve_end_one_to_shorter_curve = round(
            shorter_curve.curve.Distance(longer_curve_end_one), 4
        )

        # check which end of the longer curve is outside the shorter curve
        is_longer_curve_end_zero_on_shorter_curve = is_close(
            distance_longer_curve_end_zero_to_shorter_curve, 0.000, 0.000
        )
        is_longer_curve_end_one_on_shorter_curve = is_close(
            distance_longer_curve_end_one_to_shorter_curve, 0.000, 0.000
        )

        # determine the start and end point of the longer curve
        point_zero = None
        point_one = None
        # check which point of the shorter curve is not on the longer curve ( new end point )
        if is_shorter_curve_end_zero_on_longer_curve:
            # one end of shorter curve is outside the longer curve
            point_one = shorter_curve.curve.GetEndPoint(1)
        elif is_shorter_curve_end_one_on_longer_curve:
            # zero end of shorter curve is outside the longer curve
            point_one = shorter_curve.curve.GetEndPoint(0)
        else:
            raise ValueError(
                "Neither end point of shorter curve {} is on longer curve {}. That is impossible since that would mean curves are not overlapping...at all.\nDistance shorter curve end point zero to longer curve: {}\nDistance shorter curve end point one to longer curve: {}".format(
                    shorter_curve.id,
                    longer_curve.id,
                    distance_shorter_curve_end_zero_to_longer_curve,
                    distance_shorter_end_one_to_longer_curve,
                )
            )

        # check which point of the longer curve is not on the shorter curve ( new start point )
        if is_longer_curve_end_zero_on_shorter_curve:
            # point at end 1 is not one shorter curve
            point_zero = longer_curve.curve.GetEndPoint(1)
        elif is_longer_curve_end_one_on_shorter_curve:
            # point at end 0 is not one shorter curve
            point_zero = longer_curve.curve.GetEndPoint(0)
        else:
            raise ValueError(
                "Neither end point of longer curve {} is on shorter curve {}.\n This indicates the longer curve is completely overlapping the shorter curve. \nDistance longer curve end point zero to shorter curve: {}\nDistance longer curve end point one to shorter curve: {}\nDistance shorter curve end point zero to longer curve: {}\nDistance shorter curve end point one to longer curve: {}".format(
                    longer_curve.id,
                    shorter_curve.id,
                    distance_longer_curve_end_zero_to_shorter_curve,
                    distance_longer_curve_end_one_to_shorter_curve,
                    distance_shorter_curve_end_zero_to_longer_curve,
                    distance_shorter_end_one_to_longer_curve,
                )
            )

        new_point_zero = None
        new_point_one = None
        # trying to avoid to flip start at end point of the line, since this may cause the rooms to moveI(!?)
        if longer_curve.curve.GetEndPoint(0).IsAlmostEqualTo(point_zero):
            # assign the same end point for 0 index
            new_point_zero = longer_curve.curve.GetEndPoint(0)
            # assign a new end point for 1 index
            new_point_one = point_one
        elif longer_curve.curve.GetEndPoint(0).IsAlmostEqualTo(point_one):
            # assign the same end point for 0 index
            new_point_zero = longer_curve.curve.GetEndPoint(0)
            # assign a new end point for 1 index
            new_point_one = point_zero
        elif longer_curve.curve.GetEndPoint(1).IsAlmostEqualTo(point_zero):
            # assign a new end point for 0 index
            new_point_zero = point_one
            # assign the same end point for 1 index
            new_point_one = longer_curve.curve.GetEndPoint(1)
        else:
            # assign a new end point for 0 index
            new_point_zero = point_zero
            # assign the same end point for 1 index
            new_point_one = longer_curve.curve.GetEndPoint(1)

        # check for to short lines:
        # Aborted with exception: Curve length is too small for Revit's tolerance (as identified by Application.ShortCurveTolerance).

        # create a new curve depending on whether this is an arc or a line
        if type(longer_curve.curve) == Line:
            try:
                longer_curve.new_curve = Line.CreateBound(new_point_zero, new_point_one)
            except Exception as e:
                print(
                    "new line curve: {} points: 0: {} 1: {} with exception: {}".format(
                        longer_curve.id, new_point_zero, new_point_one, e
                    )
                )
        elif type(longer_curve.curve) == Arc:
            try:
                longer_curve.new_curve = Arc.Create(
                    new_point_zero, new_point_one, longer_curve.curve.Center
                )
            except Exception as e:
                print(
                    "new arc curve: {} points: 0: {} 1: {} C: {} with exception: {}".format(
                        longer_curve.id,
                        new_point_zero,
                        new_point_one,
                        longer_curve.curve.Center,
                        e,
                    )
                )
        else:
            raise ValueError(
                "Curve type {} is not supported.".format(type(longer_curve.curve))
            )

        return longer_curve, shorter_curve
    else:
        return None, None


def calculate_shortened_curve_geometry(curve_one, curve_two):
    """
    Two options when lines are overlapping:

    - extend the longer line to the end of the shorter line not overlapping and delete the shorter line or
    - shorten shorter line to move the endpoint currently overlapping to the end point of the longer line, therefore removing the overlap

    This is an attempt on option 2

    returns the curve of which to change the length!
    """
    # which curve is the longer curve?
    # assume default
    longer_curve = curve_two
    shorter_curve = curve_one
    # check default was correct?
    if curve_one.curve.ApproximateLength > curve_two.curve.ApproximateLength:
        longer_curve = curve_one
        shorter_curve = curve_two

    # find the endpoint of the shorter line which is not within the longer line
    shorter_curve_end_zero = shorter_curve.curve.GetEndPoint(0)
    shorter_curve_end_one = shorter_curve.curve.GetEndPoint(1)

    # measure distance to other curve. Due to precision issues these
    # values are rounded. A distance of 0 indicates point is on curve
    distance_shorter_curve_end_zero_to_longer_curve = round(
        longer_curve.curve.Distance(shorter_curve_end_zero), 4
    )
    distance_shorter_end_one_to_longer_curve = round(
        longer_curve.curve.Distance(shorter_curve_end_one), 4
    )

    # check which end of the shorter curve is outside the longer curve
    is_shorter_curve_end_zero_on_longer_curve = is_close(
        distance_shorter_curve_end_zero_to_longer_curve, 0.000, 0.000
    )
    is_shorter_curve_end_one_on_longer_curve = is_close(
        distance_shorter_end_one_to_longer_curve, 0.000, 0.000
    )

    # check which end of the longer curve is outside the shorter curve ( that end will stay unchanged )
    # find the endpoint of the shorter line which is not within the longer line
    longer_curve_end_zero = longer_curve.curve.GetEndPoint(0)
    longer_curve_end_one = longer_curve.curve.GetEndPoint(1)

    # measure distance to other curve. Due to precision issues these
    # values are rounded. A distance of 0 indicates point is on curve
    distance_longer_curve_end_zero_to_shorter_curve = round(
        shorter_curve.curve.Distance(longer_curve_end_zero), 4
    )
    distance_longer_curve_end_one_to_shorter_curve = round(
        shorter_curve.curve.Distance(longer_curve_end_one), 4
    )

    # check which end of the longer curve is outside the shorter curve
    is_longer_curve_end_zero_on_shorter_curve = is_close(
        distance_longer_curve_end_zero_to_shorter_curve, 0.000, 0.000
    )
    is_longer_curve_end_one_on_shorter_curve = is_close(
        distance_longer_curve_end_one_to_shorter_curve, 0.000, 0.000
    )

    # determine the start and end point of the shorter curve
    point_zero = None
    point_one = None
    # check which point of the longer curve is on the shorter curve ( new end point )
    if is_longer_curve_end_zero_on_shorter_curve:
        # one end of longer curve is on the shorter curve
        point_one = longer_curve.curve.GetEndPoint(0)
    elif is_longer_curve_end_one_on_shorter_curve:
        # zero end of longer curve is on the shorter curve
        point_one = longer_curve.curve.GetEndPoint(1)
    else:
        raise ValueError(
            "Neither end point of {} is on {}".format(shorter_curve.id, longer_curve.id)
        )

    # check which point of the shorter curve is not on the longer curve ( start point to keep)
    if is_shorter_curve_end_zero_on_longer_curve:
        # point at end 1 is not one longer curve
        point_zero = shorter_curve.curve.GetEndPoint(1)
    elif is_shorter_curve_end_one_on_longer_curve:
        # point at end 0 is not one longer curve
        point_zero = shorter_curve.curve.GetEndPoint(0)
    else:
        raise ValueError(
            "Neither end point of {} is on {}".format(longer_curve.id, shorter_curve.id)
        )

    new_point_zero = None
    new_point_one = None
    # trying to avoid to flip start at end point of the line, since this may cause the rooms to moveI(!?)
    if shorter_curve.curve.GetEndPoint(0).IsAlmostEqualTo(point_zero):
        # assign the same end point for 0 index
        new_point_zero = shorter_curve.curve.GetEndPoint(0)
        # assign a new end point for 1 index
        new_point_one = point_one
    elif shorter_curve.curve.GetEndPoint(0).IsAlmostEqualTo(point_one):
        # assign the same end point for 0 index
        new_point_zero = shorter_curve.curve.GetEndPoint(0)
        # assign a new end point for 1 index
        new_point_one = point_zero
    elif shorter_curve.curve.GetEndPoint(1).IsAlmostEqualTo(point_zero):
        # assign a new end point for 0 index
        new_point_zero = point_one
        # assign the same end point for 1 index
        new_point_one = shorter_curve.curve.GetEndPoint(1)
    else:
        # assign a new end point for 0 index
        new_point_zero = point_zero
        # assign the same end point for 1 index
        new_point_one = shorter_curve.curve.GetEndPoint(1)

    # create a new curve depending on whether this is an arc or a line
    if type(shorter_curve.curve) == Line:
        shorter_curve.new_curve = Line.CreateBound(new_point_zero, new_point_one)
    elif type(shorter_curve.curve) == Arc:
        shorter_curve.new_curve = Arc.Create(
            new_point_zero, new_point_one, shorter_curve.curve.Centre
        )
    else:
        raise ValueError(
            "Curve type {} is not supported.".format(type(longer_curve.curve))
        )

    return shorter_curve


def modify_model_line_action(existing_curve, new_curve, override_joins=True):
    """
    Modify the geometry of an existing curve by setting it to a new curve.

    Args:
        existing_curve (object): The existing curve that needs to be modified.
        new_curve (object): The new curve that will replace the existing curve.
        override_joins (bool, optional): Flag to indicate whether to override the joins between adjoining model lines. Defaults to True.

    Returns:
        object: An instance of the Result class that contains information about the success or failure of the geometry modification.
    """
    return_value = res.Result()
    try:
        # make sure to set this to True, otherwise adjoining model lines will move with end points
        existing_curve.SetGeometryCurve(new_curve, override_joins)
        return_value.update_sep(
            True,
            "Successfully changed geometry of element: {}".format(existing_curve.Id),
        )
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to change geometry of element {} with exception: {}".format(
                existing_curve.Id, e
            ),
        )
    return return_value


def translate_curves_in_elevation(
    doc, original_curves, source_elevation, target_elevation
):
    return_value = res.Result()
    try:
        new_curves = doc.Application.Create.NewCurveArray()
        # work out Z translation vector
        z = target_elevation - source_elevation
        return_value.append_message(
            "new level RL: {} old level RL: {} translation z: {}".format(
                target_elevation, source_elevation, z
            )
        )
        # vector of translation
        vector_translation = XYZ(0, 0, z)
        # transformation
        tf = Transform.CreateTranslation(vector_translation)
        for sgs in original_curves:
            new_curves.Append(sgs.CreateTransformed(tf))
        return_value.append_message("Created {} mew curve(s)".format(new_curves.Size))
        return_value.result = [new_curves]
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to translate curves from elevation {} to elevation: {} with exception: {}".format(
                source_elevation, target_elevation, e
            ),
        )
    return return_value


def get_perpendicular_line_through_point(original_line, rotation_axis, rotation_point):
    """
    Returns a line rotated by 90 degree around the rotation point.

    :param original_line: The original line to be rotated
    :type original_line:  Autodesk.Revit.DB.Line
    :param rotation_point: The point to rotate around.
    :type rotation_point:  Autodesk.Revit.DB.XYZ
    :param rotation_axis: The axis around to rotate the line
    :type rotation_axis:  Autodesk.Revit.DB.XYZ

    :return: The rotated line.
    :rtype: Autodesk.Revit.DB.Line
    """

    # get a line through origin at 90 degree
    trans_form = Transform.CreateRotationAtPoint(
        rotation_axis, math.pi / 2.0, rotation_point
    )
    transformed_line = original_line.CreateTransformed(trans_form)
    return transformed_line


def get_curve_level(doc, curve):
    """
    Sorts the area lines based on their associated level names and returns a dictionary where the keys are the level names and the values are lists of area lines.

    Args:
        doc (Document): The current model document.
        area_lines (list): A list of area lines.

    Returns:
        dict: A dictionary where the keys are the level names and the values are lists of area lines.
    """

    if isinstance(curve, ModelCurve)==False:
        raise TypeError("Expect curve to be a ModelCurve instance. Got {} instead".format(type(curve)))
    
    level_id = curve.LevelId
    if(level_id==ElementId.InvalidElementId):
        return None
    level = doc.GetElement(level_id)
    return level