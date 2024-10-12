"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit view geometry helper functions
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

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from Autodesk.Revit.DB import ViewType
from duHast.Revit.Common.Geometry.geometry import (
    point_in_polygon,
    UV_pt_list_from_crv_list,
)


def is_point_in_plan_view_crop_box(point, target_view):
    """
    Checks if the X,Y of a given point are in the crop box of a given plan view.
    Assumes the CropBoxActive for the view is True.
    :param point: XYZ point
    :param type: XYZ
    :param target_view: Plan view
    :param type: ViewPlan
    :return: True if point is in crop box, False otherwise
    :rtype: bool
    """
    if target_view.ViewType == ViewType.FloorPlan:
        crop_region_shape_mgr = target_view.GetCropRegionShapeManager()
        if crop_region_shape_mgr is None:
            return False
        crop_region_shape = crop_region_shape_mgr.GetCropShape()

        if not crop_region_shape == None and len(list(crop_region_shape)) > 0:
            crop_box_perimeter_pts = []
            # Iterate over all the curve loops in the crop region shape incase there
            # are multiple
            for curve_loop in crop_region_shape:
                crop_box_perimeter_pts.extend(UV_pt_list_from_crv_list(curve_loop))

            tag_head_uv = (point.X, point.Y)

            if point_in_polygon(tag_head_uv, crop_box_perimeter_pts):
                return True
            else:
                return False
