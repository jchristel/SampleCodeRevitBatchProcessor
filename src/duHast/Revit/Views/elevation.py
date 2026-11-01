"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit elevations. 
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

from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    ElevationMarker,
    ElementId,
    FilteredElementCollector,
    LocationPoint,
    ViewPlan,
    ViewSection,
    XYZ,
)

from duHast.Revit.Common.element_id import get_el_id_int

from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm


def get_marker_and_index_of_view(doc, view):
    """
    Get the elevation marker hosting an elevation view and the index the view has on it.

    The index alone does not say which marker it belongs to: a room with two markers has an
    index 0 on each, so the marker is needed to know which views belong together.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: Revit view.
    :type view: Autodesk.Revit.DB.View

    :return: The marker and the index, or (None, None) if the view is not on a marker.
    :rtype: (Autodesk.Revit.DB.ElevationMarker, int) or (None, None)
    """

    # check if we got an elevation view to start with
    if not isinstance(view, ViewSection):
        return None, None

    for marker in FilteredElementCollector(doc).OfClass(ElevationMarker):
        for i in range(marker.MaximumViewCount):
            if marker.GetViewId(i) == view.Id:
                return marker, i
    return None, None


def get_view_index_on_marker(doc, view):
    """
    Get the index of the view on the elevation marker.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: Revit view.
    :type view: Autodesk.Revit.DB.View

    :return: Index of the view on the elevation marker. None if not found.
    :rtype: int or None
    """

    marker, index = get_marker_and_index_of_view(doc, view)
    return index


def get_marker_location(marker, doc=None):
    """
    Get where an elevation marker sits.

    Revit gives an elevation marker no point of its own: its Location is the bare Location class (it can only
    be moved and rotated), and it has no bounding box outside a plan view. So, when it is not a LocationPoint,
    and a document is given, the centre of the marker's circle is worked out from its view pointers (see
    get_marker_centre_from_pointers).

    :param marker: The elevation marker.
    :type marker: Autodesk.Revit.DB.ElevationMarker
    :param doc: The document the marker is in, defaults to None (only a LocationPoint is then answered).
    :type doc: Autodesk.Revit.DB.Document, optional

    :return: The marker's point in Revit's internal units (feet), None if it cannot be found.
    :rtype: Autodesk.Revit.DB.XYZ or None
    """

    location = marker.Location
    if isinstance(location, LocationPoint):
        return location.Point
    if doc is None:
        return None
    return get_marker_centre_from_pointers(doc, marker)


def _plan_view_showing(doc, marker):
    """The first plan view in which the marker has a bounding box (it has none outside a view), or None."""
    for view in FilteredElementCollector(doc).OfClass(ViewPlan):
        try:
            if view.IsTemplate:
                continue
            if marker.get_BoundingBox(view) is not None:
                return view
        except Exception:
            continue
    return None


def get_marker_centre_from_pointers(doc, marker):
    """
    The centre of an elevation marker's circle, from the pointers of its views.

    Each view on a marker has a pointer (a dependent element of the Viewers category, shown as "Views" in Revit, created just before the
    view, so the one with the largest id below the view's) that sits along the view's direction from the
    circle. The pointer's bounding box in a plan view therefore has its centre on the line through the circle
    along the view's direction, and the circle is where those lines cross: the least squares point over every
    view. Two opposite views alone fix the point as the middle of their pointers. One view cannot say how far
    along its line the circle is, so a marker with a single view answers None.

    Measured on a marker with four views: the four pointers' lines crossed at the circle's centre, where the
    elevation lines' own middles were 280 mm away (a line can be cropped off-centre).

    :param doc: The document the marker is in.
    :type doc: Autodesk.Revit.DB.Document
    :param marker: The elevation marker.
    :type marker: Autodesk.Revit.DB.ElevationMarker

    :return: The centre in feet, None if it cannot be worked out.
    :rtype: Autodesk.Revit.DB.XYZ or None
    """

    try:
        plan = _plan_view_showing(doc, marker)
        if plan is None:
            return None
        # the pointers are in OST_Viewers (-2000278), which Revit names "Views"; OST_Views is another category
        views_category = int(BuiltInCategory.OST_Viewers)
        pointers = []
        for element_id in marker.GetDependentElements(None):
            element = doc.GetElement(element_id)
            if element is None or element.Category is None or isinstance(element, (ViewSection, ElevationMarker)):
                continue
            if get_el_id_int(element.Category.Id) != views_category:
                continue
            box = element.get_BoundingBox(plan)
            if box is not None:
                pointers.append((get_el_id_int(element_id), (box.Min + box.Max) * 0.5))

        axes = []
        for index in range(marker.MaximumViewCount):
            view_id = marker.GetViewId(index)
            if view_id == ElementId.InvalidElementId:
                continue
            view = doc.GetElement(view_id)
            below = [p for p in pointers if p[0] < get_el_id_int(view_id)]
            if view is None or not below:
                continue
            centre = max(below, key=lambda p: p[0])[1]
            direction = view.ViewDirection
            length = (direction.X * direction.X + direction.Y * direction.Y) ** 0.5
            if length == 0.0:
                continue
            axes.append((centre, direction.X / length, direction.Y / length))
        if len(axes) < 2:
            return None

        # least squares over the lines (a point, a direction): the normal equations of the squared distances
        a = b = d = rx = ry = 0.0
        for centre, dx, dy in axes:
            nx, ny = -dy, dx
            a += nx * nx
            b += nx * ny
            d += ny * ny
            k = nx * centre.X + ny * centre.Y
            rx += nx * k
            ry += ny * k
        det = a * d - b * b
        z = axes[0][0].Z
        if abs(det) < 1e-6:
            # every line parallel (two opposite views): the middle of the pointers is the circle
            return XYZ(sum(c.X for c, _, _ in axes) / len(axes), sum(c.Y for c, _, _ in axes) / len(axes), z)
        return XYZ((d * rx - b * ry) / det, (a * ry - b * rx) / det, z)
    except Exception:
        return None


def get_elevation_footprint(view):
    """
    Get the elevation line and how far the view looks, in model coordinates.

    The crop box of an elevation is in the view's own frame (x to the right, y up, z towards
    the viewer) and its transform takes it to the model. The elevation line is the crop box's
    width on the plane through the view origin (z = 0); the view looks back from it along
    minus z, so the crop box's minimum z is how far it sees.

    :param view: The elevation view.
    :type view: Autodesk.Revit.DB.ViewSection

    :return: (line start, line end, depth) as XYZ in feet and a length in feet, or None when the
        view has no crop box.
    :rtype: (Autodesk.Revit.DB.XYZ, Autodesk.Revit.DB.XYZ, float) or None
    """

    crop = view.CropBox
    if crop is None:
        return None

    transform = crop.Transform
    start = transform.OfPoint(XYZ(crop.Min.X, 0.0, 0.0))
    end = transform.OfPoint(XYZ(crop.Max.X, 0.0, 0.0))
    return start, end, max(0.0, -crop.Min.Z)


def get_far_clip(view):
    """
    Get the far clip settings of an elevation view.

    :param view: The elevation view.
    :type view: Autodesk.Revit.DB.ViewSection

    :return: (mode, offset in mm). Mode is 0 for no clip, 1 for clip with line, 2 for clip without
        line (Revit's own values); either is None when the parameter is missing.
    :rtype: (int or None, float or None)
    """

    mode = None
    offset = None
    p_mode = view.get_Parameter(BuiltInParameter.VIEWER_BOUND_FAR_CLIPPING)
    if p_mode is not None and p_mode.HasValue:
        mode = p_mode.AsInteger()
    p_offset = view.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)
    if p_offset is not None and p_offset.HasValue:
        offset = convert_imperial_feet_to_metric_mm(p_offset.AsDouble())
    return mode, offset
