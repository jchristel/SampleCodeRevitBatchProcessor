"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids extend to view crop.
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

import clr

from Autodesk.Revit.DB import (
    CurveLoop,
    DatumExtentType,
    IntersectionResultArray,
    Line,
    SetComparisonResult,
    Transaction,
    Transform,
    ViewType,
    XYZ,
)

from duHast.Revit.Common import transaction as rTran
from duHast.Revit.Views import views as rView
from duHast.Utilities.Objects import result as res
from duHast.Revit.Grids.grids import get_linear_grids_in_model_by_view
from duHast.Revit.Common.Geometry.points import (
    on_which_side_of_line_is_point,
    distance_between_two_points,
)
from duHast.Revit.Common.Geometry.curve import get_perpendicular_line_through_point


""" type of views this script will work with"""
TEMPLATE_VIEW_TYPES = [ViewType.FloorPlan, ViewType.CeilingPlan, ViewType.AreaPlan]


def _check_active_view_type(view):
    """
    Checks whether the past in view is of a specific type.

    Refer global list: TEMPLATE_VIEW_TYPES

    :param view: The view.
    :type view: AutoDesk.Revit.DB.View
    :return: True if view is of a given view type, otherwise False
    :rtype: bool
    """

    if view.ViewType in TEMPLATE_VIEW_TYPES:
        return True
    else:
        return False


def _sort_projected_grid_end_points(grid, rotation_axis, projected_points):
    """
    Sorts projected grid end points.

    Checks on which side of a line perpendicular through the grid origin the projected points and the other grid end point are
    Possible outcomes:

    - all three points are smaller then 0 or all three points are greater then 0: grid 0 point is projected point closest to grid origin
    - one projected point is smaller then 0 and the other one is greater then 0: grid 0 point is point on opposite site to other grid end point
    - both projected points are on the opposite site then other grid origin point: grid 0 point is point furthest from grid origin

    :param grid: The grid to extend to the view crop.
    :type grid: Autodesk.Revit.DB.Grid
    :param rotation_axis: The axis around which to rotate the test line.
    :type rotation_axis: Autodesk.Revit.DB.XYZ
    :param projected_points: Two projected points representing the new grid extent.
    :type projected_points: [Autodesk.Revit.DB.XYZ,Autodesk.Revit.DB.XYZ]

    :return: Sorted list of points where point at index 0 represents the start point of the new grid extent and point at index 1 the end point of the new grid.
    :rtype: [Autodesk.Revit.DB.XYZ,Autodesk.Revit.DB.XYZ]
    """

    # list of points to be returned
    sorted_points = []
    # get grid details required for rotation
    curve_grid = grid.Curve
    # origin point is the same as 0 end?
    grid_origin_point = curve_grid.Origin
    # create line through grid origin rotated by 90 degree
    reference_line = get_perpendicular_line_through_point(
        curve_grid, rotation_axis, grid_origin_point
    )

    # work out on which side of the reference line are the two projected points and the other grid end point
    grid_end_point_side = on_which_side_of_line_is_point(
        reference_line, curve_grid.GetEndPoint(1)
    )
    projected_grid_end_point_zero = on_which_side_of_line_is_point(
        reference_line, projected_points[0]
    )
    projected_grid_end_point_one = on_which_side_of_line_is_point(
        reference_line, projected_points[1]
    )

    # work out distances from grid origin to projected points
    projected_end_point_zero_to_grid_origin = distance_between_two_points(
        grid_origin_point, projected_points[0]
    )
    projected_end_point_one_to_grid_origin = distance_between_two_points(
        grid_origin_point, projected_points[1]
    )

    # possible outcomes
    # all three points are smaller then 0 or all three points are greater then 0: grid 0 point is projected point closest to grid origin
    # one projected point is smaller then 0 and the other one is greater then 0: grid 0 point is point on opposite site to other grid end point
    # both projected points are on the opposite site then other grid origin point: grid 0 point is point furthest from grid origin

    if (
        grid_end_point_side < 0
        and projected_grid_end_point_zero < 0
        and projected_grid_end_point_one < 0
    ) or (
        grid_end_point_side > 0
        and projected_grid_end_point_zero > 0
        and projected_grid_end_point_one > 0
    ):
        # grid 0 point is projected point closest to grid origin
        if (
            projected_end_point_zero_to_grid_origin
            < projected_end_point_one_to_grid_origin
        ):
            sorted_points.append(projected_points[0])
            sorted_points.append(projected_points[1])
        else:
            sorted_points.append(projected_points[1])
            sorted_points.append(projected_points[0])
    elif projected_grid_end_point_zero * projected_grid_end_point_one < 0:
        # grid 0 point is point on opposite site to other grid end point
        if projected_grid_end_point_zero * grid_end_point_side < 0:
            # projected 0 end point is opposite grid origin point
            sorted_points.append(projected_points[0])
            sorted_points.append(projected_points[1])
        else:
            # projected 1 end point is opposite grid origin point
            sorted_points.append(projected_points[1])
            sorted_points.append(projected_points[0])
    else:
        # grid 0 point is point furthest from grid origin
        if (
            projected_end_point_zero_to_grid_origin
            > projected_end_point_one_to_grid_origin
        ):
            sorted_points.append(projected_points[0])
            sorted_points.append(projected_points[1])
        else:
            sorted_points.append(projected_points[1])
            sorted_points.append(projected_points[0])
    return sorted_points


def _create_datum_line_linear_grid(crop_box_boundary_lines, grid, debug_view):
    """
        Creates a new datum line for a linear grid from its intersection points with a crop box.

        :param crop_box_boundary_lines: The boundary segments of a view crop.
        :type crop_box_boundary_lines: _type_
        :param grid: The grid to be extended.
        :type grid: Autodesk.Revit.DB.Grid
        :param debug_view: The view to draw debug lines on. (commands commented out in the moment)
        :type debug_view: Autodesk.Revit.DB.View

        :return:
        Result class instance.

        - result.status. True if a new datum line was successfully calculated, otherwise False.
        - result.message will contain the name(s) of the grids.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    new_grid_line = None
    # get the curve describing the grid (Autodesk.Revit.DB.Line)
    curve_grid = grid.Curve
    # check this is a line (and not an arc or similar...)
    if type(curve_grid) == Line:
        # get a direction of that curve
        grid_vector = curve_grid.Direction
        projected_points_list = []
        # loop over view crop outlines
        for line_bound in crop_box_boundary_lines:
            # cast a ray from the grid origin point along the direction vector
            point = XYZ(
                curve_grid.Origin.X, curve_grid.Origin.Y, line_bound.GetEndPoint(0).Z
            )
            ray_cast = Line.CreateUnbound(point, grid_vector)

            # set up result array that will contain the intersection point if one is found
            out_intersection_results = clr.Reference[IntersectionResultArray]()
            # perform a ray intersect operation of the unbound line through the grid curve origin and the bounding box line and populate IntersectionResultArray if there is an intersection
            result = ray_cast.Intersect(line_bound, out_intersection_results)
            # check what type of intersection the ray has with the bounding box line
            # if result is an overlap store the intersection point
            if result == SetComparisonResult.Overlap:
                intersection_result = out_intersection_results.Value
                projected_points_list.append(intersection_result[0].XYZPoint)

        # check if we have 2 intersection points
        if len(projected_points_list) == 2:
            # create a new grid line curve
            # Check location of points...
            # use approach checking which new point is on which side of the original origin point if drawing a perpendicular line through the curve origin point:
            # if both new points are on the same side than the other original curve end point then the point closest to the original origin is the new end 0 and the other one is the new end 1
            # if both new points are on the opposite side than the other original curve end point then the point closest to the original origin is the new end 0 and the other one is the new end 1
            # if one new point is on the opposing side and one new point on the same side than the other original curve end point, then the point on the opposing side is the new end 0 and the other one is the new end 1
            sorted_points = _sort_projected_grid_end_points(
                grid, XYZ.BasisZ, projected_points_list
            )

            # for some reason the create bound needs to get the points back to front in order not to swap end 0 and end 1 once the curve is assigned.
            new_grid_line = Line.CreateBound(sorted_points[1], sorted_points[0])
            return_value.update_sep(
                True, "Grid {} line successfully calculated".format(grid.Name)
            )
            return_value.result = [new_grid_line]
        else:
            return_value.update_sep(
                False,
                "Grid {} returned {} intersection points. Exactly 2 intersection points are required.".format(
                    grid.Name, len(projected_points_list)
                ),
            )
    else:
        return_value.update_sep(
            False, "Grid {} is not line based and will be ignored.".format(grid.Name)
        )
    return return_value


def _extend_linear_grids_to_view_crop(
    active_view, bound_lines_original, cut_offset, grids
):
    """
    Extends grids to view crop.

    :param active_view: The view in which the grids to extend to the crop.
    :type active_view: Autodesk.Revit.DB.View
    :param bound_lines_original: List of lines forming the view crop.
    :type bound_lines_original: IList<AutoDesk.Revit.DB.CurveLoop>
    :param cut_offset: Z value of view.
    :type cut_offset: double
    :param grids: Linear grids visible in view.
    :type grids: [Autodesk.Revit.DB.Grid]

    :return:
    Result class instance.

    - result.status. True if all grids in view got extended successfully, otherwise False.
    - result.message will contain the name(s) of the grids extended.
    - result.result empty list

    On exception:

    - result.status (bool) will be False.
    - result.message will contain generic exception message.
    - result.result will be empty

    :rtype: :class:`.Result`
    """
    return_value = res.Result()
    try:
        # check if plan view...crop box needs a transform!
        if active_view.ViewDirection.IsAlmostEqualTo(XYZ(0, 0, 1)):
            # get Current Elevation of boundLines
            current_view_plane_z = list(bound_lines_original)[0].GetEndPoint(0).Z
            # transform boundLines CurveLoop
            crop_box_transform = Transform.CreateTranslation(
                XYZ(0, 0, cut_offset - current_view_plane_z)
            )
            # transform crop box curve loop
            bound_lines_transformed = CurveLoop.CreateViaTransform(
                bound_lines_original, crop_box_transform
            )
            # loop over grids and calculate new curves intersecting the crop box curve loop
            for grid in grids:
                # calculate grid extent to fit exactly into the crop box
                new_grid_line_curve_status = _create_datum_line_linear_grid(
                    bound_lines_transformed, grid, active_view
                )
                return_value.update(new_grid_line_curve_status)
                if new_grid_line_curve_status.status:
                    new_grid_line_curve = new_grid_line_curve_status.result[0]
                    try:
                        # set grid to be a 2D grid, in active view with curve as calculated.
                        grid.SetCurveInView(
                            DatumExtentType.ViewSpecific,
                            active_view,
                            new_grid_line_curve,
                        )
                        return_value.update_sep(
                            True,
                            "Set extend of grid: {} in view: {}".format(
                                grid.Name, active_view.Name
                            ),
                        )
                    except Exception as e:
                        return_value.update_sep(
                            False,
                            "Failed to set extend of grid: {} with: {}".format(
                                grid.Name, e
                            ),
                        )
        else:
            # elevations and sections
            for grid in grids:
                # calculate grid extent to fit exactly into the crop box
                new_grid_line_curve = _create_datum_line_linear_grid(
                    bound_lines_original, grid, active_view
                )
                if new_grid_line_curve is not None:
                    try:
                        # set grid to be a 2D grid, in active view with curve as calculated.
                        grid.SetCurveInView(
                            DatumExtentType.ViewSpecific,
                            active_view,
                            new_grid_line_curve,
                        )
                        return_value.update_sep(
                            True,
                            "Set extend of grid: {} in view: {}".format(
                                grid.Name, active_view.Name
                            ),
                        )
                    except Exception as e:
                        return_value.update_sep(
                            False,
                            "Failed to set extend of grid: {} with: {}".format(
                                grid.Name, e
                            ),
                        )
    except Exception as e:
        return_value.update_sep(False, e.message)
    return return_value


def extend_linear_grids_to_crop_box_of_view(doc, view):
    """
    Extends all linear grids to intersection points with crop box on active view.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
    Result class instance.

    - result.status. True if all grids in active view got extended successfully, otherwise False.
    - result.message will contain the name(s) of the grids extended.
    - result.result empty list

    On exception:

    - result.status (bool) will be False.
    - result.message will contain generic exception message.
    - result.result will be empty

    :rtype: :class:`.Result`
    """
    return_value = res.Result()
    try:
        # check the active view type
        if not (_check_active_view_type(view)):
            raise ValueError(
                "The active view {} is not of an supported view type: {}.".format(
                    view.Name, view.ViewType
                )
            )
        # get grids visible in active view
        # note: this will only return standalone linear grids
        linear_grids_in_view = get_linear_grids_in_model_by_view(doc, view)
        # check if anything came back
        if len(linear_grids_in_view) == 0:
            raise ValueError(
                "The active view {} contains no grids.".format(
                    view.Name,
                )
            )
        # get Z point of active view
        cut_offset = (
            linear_grids_in_view[0]
            .GetCurvesInView(DatumExtentType.ViewSpecific, view)[0]
            .GetEndPoint(0)
            .Z
        )
        # get the crop box outline
        shape_manager = view.GetCropRegionShapeManager()
        # check whether crop box outline is valid (i.e. the view has crop active either just as visible or as visible and applied)
        bound_lines_original = None
        if len(shape_manager.GetCropShape()) > 0:
            bound_lines_original = shape_manager.GetCropShape()[0]
        else:
            raise ValueError(
                "The active view {} does has no crop active.".format(view.Name)
            )

        # change grids in view within an action (which will get wrapped in a transaction)
        def action():
            return_value = _extend_linear_grids_to_view_crop(
                view,  # the active view
                bound_lines_original,  # the crop bound lines
                cut_offset,  # z-point of active view
                linear_grids_in_view,  # grids in view
            )
            return return_value

        transaction = Transaction(
            doc, "Updating grid extents in view: {}".format(view.Name)
        )
        # execute the transaction
        updated_grids = rTran.in_transaction(transaction, action)
        return_value.update(updated_grids)
    except Exception as e:
        return_value.update_sep(False, e.message)
        return_value.append_message("Aborting!")
    return return_value
