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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import Transaction


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


