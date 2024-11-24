"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit plan view creation. 
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
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Revit.Common.parameter_set_utils import set_builtin_parameter_without_transaction_wrapper_by_name
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)

from duHast.Revit.Views.views_crop import apply_view_crop_without_transaction_wrapper, apply_view_bounding_box_crop_without_transaction_wrapper

from Autodesk.Revit.DB import  BoundingBoxXYZ, BuiltInParameter, CurveLoop, Transaction, ViewPlan


def create_view_plan(
        doc, 
        level, 
        view_type, 
        view_name = None, 
        phasing=None, 
        view_crop = None, 
        view_crop_visible = True
    ):
    """
    Creates a new plan view in the Revit document.

    This function creates a new plan view in the specified Revit document, sets its properties, and handles any errors that occur during the process. The function supports setting the view name, phasing, and crop box properties.

    :param doc: The Revit document where the view will be created.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level at which the view will be created.
    :type level: Autodesk.Revit.DB.Level
    :param view_type: The type of the view to be created.
    :type view_type: Autodesk.Revit.DB.ViewFamilyType
    :param view_name: The name to assign to the new view, defaults to None.
    :type view_name: str, optional
    :param phasing: The phase to assign to the new view, defaults to None.
    :type phasing: Autodesk.Revit.DB.Element, optional
    :param view_crop: The crop box or loop to apply to the view, defaults to None.
    :type view_crop: Autodesk.Revit.DB.BoundingBoxXYZ or Autodesk.Revit.DB.CurveLoop, optional
    :param view_crop_visible: Flag indicating whether the crop box should be visible, defaults to True.
    :type view_crop_visible: bool, optional
    
    :return: A Result object containing the outcome of the view creation process.
    :rtype: Result
    """

    return_value = Result()

    try:
        # set up an action which creates the sheet and assigns properties
        def action():
            action_return_value = Result()
            try:
                view_plan = ViewPlan.Create(doc, view_type.Id, level.Id)

                # check if sheet was actually created?
                if not view_plan:
                    raise ValueError("Failed to create new plan view.")
                try:
                    # set view standard properties
                    if(view_name):
                        view_plan.Name = view_name
                except Exception as e:
                    # only pass on the message to caller
                    action_return_value.append_message("Failed to set view name to {} with exception: {}".format(view_name, e))
                
                # set the phasing
                result_phase = set_builtin_parameter_without_transaction_wrapper_by_name(
                    element=view_plan, 
                    parameter_definition=BuiltInParameter.VIEW_PHASE, 
                    parameter_value=phasing.Id
                )
                # only pass on the message to caller
                action_return_value.append_message(result_phase.message)
               
                # set the view crop ( can be a bounding box or a loop )
                if(isinstance(view_crop,  BoundingBoxXYZ)):
                    # set the crop shape
                    result_bbox = apply_view_bounding_box_crop_without_transaction_wrapper(view=view_plan, bbox=view_crop)
                    # only pass on the message to caller
                    return_value.append_message(result_bbox.message)
                elif (isinstance(view_crop, CurveLoop)):
                    result_loop =  apply_view_crop_without_transaction_wrapper(view=view_plan, crop_loop=view_crop)
                    # only pass on the message to caller
                    return_value.append_message(result_loop.message)
                
                # make sure the view is cropped if a crop method was supplied
                if view_crop:
                    view_plan.CropBoxActive = True
                
                # set the visibility of the view crop
                view_plan.CropBoxVisible = view_crop_visible
                
                action_return_value.append_message("Successfully created view {}".format(view_plan.Name))
                action_return_value.result.append(view_plan)
            except Exception as e:
                action_return_value.update_sep(False,"{}".format(e))
            return action_return_value
        
        # define failure handling for the transaction ( roll back on any warnings or errors )
        failure_handling_settings = FailureHandlingConfig(
            roll_back_on_warning=True,
            print_warnings=False,
            roll_back_on_error=True,
            print_errors=False,
        )

        if(view_name):
            view_name_transaction = view_name
        else:
            view_name_transaction = "default revit view name"
        # set up the transaction
        trans = Transaction(doc, "creating view plan {}".format(view_name_transaction))

        # execute the transaction with failure handling
        result_transaction = in_transaction_with_failure_handling(
            transaction=trans,
            action=action,
            failure_config=failure_handling_settings,
        )

        # update the return value with the result of the transaction
        return_value.update(result_transaction)
    except Exception as e:
        return_value.update_sep(False, "failed to create plan view with exception: {}".format(e))

    return return_value