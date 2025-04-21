"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit 2D curve creation.
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


from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common import transaction as rTran

from Autodesk.Revit.DB import (
    Line,
    Transaction,
    XYZ
)

def draw_line_between_points(doc, view, start_point, end_point, transaction_manager=rTran.in_transaction):
    """
    Draws a line between two points in a Revit view.
    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view in which to draw the line.
    :type view: Autodesk.Revit.DB.View
    :param start_point: The start point of the line.
    :type start_point: Autodesk.Revit.DB.XYZ
    :param end_point: The end point of the line.
    :type end_point: Autodesk.Revit.DB.XYZ
    :return: Result object containing the status of the operation.
    :rtype: Result
    """

    # set up an action to be run in a transaction
    # to draw a 2D line
    # in the provided view
    def action():
        action_return_value = Result()
        try:
            line_to_draw = Line.CreateBound(start_point, end_point)
            dc = doc.Create.NewDetailCurve(view, line_to_draw)
            action_return_value.update_sep(True, "Line drawn")
            return action_return_value
        except Exception as e:
            action_return_value.update_sep(False, "Failed to draw line: {}".format(e))
            return action_return_value
       

    # if no transaction manager is provided, assume this is running in a transaction
    # started outside of this function
    if transaction_manager is None:
        return_value = action()
        return return_value
    
    # otherwise, use the provided transaction manager
    transaction = Transaction(doc, "Drawing line")
    return_value = transaction_manager(transaction, action)
    return return_value


def draw_2D_lines_on_bounding_box(doc, bounding_box, view,  transaction_manager=rTran.in_transaction):
    """
    Draw 2D lines on the bounding box of an element in view provided
    
    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param bounding_box: The bounding box of the element.
    :type bounding_box: Autodesk.Revit.DB.BoundingBoxXYZ
    :param view: The view in which to draw the lines.
    :type view: Autodesk.Revit.DB.View
    :param transaction_manager: The transaction manager to use.
    :type transaction_manager: function
    
    :return: Result object containing the status of the operation.
    :rtype: Result
    """

    return_value = Result()

    # get the corners of the bounding box
    min_x = bounding_box.Min.X
    min_y = bounding_box.Min.Y
    max_x = bounding_box.Max.X
    max_y = bounding_box.Max.Y

    # create a list of points for the lines
    points = [
        XYZ(min_x, min_y, 0),
        XYZ(max_x, min_y, 0),
        XYZ(max_x, max_y, 0),
        XYZ(min_x, max_y, 0),
        XYZ(min_x, min_y, 0)
    ]

    def action():
        action_return_value = Result()
        try:
            # draw the lines on the view
            for i in range(len(points) - 1):
                create_line_result = draw_line_between_points(doc, view, start_point=points[i], end_point=points[i + 1],  transaction_manager=None)
                action_return_value.update(create_line_result)
        except Exception as e:
            action_return_value.update_sep(False, "Failed to draw lines: {}".format(e))

        return action_return_value

    # use the provided transaction manager to draw the bounding box
    transaction = Transaction(doc, "Drawing bounding box")
    return_value = transaction_manager(transaction, action)

    return return_value


def draw_2D_lines_on_bounding_box_and_separate_point(doc, bounding_box, additional_point, view,  transaction_manager=rTran.in_transaction):
    """
    Draw 2D lines on the bounding box of an element in view provided and in addition lines from each corner of the bounding box to the additional point.
    
    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param bounding_box: The bounding box of the element.
    :type bounding_box: Autodesk.Revit.DB.BoundingBoxXYZ
    :param additional_point: The additional point to draw lines to.
    :type additional_point: Autodesk.Revit.DB.XYZ
    :param view: The view in which to draw the lines.
    :type view: Autodesk.Revit.DB.View
    :param transaction_manager: The transaction manager to use.
    :type transaction_manager: function
    
    :return: Result object containing the status of the operation.
    :rtype: Result
    """

    return_value = Result()

    # get the corners of the bounding box
    min_x = bounding_box.Min.X
    min_y = bounding_box.Min.Y
    max_x = bounding_box.Max.X
    max_y = bounding_box.Max.Y

    # create a list of points for the lines
    points_bbox = [
        XYZ(min_x, min_y, 0),
        XYZ(max_x, min_y, 0),
        XYZ(max_x, max_y, 0),
        XYZ(min_x, max_y, 0),
        XYZ(min_x, min_y, 0),
    ]
    
    # flatten the additional point to 2D
    additional_point = XYZ(additional_point.X, additional_point.Y, 0)

    def action():
        action_return_value = Result()
        try:
            # draw the lines on the view
            for i in range(len(points_bbox) - 1):
                create_line_result = draw_line_between_points(doc, view, start_point=points_bbox[i], end_point=points_bbox[i + 1],  transaction_manager=None)
                action_return_value.update(create_line_result)
            # draw lines from each corner of the bounding box to the additional point
            for point in points_bbox[:-1]:
                create_line_result = draw_line_between_points(doc, view, start_point=point, end_point=additional_point,  transaction_manager=None)
                action_return_value.update(create_line_result)
        except Exception as e:
            action_return_value.update_sep(False, "Failed to draw lines: {}".format(e))

        return action_return_value

    # use the provided transaction manager to draw the bounding box
    transaction = Transaction(doc, "Drawing bounding box")
    return_value = transaction_manager(transaction, action)

    return return_value