"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit detail lines.
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

from duHast.Utilities.Objects import result as res

# import Autodesk
from Autodesk.Revit.DB import (
    ElementTransformUtils,
    Line,
    Transform,
    XYZ,
)


def draw_detail_line_at_90_degree(doc, view, start_point, end_point):
    """
        Draws a detail line at 90 degree angle to given points, rotated around 0 end point.

        Needs to run in a transaction.

        :param doc: The current model document
        :type doc: Autodesk.Revit.DB.Document
        :param view: The plan view to draw the detail line on.
        :type view: Autodesk.Revit.DB.View
        :param start_point: Start point of line.
        :type start_point: Autodesk.Revit.DB.XYZ
        :param end_point: End point of line.
        :type end_point: Autodesk.Revit.DB.XYZ

        :return:
        Result class instance.

        - result.status. True if line was rotated and drawn on view successfully, otherwise False.
        - result.message will contain the original points and rotated start and end points.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    line_to_draw = Line.CreateBound(start_point, end_point)
    return_value = res.Result()
    try:
        dc = doc.Create.NewDetailCurve(view, line_to_draw)
        dc_curve = dc.GeometryCurve
        aa = dc_curve.GetEndPoint(0)
        cc = XYZ(aa.X, aa.Y, aa.Z + 10)
        axis = Line.CreateBound(aa, cc)
        ElementTransformUtils.RotateElement(doc, dc.Id, axis, math.pi / 2.0)

        dc_curve_rotated = dc.GeometryCurve

        # get a line through origin at 90 degree
        trans_form = Transform.CreateRotationAtPoint(
            XYZ.BasisZ, math.pi / 2.0, start_point
        )
        transformed_line = line_to_draw.CreateTransformed(trans_form)

        return_value.append_message(
            "transformed line origin {} and end point {}".format(
                transformed_line.GetEndPoint(0), transformed_line.GetEndPoint(1)
            )
        )

        return_value.append_message(
            "rotated line origin {} and end point {}".format(
                dc_curve_rotated.GetEndPoint(0), dc_curve_rotated.GetEndPoint(1)
            )
        )

        return_value.update_sep(
            True,
            "Drew line between origin:{} and second point: {} in view {}".format(
                start_point, end_point, view.Name
            ),
        )
    except Exception as e:
        return_value.update_sep(False, e.message)

    return return_value
