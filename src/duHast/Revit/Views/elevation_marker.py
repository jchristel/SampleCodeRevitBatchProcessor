"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to make an elevation marker at a place and turn, create the views on it and set what they look at.
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

from Autodesk.Revit.DB import (
    BoundingBoxXYZ,
    BuiltInParameter,
    ElementTransformUtils,
    ElevationMarker,
    Line,
    XYZ,
)


def create_elevation_marker_without_transaction_wrapper(doc, view_type, location, scale, rotation=0.0):
    """
    Creates an elevation marker and turns it about its own point.

    A marker holds up to four elevation views, one per index; turning the marker turns all of them,
    which is how an index is made to face a chosen wall.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_type: The elevation view family type.
    :type view_type: Autodesk.Revit.DB.ViewFamilyType
    :param location: Where the marker goes (z is the level it belongs to).
    :type location: Autodesk.Revit.DB.XYZ
    :param scale: The scale of the views on the marker.
    :type scale: int
    :param rotation: Counter clockwise turn about the marker's point in radians, defaults to 0.0.
    :type rotation: float, optional

    :return: Result class instance. .result holds the marker when it was created.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        marker = ElevationMarker.CreateElevationMarker(doc, view_type.Id, location, int(scale))
        if marker is None:
            return_value.update_sep(False, "Revit did not create the elevation marker.")
            return return_value
        if abs(rotation) > 1e-9:
            axis = Line.CreateBound(location, XYZ(location.X, location.Y, location.Z + 1.0))
            ElementTransformUtils.RotateElement(doc, marker.Id, axis, rotation)
        return_value.result.append(marker)
        return_value.append_message("Elevation marker created.")
    except Exception as e:
        return_value.update_sep(False, "Failed to create the elevation marker with exception: {}".format(e))
    return return_value


def rotate_elevation_marker_without_transaction_wrapper(doc, marker, location, rotation):
    """
    Turns an elevation marker, and the views on it, about the marker's own point.

    Which way index 0 of a new marker looks is Revit's to say, so a caller which needs a view to look a
    certain way creates the views first, reads where one looks (ViewSection.ViewDirection) and turns the
    marker by the difference.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param marker: The elevation marker.
    :type marker: Autodesk.Revit.DB.ElevationMarker
    :param location: The marker's point, in feet.
    :type location: Autodesk.Revit.DB.XYZ
    :param rotation: Counter clockwise turn in radians.
    :type rotation: float

    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        axis = Line.CreateBound(location, XYZ(location.X, location.Y, location.Z + 1.0))
        ElementTransformUtils.RotateElement(doc, marker.Id, axis, rotation)
        return_value.append_message("Elevation marker turned by {:.1f} degrees.".format(math.degrees(rotation)))
    except Exception as e:
        return_value.update_sep(False, "Failed to turn the elevation marker with exception: {}".format(e))
    return return_value


def create_elevation_on_marker_without_transaction_wrapper(doc, marker, view_plan, index, name=None, phase_id=None):
    """
    Creates the elevation view at one index of a marker.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param marker: The elevation marker.
    :type marker: Autodesk.Revit.DB.ElevationMarker
    :param view_plan: The plan view the marker is in.
    :type view_plan: Autodesk.Revit.DB.ViewPlan
    :param index: The index on the marker, 0 to 3.
    :type index: int
    :param name: The name of the new view, defaults to None (Revit's own).
    :type name: str, optional
    :param phase_id: The phase of the new view, defaults to None (Revit's own).
    :type phase_id: Autodesk.Revit.DB.ElementId, optional

    :return: Result class instance. .result holds the view when it was created.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        if not marker.IsAvailableIndex(index):
            return_value.update_sep(False, "Index {} of the marker is not available.".format(index))
            return return_value
        view = marker.CreateElevation(doc, view_plan.Id, index)
        if name:
            view.Name = name
        if phase_id is not None:
            phase = view.get_Parameter(BuiltInParameter.VIEW_PHASE)
            if phase is not None and not phase.IsReadOnly:
                phase.Set(phase_id)
        return_value.result.append(view)
        return_value.append_message("Elevation view {} created at index {}.".format(view.Name, index))
    except Exception as e:
        return_value.update_sep(False, "Failed to create the elevation view with exception: {}".format(e))
    return return_value


def get_rotation_to_face(look_x, look_y, index_zero_looks=(0.0, 1.0)):
    """
    The turn, in radians counter clockwise, that makes index 0 of an unturned marker look along (look_x, look_y).

    A new marker's index 0 looks along +y in plan (indices 1 to 3 follow at quarter turns); this is
    the assumption to check when a marker comes out facing the wrong way, and the only place it is made.

    :param look_x: x of the direction to look along in plan.
    :type look_x: float
    :param look_y: y of the direction to look along in plan.
    :type look_y: float
    :param index_zero_looks: The direction index 0 looks along on an unturned marker, defaults to (0.0, 1.0).
    :type index_zero_looks: tuple, optional

    :return: The turn in radians, in (-pi, pi].
    :rtype: float
    """

    wanted = math.atan2(look_y, look_x)
    base = math.atan2(index_zero_looks[1], index_zero_looks[0])
    turn = wanted - base
    while turn > math.pi:
        turn -= 2.0 * math.pi
    while turn <= -math.pi:
        turn += 2.0 * math.pi
    return turn


def set_elevation_extent_without_transaction_wrapper(view, line_start, line_end, depth):
    """
    Sets how wide and how far an elevation view looks.

    The width is the crop box's extent along the view's right direction, taken from where the line's
    two ends fall on it; the depth is the far clip, made active, at that offset from the view plane.

    Changing the model: this needs to run inside a transaction.

    :param view: The elevation view.
    :type view: Autodesk.Revit.DB.ViewSection
    :param line_start: One end of the elevation line in the model, in feet.
    :type line_start: Autodesk.Revit.DB.XYZ
    :param line_end: The other end, in feet.
    :type line_end: Autodesk.Revit.DB.XYZ
    :param depth: How far the view looks from its plane, in feet; None or 0 leaves the far clip as it is.
    :type depth: float or None

    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        crop = view.CropBox
        inverse = crop.Transform.Inverse
        xs = [inverse.OfPoint(line_start).X, inverse.OfPoint(line_end).X]
        box = BoundingBoxXYZ()
        box.Transform = crop.Transform
        box.Min = XYZ(min(xs), crop.Min.Y, crop.Min.Z)
        box.Max = XYZ(max(xs), crop.Max.Y, crop.Max.Z)
        view.CropBoxActive = True
        view.CropBox = box
        if depth is not None and depth > 0.0:
            clipping = view.get_Parameter(BuiltInParameter.VIEWER_BOUND_FAR_CLIPPING)
            if clipping is not None and not clipping.IsReadOnly:
                clipping.Set(1)  # clip with line
            offset = view.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)
            if offset is not None and not offset.IsReadOnly:
                offset.Set(depth)
        return_value.append_message("Extent of {} set.".format(view.Name))
    except Exception as e:
        return_value.update_sep(False, "Failed to set the extent of the elevation view with exception: {}".format(e))
    return return_value
