"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view port to data view port conversion. 
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


from duHast.Data.Objects.data_sheet_view_port import DataSheetViewPort
from duHast.Data.Objects.Properties.Geometry.geometry_bounding_box import DataBoundingBox
from duHast.Data.Objects.Properties.data_view_port_type_names import DataViewPortTypeNames
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

from Autodesk.Revit.DB import ViewType


def _get_view_port_type(doc, revit_view_port):
    """
    Returns a string reprensenting the viewport type on None if to be ignored (not match with view port types of interest)

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_port: A Revit ViewPort
    :type view_port: Autodesk.Revit.DB.ViewPort

    :return: The viewport type name or none
    :rtype: str or None
    """

    view = doc.GetElement(revit_view_port.ViewId)

    if view.ViewType == ViewType.FloorPlan:
        return DataViewPortTypeNames.FLOOR_PLAN
    elif view.ViewType == ViewType.Elevation:
        return DataViewPortTypeNames.ELEVATION
    elif view.ViewType == ViewType.ThreeD:
        return DataViewPortTypeNames.THREE_D
    elif view.ViewType == ViewType.Schedule:
        # thats unlikely
        return DataViewPortTypeNames.SCHEDULE
    else:
        return None


def convert_revit_viewport_to_data_instance(doc, revit_view_port):
    """
    Convertes a Revit ViewPort into a data viewport

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_port: A Revit ViewPort
    :type view_port: Autodesk.Revit.DB.ViewPort
    :return: A populated data viewport instance
    :rtype: :class:`.DataSheetViewPort`
    """

    view_port_type = _get_view_port_type(doc, revit_view_port)
    if view_port_type == None:
        # ignore this viewport
        return None

    # set up data instances
    view_port_data = DataSheetViewPort()
    bbox = DataBoundingBox()

    # get an outline from the Revit view port
    view_port_outline = revit_view_port.GetBoxOutline()
    # get the outlines min and max points
    max_point = view_port_outline.MaximumPoint
    min_point = view_port_outline.MinimumPoint

    # get the min and max point from the outline
    bbox.max = [convert_imperial_feet_to_metric_mm(max_point.X),convert_imperial_feet_to_metric_mm(max_point.Y),convert_imperial_feet_to_metric_mm(max_point.Z)]
    bbox.min = [convert_imperial_feet_to_metric_mm(min_point.X),convert_imperial_feet_to_metric_mm(min_point.Y),convert_imperial_feet_to_metric_mm(min_point.Z)]
    
    # update the bounding box property of the view port instance
    view_port_data.bounding_box = bbox

    # set the viewport type
    view_port_data.vp_type =view_port_type

    return view_port_data