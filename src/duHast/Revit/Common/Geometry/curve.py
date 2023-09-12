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

from Autodesk.Revit.DB import Arc, Line

from duHast.Revit.Common.Geometry.geometry import is_close
from duHast.Utilities.Objects import result as res


def check_curve_is_within_curve(curve_one, curve_two):
    """
    checks whether one curve ( can be an arc or a line) is completely within the other
    returns:

    - Curve One if curves are identical,
    - the curve which is completely within the other curve
    - None if neither of the above applies
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


def calculate_shortened_curve_geometry(curve_one, curve_two):
    """
    Two options when lines are overlapping:

    - extend the longer line to the end of the shorter line not overlapping and delete the shorter line or
    - shorten shorter line to move the endpoint currently overlapping to the end point of the longer line, therefore removing the overlap

    First option will room separation lines

    returns two values: first one is the curve to change in length, second one is the curve to delete!
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
    is_shorter_curve_end_zero_in_longer_curve = is_close(
        distance_shorter_curve_end_zero_to_longer_curve, 0.000, 0.000
    )
    is_shorter_curve_end_one_in_longer_curve = is_close(
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
    is_longer_curve_end_zero_in_shorter_curve = is_close(
        distance_longer_curve_end_zero_to_shorter_curve, 0.000, 0.000
    )
    is_longer_curve_end_one_in_shorter_curve = is_close(
        distance_longer_curve_end_one_to_shorter_curve, 0.000, 0.000
    )

    # determine the start and end point of the longer curve
    # TODO: trying to avoid to flip start at end point!
    new_point = None
    start_point = None
    end_point = None
    # check which point of the shorter curve is not on the longer curve ( new end point )
    if is_shorter_curve_end_zero_in_longer_curve:
        # one end of shorter curve is outside the longer curve
        end_point = shorter_curve.curve.GetEndPoint(1)
    elif is_shorter_curve_end_one_in_longer_curve:
        # zero end of shorter curve is outside the longer curve
        end_point = shorter_curve.curve.GetEndPoint(0)
    else:
        raise ValueError(
            "Neither end point of {} is on {}".format(shorter_curve.id, longer_curve.id)
        )

    # check which point of the longer curve is not on the shorter curve ( new start point )
    if is_longer_curve_end_zero_in_shorter_curve:
        # point at end 1 is not one shorter curve
        start_point = longer_curve.curve.GetEndPoint(1)
    elif is_longer_curve_end_one_in_shorter_curve:
        # point at end 0 is not one shorter curve
        start_point = longer_curve.curve.GetEndPoint(0)
    else:
        raise ValueError(
            "Neither end point of {} is on {}".format(longer_curve.id, shorter_curve.id)
        )

    # create a new curve depending on whether this is an arc or a line
    if type(longer_curve.curve) == Line:
        longer_curve.new_curve = Line.CreateBound(start_point, end_point)
    elif type(longer_curve.curve) == Arc:
        longer_curve.new_curve = Arc.Create(
            start_point, end_point, longer_curve.curve.Centre
        )
    else:
        raise ValueError(
            "Curve type {} is not supported.".format(type(longer_curve.curve))
        )

    return longer_curve, shorter_curve


def modify_model_line_action(existing_curve, new_curve, override_joins=True):
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
