"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit elevation view creation. 
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

from Autodesk.Revit.DB import  BoundingBoxXYZ, BuiltInParameter, CurveLoop, ElevationMarker, Transaction


def create_elevation_views(
        doc, 
        view_type, 
        view_marker_location, 
        scale, 
        view_index_list = [],
        view_names = [], 
        view_plan = None, 
        phasing=None, 
        view_crop = None, 
        view_crop_visible = True, 
        transaction_manager =  in_transaction_with_failure_handling
    ):
    """
    Creates an elevation marker and associated elevation views in the Revit document.

    This function creates an elevation marker at the specified location and, if defined through their indicis, creates elevation views on that marker. It sets various properties for the views, such as names, phasing, and crop box settings. The function can handle transactions and failure handling as specified.

    :param doc: The Revit document where the elevation marker and views will be created.
    :type doc: Autodesk.Revit.DB.Document
    :param view_type: The type of the elevation view to be created.
    :type view_type: Autodesk.Revit.DB.ViewFamilyType
    :param view_marker_location: The location where the elevation marker will be placed.
    :type view_marker_location: Autodesk.Revit.DB.XYZ
    :param scale: The initial scale of the elevation views.
    :type scale: int
    :param view_index_list: List of indices specifying which elevation views on the marker to create, defaults to an empty list.
    :type view_index_list: list of int, optional
    :param view_names: List of names to assign to the created elevation views, defaults to an empty list.
    :type view_names: list of str, optional
    :param view_plan: The plan view to associate with the elevation views, defaults to None. Only required if elevation views are to be created (not just a marker)
    :type view_plan: Autodesk.Revit.DB.ViewPlan, optional
    :param phasing: The phase to assign to the new views, defaults to None.
    :type phasing: Autodesk.Revit.DB.Element, optional
    :param view_crop: The crop box or loop to apply to the views, defaults to None.
    :type view_crop: Autodesk.Revit.DB.BoundingBoxXYZ or Autodesk.Revit.DB.CurveLoop, optional
    :param view_crop_visible: Flag indicating whether the crop box should be visible, defaults to True.
    :type view_crop_visible: bool, optional
    :param transaction_manager: The transaction manager to handle transactions and failure handling, defaults to in_transaction_with_failure_handling. Set to None if a transaction is already running.
    :type transaction_manager: function, optional
    :raises ValueError: If the elevation marker or views cannot be created.
    
    :return: A Result object containing the outcome of the elevation creation process.
    :rtype: Result
    """

    return_value = Result()

    try:
        # set up an action which creates the sheet and assigns properties
        def action():
            action_return_value = Result()
            try:
                elevation_marker = ElevationMarker.CreateElevationMarker(doc, view_type.Id, view_marker_location, scale)

                # check if sheet was actually created?
                if not elevation_marker :
                    raise ValueError("Failed to create new elevation marker.")
                else:
                    # add it to the return object
                    action_return_value.result.append(elevation_marker)
                
                
                # create the actual elevations
                if len(view_index_list)>0:
                    for elevation_index in view_index_list:
                        # create view by index
                        new_view = elevation_marker.CreateElevation(doc, view_plan.Id, elevation_index)
                
                        try:
                            # set view standard properties
                            if(new_view and len(view_names)> elevation_index):
                                new_view.Name = view_names[elevation_index]
                            else:
                                action_return_value.append_message("no new name provided. Keeping revit default name.")
                        except Exception as e:
                            # only pass on the message to caller
                            action_return_value.append_message("Failed to set view name with exception: {}".format(e))
                
                        # set the phasing
                        result_phase = set_builtin_parameter_without_transaction_wrapper_by_name(
                            element=new_view, 
                            parameter_definition=BuiltInParameter.VIEW_PHASE, 
                            parameter_value=phasing.Id
                        )
                        # only pass on the message to caller
                        action_return_value.append_message(result_phase.message)
               
                        # set the view crop ( can be a bounding box or a loop )
                        if(isinstance(view_crop, BoundingBoxXYZ)):
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
                            new_view.CropBoxActive = True
                
                        # set the visibility of the view crop
                        new_view.CropBoxVisible = view_crop_visible
                
                        action_return_value.append_message("Successfully created view {}".format(new_view.Name))
                        action_return_value.result.append(new_view)
            except Exception as e:
                action_return_value.update_sep(False,"{}".format(e))
            return action_return_value
        

        # check if this is to be run in a transaction or not
        if(transaction_manager):

            # define failure handling for the transaction ( roll back on any warnings or errors )
            failure_handling_settings = FailureHandlingConfig(
                roll_back_on_warning=True,
                print_warnings=False,
                roll_back_on_error=True,
                print_errors=False,
            )

            # set up the transaction
            trans = Transaction(doc, "creating view elevation(s) {}")

            # execute the transaction with failure handling
            result_transaction = transaction_manager(
                transaction=trans,
                action=action,
                failure_config=failure_handling_settings,
            )

            # update the return value with the result of the transaction
            return_value.update(result_transaction)
        else:
            # assume a transaction is already running
            return_value.update(action())

    except Exception as e:
        return_value.update_sep(False, "failed to create plan view with exception: {}".format(e))

    return return_value