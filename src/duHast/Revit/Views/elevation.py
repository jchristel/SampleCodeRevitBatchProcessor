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
    BuiltInParameter,
    ElevationMarker,
    FilteredElementCollector,
    LocationPoint,
    ViewSection,
    XYZ,
)

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


def get_marker_location(marker):
    """
    Get where an elevation marker sits.

    :param marker: The elevation marker.
    :type marker: Autodesk.Revit.DB.ElevationMarker

    :return: The marker's point in Revit's internal units (feet), None if it has no point location.
    :rtype: Autodesk.Revit.DB.XYZ or None
    """

    location = marker.Location
    if isinstance(location, LocationPoint):
        return location.Point
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
