# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from duHast.Revit.Family.family_element_utils import get_all_curve_based_elements_in_family,get_all_generic_forms_in_family
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Revit.Common.transaction import in_transaction

from duHast.Revit.Levels.levels import get_levels_in_model

from Autodesk.Revit.DB import CurveArrArray, CurveArray, CurveLoop, Curve, Extrusion, ModelLine ,Transaction, SketchPlane


def convert_loop_to_curve_array(curve_loop):
    curve_array = CurveArray()
    if (isinstance(curve_loop, CurveLoop)):
        for curve in curve_loop:
            if (isinstance(curve, Curve)):
                print("Curve: {}".format(curve))
                curve_array.Append(curve)
                
    return curve_array

def convert_curve_loops_to_curve_arr_array(curve_loops):
    """
    Convert a list of curve loops to a CurveArrArray object.
    This is used to create a new extrusion in the family document.
    
    :param curve_loops: list of curve loops
    :return: CurveArrArray object
    """
    
    # create a new curve array array
    curve_arr_array = CurveArrArray()

    curve_array = CurveArray()
    for loop in curve_loops:
        
        if (isinstance(loop, CurveLoop)):
            # a loop of curves, convert to curve array
            c_ar = convert_loop_to_curve_array(loop)
            curve_arr_array.Append(c_ar)
        elif (isinstance(loop, Curve)):
            # just a curve, not a loop
            curve_array.Append(loop)
            
    # only append the curve array if it is not empty
    if (curve_array.Size > 0):
        curve_arr_array.Append(curve_array)

    return curve_arr_array


def update_extrusion_outline(family_doc, curve_loops):
    # set up a status tracker
    return_value = Result()
    try:
        # rather than updating the extrusion outline, we will delete the old extrusion and create a new one
        # need to get the category of the existing extrusion
        # cant delete an extrusion when it comes from a family template...need to create a new family from
        # an existing family not a from a template
        
        # create a new extrusion
        # get the level in the family document   
        level_col = get_levels_in_model(family_doc)
        
        level_plane = None
        for level in level_col:
            level_plane =level
            
        # convert filled region curve loops to curve array array
        new_profile = convert_curve_loops_to_curve_arr_array(curve_loops)
        
        # create a new extrusion in the family document
        def action():
       
            action_return_value = Result()
            try:
                level_reference = level_plane.GetPlaneReference()
                sketch_plane = SketchPlane.Create(family_doc, level_reference)
                
                # Create new extrusion
                new_extrusion = family_doc.FamilyCreate.NewExtrusion(True, new_profile, sketch_plane, 10.00)
                
                action_return_value.append_message("Created new extrusion in family")
                action_return_value.result.append(new_extrusion)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new extrusion in family: {}".format(e))
            return action_return_value

        transaction = Transaction(family_doc, "Creating extrusion")
        return_value = in_transaction(transaction,action )
                
    except Exception as e:
        message = "Failed to update extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def add_2D_outline(family_doc, curve_loop):
    # set up a status tracker
    return_value = Result()
    try:
        return_value.append_message("Adding 2D outline to family")
    except Exception as e:
        message = "Failed to add 2D lines in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value