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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.parameter_set_utils import set_builtin_parameter_without_transaction_wrapper_by_name

from Autodesk.Revit.DB import BoundingBoxXYZ, BuiltInParameter, View3D, ViewOrientation3D, XYZ


def _unit(x, y, z):
    length = (x * x + y * y + z * z) ** 0.5
    if length == 0:
        raise ValueError("a view direction needs a length")
    return XYZ(x / length, y / length, z / length)


def create_view_3d_around_box_without_transaction_wrapper(
    doc, view_type, view_name, forward, up, box_min, box_max, phase=None
):
    """
    Creates an isometric 3D view that looks along a direction at a box, and cuts the model to that box (the section box).

    The camera is put back along the direction far enough to see the whole box, so the box is what the view shows
    whatever height the model sits at: the pitch comes from the direction.

    Must be called inside a transaction.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_type: The 3D view family type.
    :type view_type: Autodesk.Revit.DB.ViewFamilyType
    :param view_name: The name of the new view.
    :type view_name: str
    :param forward: The direction the view looks along (x, y, z); any length.
    :type forward: tuple of float
    :param up: The view's up direction (x, y, z); any length.
    :type up: tuple of float
    :param box_min: The corner of the box with the smallest coordinates, in feet.
    :type box_min: Autodesk.Revit.DB.XYZ
    :param box_max: The opposite corner, in feet.
    :type box_max: Autodesk.Revit.DB.XYZ
    :param phase: The phase of the view, defaults to None (Revit's default).
    :type phase: Autodesk.Revit.DB.Phase, optional

    :return: Result with the new view in its result list.
    :rtype: Result
    """

    return_value = Result()
    try:
        view = View3D.CreateIsometric(doc, view_type.Id)
        if view is None:
            raise ValueError("Failed to create a 3D view.")
        view.Name = view_name

        if phase is not None:
            set_builtin_parameter_without_transaction_wrapper_by_name(
                element=view, parameter_definition=BuiltInParameter.VIEW_PHASE, parameter_value=phase.Id
            )

        box = BoundingBoxXYZ()
        box.Min = box_min
        box.Max = box_max
        view.SetSectionBox(box)
        view.IsSectionBoxActive = True

        forward_unit = _unit(*forward)
        up_unit = _unit(*up)
        centre = XYZ(
            (box_min.X + box_max.X) / 2.0, (box_min.Y + box_max.Y) / 2.0, (box_min.Z + box_max.Z) / 2.0
        )
        diagonal = box_min.DistanceTo(box_max)
        eye = centre - forward_unit * (diagonal * 2.0)
        view.SetOrientation(ViewOrientation3D(eye, up_unit, forward_unit))

        return_value.append_message("Successfully created 3D view {}".format(view_name))
        return_value.result.append(view)
    except Exception as e:
        return_value.update_sep(False, "Failed to create 3D view {}: {}".format(view_name, e))
    return return_value
