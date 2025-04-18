"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit curve loops helper functions
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

from System.Collections.Generic import List

from duHast.Revit.Common.transaction import in_temp_transaction
from duHast.Utilities.Objects.result import Result
from duHast.Revit.DetailItems.filled_regions_create import create_filled_region_by_view
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value, getter_double_as_double_converted_to_metric

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInParameter,
    CurveLoop,
    Transaction
)

def create_curve_loops_through_transform(curve_loops, transform, convert_net_list=False):
    """
    Creates a new curve loop by transforming the existing curve loops using the provided transform.

    :param curve_loops: The curve loops to be transformed.
    :type curve_loops: list of Autodesk.Revit.DB.CurveLoop
    :param transform: The transform to be applied to the curve loops.
    :type transform: Autodesk.Revit.DB.Transform
    :param convert_net_list: Flag to indicate whether to convert the curve loops to a .net List of curves (true) or python list (false).
    :type convert_net_list: bool

    :return: A list of transformed curve loops.
    :rtype: .net List of Autodesk.Revit.DB.CurveLoop or python list of Autodesk.Revit.DB.CurveLoop
    """

    if convert_net_list:
        # convert the curve loops to a list of curves
        new_curve_loops = List[CurveLoop]()
        for curve_loop in curve_loops:
            # create a new curve loop
            new_curve_loop = CurveLoop.CreateViaTransform(curve_loop, transform)
            # add the new curve loop to the list
            new_curve_loops.Add(new_curve_loop)
        return new_curve_loops
    else:
        new_curve_loops = []
        for curve_loop in curve_loops:
            transformed_curve_loop = CurveLoop.CreateViaTransform(curve_loop,  transform)
            new_curve_loops.append(transformed_curve_loop)
        
        return new_curve_loops


def get_area_from_closed_curve_loop(doc, view, curve_loop, filled_region_type_id):
    """
    Calculates the area of a closed curve loop in a given view.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view in which the curve loop is located.
    :type view: Autodesk.Revit.DB.View
    :param curve_loop: The closed curve loop.
    :type curve_loop: Autodesk.Revit.DB.CurveLoop

    :return: The area of the closed curve loop.
    :rtype: float
    """

    # set up a status tracker
    return_value = Result()
    
    # default area value
    area = -1.0
    
    try:
        
        # check if the curve loop is closed
        if curve_loop.IsOpen():
            return_value.update_sep(False, "Curve loop is not closed.")
            return_value.result.append(area)
            return return_value
        
        # set up an action creating a filled region using the loop
        def action():
            # set up a status tracker
            action_return_value = Result()
            try:
                # create the filled region using the loop
                filled_region_result = create_filled_region_by_view(
                    doc=doc, 
                    view=view, 
                    curve_loops=List[CurveLoop](curve_loop), 
                    filled_region_type=filled_region_type_id,
                )
                
                if filled_region_result.status == False:
                    action_return_value.update_sep(False, "Failed to create filled region.")
                    return action_return_value
                
                # get the actual filled region instance
                filled_region = filled_region_result.result[0]
                
                # get the area of the filled region
                area = get_built_in_parameter_value(
                    element=filled_region,
                    built_in_parameter_def=BuiltInParameter.HOST_AREA_COMPUTED,
                    parameter_value_getter=getter_double_as_double_converted_to_metric,
                )
                
                # store the area in the return value
                action_return_value.result.append(area)
                action_return_value.append_message("Filled region area retrieved successfully.")
            except Exception as e:
                action_return_value.update_sep(False, "Failed to get filled region area with error: {}".format(e))
            return action_return_value
    
        transaction = Transaction(doc, "Getting area of curve loop")
        return_value = in_temp_transaction(transaction, action)
        
    except Exception as e:
        return_value.update_sep(False, "Failed to get filled region loop area with error: {}".format(e))
        
    return return_value