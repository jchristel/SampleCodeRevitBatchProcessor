"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
View crop utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.element_id import get_el_id_int, get_element_id_from_int
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import (
    BoundingBoxXYZ,
    BuiltInParameter,
    ElementId,
    ElementTransformUtils,
    Line,
    SubTransaction,
    Transaction,
    XYZ,
)


def get_view_crop(view):
    """
    Get the crop region loops of a view.

    This method returns a representation of the boundaries of the currently active crop for the associated view.
    If the view crop has a non-rectangular shape, the method returns that shape.
    Otherwise, if the view crop has been split, the method returns the multiple rectangular boundaries visible in the crop - note that this does not reflect any offsets that may have been applied to the boundary regions.
    If the crop is not split, this returns a single rectangle representing the crop.
    All coordinates are in the coordinate frame of the view.

    :param view: The view to get the crop region from.
    :type view: Autodesk.Revit.DB.View
    :return: The crop region of the view.
    :rtype: [Autodesk.Revit.DB.CurveLoop]
    """

    # attempt to get the views shape manager
    shape_manager = view.GetCropRegionShapeManager()

    # check if the shape manager is None
    if shape_manager is None:
        return None

    # get the crop shape loops
    loops = shape_manager.GetCropShape()

    return loops


def apply_view_crop_without_transaction_wrapper(view, crop_loop):
    """
    Apply a crop region to a view.

    This method sets the crop region of the view to the specified crop loops.

    :param view: The view to apply the crop region to.
    :type view: Autodesk.Revit.DB.View
    :param crop_loops: The crop loop to apply to the view.
    :type crop_loops: Autodesk.Revit.DB.CurveLoop

    :return: The result of the operation.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    try:
        # attempt to get the views shape manager
        shape_manager = view.GetCropRegionShapeManager()

        # check if the shape manager is None
        if shape_manager is None:
            return_value.update_sep(
                False,
                "Could not get the crop region shape manager for the view: {}.".format(
                    view
                ),
            )
            return return_value
       
        # set the crop shape
        shape_manager.SetCropShape(crop_loop)
        return_value .update_sep(
            True, "Successfully updated view crop: {}".format(view)
        )
       
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to update view crop: {} with error: {}".format(view, e),
        )

    return return_value


def apply_view_crop(doc, view, crop_loop):
    """
    Apply a crop region to a view.

    This method sets the crop region of the view to the specified crop loops.

    :param doc: The document containing the view.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view to apply the crop region to.
    :type view: Autodesk.Revit.DB.View
    :param crop_loops: The crop loop to apply to the view.
    :type crop_loops: Autodesk.Revit.DB.CurveLoop

    :return: The result of the operation.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    try:
        # attempt to get the views shape manager
        shape_manager = view.GetCropRegionShapeManager()

        # check if the shape manager is None
        if shape_manager is None:
            return_value.update_sep(
                False,
                "Could not get the crop region shape manager for the view: {}.".format(
                    view
                ),
            )
            return return_value

        # set up an action to be executed in a transaction
        def action():
            action_return_value = Result()
            action_return_value =apply_view_crop_without_transaction_wrapper(view=view, crop_loop=crop_loop)
            return action_return_value

        transaction = Transaction(doc, "changing view crop")
        return_value = in_transaction(transaction, action)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to update view crop: {} with error: {}".format(view, e),
        )

    return return_value


def apply_view_bounding_box_crop_without_transaction_wrapper(view, bbox):
    """
    Apply a crop region to a view.

    This method sets the crop region of the view to the specified crop loops.

    :param view: The view to apply the crop region to.
    :type view: Autodesk.Revit.DB.View
    :param bbox: The bounding box to apply as crop to the view.
    :type cbbox: Autodesk.Revit.DB.BoundingBoxXYZ

    :return: The result of the operation.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    try:
        # set the crop shape
        view.CropBox = bbox
        return_value .update_sep(
            True, "Successfully updated view crop: {}".format(view)
        )
           
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to update view crop: {} with error: {}".format(view, e),
        )

    return return_value


def apply_view_bounding_box_crop(doc, view, bbox):
    """
    Apply a crop region to a view.

    This method sets the crop region of the view to the specified crop loops.

    :param doc: The document containing the view.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view to apply the crop region to.
    :type view: Autodesk.Revit.DB.View
    :param bbox: The bounding box to apply as crop to the view.
    :type cbbox: Autodesk.Revit.DB.BoundingBoxXYZ

    :return: The result of the operation.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    try:

        # set up an action to be executed in a transaction
        def action():
            action_return_value = Result()
            action_return_value= apply_view_bounding_box_crop_without_transaction_wrapper(view, bbox)
            return action_return_value

        transaction = Transaction(doc, "changing view crop")
        return_value = in_transaction(transaction, action)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to update view crop: {} with error: {}".format(view, e),
        )

    return return_value


def set_view_crop_around_point_without_transaction_wrapper(view, centre, width, height):
    """
    Activates the crop of a view and sets it to a rectangle of the given size centred on a point.

    The rectangle is built in the crop box's own coordinate system and keeps the crop box's Z range. The crop region is
    made active and its visibility is switched off.

    :param view: The view to crop.
    :type view: Autodesk.Revit.DB.View
    :param centre: The point to centre the crop on, in model coordinates (feet).
    :type centre: Autodesk.Revit.DB.XYZ
    :param width: The crop width in the view's horizontal direction (feet).
    :type width: float
    :param height: The crop height in the view's vertical direction (feet).
    :type height: float

    :return: The result of the operation.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()
    try:
        crop_box = view.CropBox
        local = crop_box.Transform.Inverse.OfPoint(centre)
        new_box = BoundingBoxXYZ()
        new_box.Transform = crop_box.Transform
        new_box.Min = XYZ(local.X - width / 2.0, local.Y - height / 2.0, crop_box.Min.Z)
        new_box.Max = XYZ(local.X + width / 2.0, local.Y + height / 2.0, crop_box.Max.Z)
        view.CropBoxActive = True
        view.CropBoxVisible = False
        return_value.update(apply_view_bounding_box_crop_without_transaction_wrapper(view, new_box))
    except Exception as e:
        return_value.update_sep(False, "Failed to crop view {} around a point: {}".format(view, e))
    return return_value


# How far either side of a plan view's id its crop box element is looked for. Measured in Revit 2026
# (2026-11-12, two new floor plans): the crop box element is the view's id + 2, and the element at + 6
# carries the view's name as well.
CROP_ELEMENT_SEARCH = 6

# A view counts as turned as asked when its right direction is within this of the angle asked for.
TURN_TOLERANCE_DEG = 0.01


def get_crop_box_element_candidates(doc, view):
    """
    The elements that may be a plan view's crop box element, the most likely first.

    View.CropBox is only a BoundingBoxXYZ; the element that draws the crop region is not reachable through the
    API by a property. Revit creates it with the view, so its id sits next to the view's: the view's id + 2
    (learnrevitapi, and measured in Revit 2026). It carries the view's name, and **it has no category**: a lookup by
    the Viewers category (a collector, GetDependentElements, or comparing what the view shows with the crop hidden
    and shown) finds nothing. So the candidates are the elements within CROP_ELEMENT_SEARCH ids of the view whose
    name is the view's, + 2 first, then by distance. Only turning one tells which it is, which is what
    rotate_view_crop_without_transaction_wrapper does.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The plan view.
    :type view: Autodesk.Revit.DB.View

    :return: The candidates' ids, most likely first; empty when there is none.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    view_id = get_el_id_int(view.Id)
    offsets = [k for k in range(-CROP_ELEMENT_SEARCH, CROP_ELEMENT_SEARCH + 1) if k != 0]
    offsets.sort(key=lambda k: (k != 2, abs(k), k))
    candidates = []
    for k in offsets:
        element = doc.GetElement(get_element_id_from_int(view_id + k))
        if element is None:
            continue
        try:
            name = element.Name
        except Exception:
            continue
        if name == view.Name:
            candidates.append(element.Id)
    return candidates


def clear_view_crop_blockers_without_transaction_wrapper(view):
    """
    Takes away what stops a plan view's crop from being turned freely: a scope box, and an orientation of True North.

    A scope box decides the crop of the view it is assigned to, and a view oriented to True North turns with the
    project's angle to it rather than with its crop. Both are set back: the scope box to none and the orientation to
    Project North. A view whose orientation is read only (a view template controls it) is reported, not changed.

    Changing the model: this needs to run inside a transaction.

    :param view: The plan view.
    :type view: Autodesk.Revit.DB.View

    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        scope = view.get_Parameter(BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP)
        if scope is not None and scope.AsElementId() != ElementId.InvalidElementId:
            scope.Set(ElementId.InvalidElementId)
            return_value.append_message("Scope box removed from view {}.".format(view.Name))
        north = view.get_Parameter(BuiltInParameter.PLAN_VIEW_NORTH)
        if north is not None and north.AsInteger() != 0:
            if north.IsReadOnly:
                return_value.update_sep(
                    False, "View {} is oriented to True North and its orientation is read only.".format(view.Name)
                )
            else:
                north.Set(0)
                return_value.append_message("View {} set to Project North.".format(view.Name))
    except Exception as e:
        return_value.update_sep(False, "Failed to clear the crop of view {}: {}".format(view.Name, e))
    return return_value


def _wrap_deg(angle):
    """An angle in degrees brought into (-180, 180]."""

    angle = math.fmod(angle, 360.0)
    if angle > 180.0:
        angle -= 360.0
    if angle <= -180.0:
        angle += 360.0
    return angle


def _turned_by_deg(before, after):
    """The counter clockwise angle from one direction to another in plan, in degrees, in (-180, 180]."""

    return _wrap_deg(math.degrees(math.atan2(after.Y, after.X) - math.atan2(before.Y, before.X)))


def rotate_view_crop_without_transaction_wrapper(doc, view, centre, rotation):
    """
    Turns a plan view by turning its crop box element about a point, so a room at an angle sits square in the view
    and on the sheet.

    A plan view ignores a turned Transform on its CropBox (only Min and Max are honoured, measured in Revit 2026), so
    the view is turned by rotating the element that draws its crop. That element is found by its id
    (get_crop_box_element_candidates); each candidate is rotated inside a sub-transaction, kept if the view's right
    direction turned by the rotation asked for, and undone otherwise. The crop is made active and visible while it is
    turned, and its visibility put back afterwards. A scope box and True North are cleared first
    (clear_view_crop_blockers_without_transaction_wrapper).

    After the turn the crop's own frame is the turned one: fit it with fit_view_crop_to_points_without_transaction_wrapper,
    which works in that frame.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The plan view.
    :type view: Autodesk.Revit.DB.ViewPlan
    :param centre: The point to turn about, in model coordinates (feet); its z is not used.
    :type centre: Autodesk.Revit.DB.XYZ
    :param rotation: Counter clockwise turn in radians. The view's right direction turns by this much, which squares
        a room whose walls run at this angle.
    :type rotation: float

    :return: Result class instance. .result holds the id of the crop box element that turned the view.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    if abs(rotation) < 1e-9:
        return_value.append_message("View {} needs no turn.".format(view.Name))
        return return_value
    was_visible = view.CropBoxVisible
    try:
        return_value.update(clear_view_crop_blockers_without_transaction_wrapper(view))
        if not return_value.status:
            return return_value
        view.CropBoxActive = True
        view.CropBoxVisible = True
        doc.Regenerate()
        candidates = get_crop_box_element_candidates(doc, view)
        if not candidates:
            return_value.update_sep(
                False, "No crop box element found within {} ids of view {}.".format(CROP_ELEMENT_SEARCH, view.Name)
            )
            return return_value
        axis = Line.CreateBound(XYZ(centre.X, centre.Y, 0.0), XYZ(centre.X, centre.Y, 1.0))
        wanted = math.degrees(rotation)
        before = view.RightDirection
        tried = []
        for candidate in candidates:
            offset = get_el_id_int(candidate) - get_el_id_int(view.Id)
            sub = SubTransaction(doc)
            sub.Start()
            try:
                ElementTransformUtils.RotateElement(doc, candidate, axis, rotation)
                doc.Regenerate()
                turned = _turned_by_deg(before, view.RightDirection)
            except Exception as e:
                sub.RollBack()
                tried.append("{:+d} refused ({})".format(offset, e))
                continue
            if abs(_wrap_deg(turned - wanted)) < TURN_TOLERANCE_DEG:
                sub.Commit()
                return_value.result.append(candidate)
                return_value.append_message(
                    "View {} turned by {:.2f} degrees with its crop box element (id {:+d} from the view).".format(
                        view.Name, wanted, offset
                    )
                )
                return return_value
            sub.RollBack()
            tried.append("{:+d} turned the view by {:.2f} degrees".format(offset, turned))
        return_value.update_sep(
            False,
            "No crop box element turned view {} by {:.2f} degrees: {}.".format(view.Name, wanted, "; ".join(tried)),
        )
    except Exception as e:
        return_value.update_sep(False, "Failed to turn the crop of view {}: {}".format(view.Name, e))
    finally:
        try:
            view.CropBoxVisible = was_visible
        except Exception:
            pass
    return return_value


def fit_view_crop_to_points_without_transaction_wrapper(view, points, left=0.0, right=0.0, bottom=0.0, top=0.0):
    """
    Fits a view's crop round points, in the crop's own frame, with an offset on each side.

    Working in the crop's own frame (CropBox.Transform) is what makes this right for a turned view: the sides are
    the view's left, right, bottom and top, which on a view turned by rotate_view_crop_without_transaction_wrapper are
    square to the room, so a template's offsets from its room apply unchanged. Measured in Revit 2026: refitting a
    view turned 30 and -45 degrees this way keeps the turn and gives the room's own rectangle exactly. The crop box's
    z range is kept.

    Changing the model: this needs to run inside a transaction.

    :param view: The view to crop.
    :type view: Autodesk.Revit.DB.View
    :param points: The points to fit round, in model coordinates (feet), for example a room's boundary.
    :type points: list of Autodesk.Revit.DB.XYZ
    :param left: The offset outside the points on the view's left, in feet, defaults to 0.0.
    :type left: float, optional
    :param right: The offset on the view's right, in feet, defaults to 0.0.
    :type right: float, optional
    :param bottom: The offset at the view's bottom, in feet, defaults to 0.0.
    :type bottom: float, optional
    :param top: The offset at the view's top, in feet, defaults to 0.0.
    :type top: float, optional

    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        if not points:
            return_value.update_sep(False, "No points to fit the crop of view {} round.".format(view.Name))
            return return_value
        crop_box = view.CropBox
        inverse = crop_box.Transform.Inverse
        local = [inverse.OfPoint(p) for p in points]
        new_box = BoundingBoxXYZ()
        new_box.Transform = crop_box.Transform
        new_box.Min = XYZ(min(p.X for p in local) - left, min(p.Y for p in local) - bottom, crop_box.Min.Z)
        new_box.Max = XYZ(max(p.X for p in local) + right, max(p.Y for p in local) + top, crop_box.Max.Z)
        view.CropBoxActive = True
        return_value.update(apply_view_bounding_box_crop_without_transaction_wrapper(view, new_box))
    except Exception as e:
        return_value.update_sep(False, "Failed to fit the crop of view {}: {}".format(view.Name, e))
    return return_value
