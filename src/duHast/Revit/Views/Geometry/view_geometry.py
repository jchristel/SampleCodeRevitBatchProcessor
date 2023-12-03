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
