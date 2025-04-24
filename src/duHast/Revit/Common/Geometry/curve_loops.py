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

from duHast.Revit.Common.transaction import in_transaction
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.unit_conversion import  convert_mm_to_imperial_feet
from duHast.Revit.DetailItems.filled_regions_create import create_filled_region_by_view
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value, getter_double_as_double_converted_to_metric
from duHast.Revit.Common.delete import delete_by_element_ids

# import Autodesk
from Autodesk.Revit.DB import (
    Arc,
    BuiltInParameter,
    Curve,
    CurveArray,
    CurveArrArray,
    CurveLoop,
    Transaction,
    Transform,
    XYZ,
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
    
    
def create_curve_loop_through_offset(curve_loop, offset_distance, offset_to_inside = True):
    """
    Creates a new curve loop by offsetting it a given distance.

    Some 

    :param curve_loop: The curve loop to be transformed.
    :type curve_loop: Autodesk.Revit.DB.CurveLoop
    :param offset_distance: The distance to offset the curve loop.
    :type offset_distance: float
    :param offset_normal: The normal vector to offset the curve loop.
    :type offset_normal: Autodesk.Revit.DB.XYZ

    :return: A transformed curve loops.
    :rtype: Autodesk.Revit.DB.CurveLoop
    """

    # Function to determine if a CurveLoop is an outer loop or an inner loop
    def is_outer_loop(curve_loop):
        # Calculate the area of the CurveLoop
        area = 0.0
        for curve in curve_loop:
            start = curve.GetEndPoint(0)
            end = curve.GetEndPoint(1)
            area += (start.X * end.Y - end.X * start.Y)
        return area > 0

    
    # Determine the offset direction for the outer loop
    if is_outer_loop(curve_loop):
        # If the loop is an outer loop, offset towards the inside
        if  offset_to_inside:
            offset_distance = -abs(offset_distance)
        else:
            offset_distance = abs(offset_distance)
    else:
        if offset_to_inside:
            offset_distance = abs(offset_distance)
        else:
            offset_distance = -abs(offset_distance)

    # Check if the curve loop is a circle
    curve_loop_is_circle = True
    # Check if the curve is arc and adjust the offset direction if necessary
    for curve in curve_loop:
        if not type(curve) == Arc:
            curve_loop_is_circle = curve_loop_is_circle and False
            break

    # If the curve loop is a circle, offset in the opposite direction
    if curve_loop_is_circle:
        offset_distance = -1 * offset_distance

    # convert to imperial feet
    offset_distance = convert_mm_to_imperial_feet(offset_distance)

    # create a new curve loop via offset
    new_curve_loop = CurveLoop.CreateViaOffset(curve_loop, offset_distance, XYZ.BasisZ)

    return new_curve_loop


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
        
        curve_loop_net_list = List[CurveLoop]()
        curve_loop_net_list.Add(curve_loop)

        # set up an action creating a filled region using the loop
        def action():
            # set up a status tracker
            action_return_value = Result()
            try:
                # create the filled region using the loop
                action_return_value = create_filled_region_by_view(
                    doc=doc, 
                    view=view, 
                    curve_loops=curve_loop_net_list, 
                    filled_region_type=filled_region_type_id,
                    transaction_manager=None,
                )
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to get filled region area with error: {}".format(e))
            return action_return_value
    
        transaction = Transaction(doc, "Getting area of curve loop")
        return_value = in_transaction(transaction, action)

        if return_value.status == False:
            return return_value
        
        # get the actual filled region instance
        filled_region = return_value.result[0]
        
        # get the area of the filled region
        area = get_built_in_parameter_value(
            element=filled_region,
            built_in_parameter_def=BuiltInParameter.HOST_AREA_COMPUTED,
            parameter_value_getter=getter_double_as_double_converted_to_metric,
        )

        # store the area in the return value
        return_value.result=[area]

        # delete the filled region
        delete_result = delete_by_element_ids(
            doc=doc, 
            ids=[filled_region.Id],
            transaction_name="Deleting temp filled region",
            element_name="filled region",
        )

        if delete_result.status == False:
            return_value.update_sep(False, "Failed to delete filled region with error: {}".format(delete_result.message))
            return return_value
        
    except Exception as e:
        return_value.update_sep(False, "Failed to get filled region loop area with error: {}".format(e))
        
    return return_value


def convert_loop_to_curve_array(curve_loop):
    """
    Convert a curve loop to a CurveArray object.
    Curve loop can not contain nested loops.
    
    :param curve_loop: The curve loop to convert.
    :type curve_loop: Autodesk.Revit.DB.CurveLoop
    :return: CurveArray object
    """
    
    curve_array = CurveArray()
    if (isinstance(curve_loop, CurveLoop)):
        for curve in curve_loop:
            if (isinstance(curve, Curve)):
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


def get_curve_loop_centroid(curve_loop):
    """
    Finds an approximate centroid inside the given CurveLoop. The curve loop is assumed to be closed and planar.
    
    :param original_loop: The CurveLoop to find the centroid of.
    :type original_loop: Autodesk.Revit.DB.CurveLoop
    :return: The centroid point of the CurveLoop.
    :rtype: Autodesk.Revit.DB.XYZ
    """
    
    # check if the curve loop is closed
    if curve_loop.IsOpen():
        raise ValueError("Curve loop is not closed.")
        
    sum_point = XYZ.Zero
    count = 0

    for curve in curve_loop:
        sum_point += curve.GetEndPoint(0)
        sum_point += curve.GetEndPoint(1)
        count += 2

    centroid = sum_point / count
    return centroid  # Likely inside the original loop


def get_curve_loop_by_offset_towards_centroid( curve_loop, offset_distance):
    """
    Creates a new curve loop by offsetting the original curve loop towards its centroid.
    This is not a size change but a position change!
    
    :param curve_loop: The original CurveLoop to be offset.
    :type curve_loop: Autodesk.Revit.DB.CurveLoop
    :param offset_distance: The distance to offset the curve loop.
    :type offset_distance: float

    :return: A new CurveLoop that is offset from the original.
    :rtype: Autodesk.Revit.DB.CurveLoop
    """
    
    # get the centroid of the curve loop
    centroid = get_curve_loop_centroid(curve_loop)
    
    vector_to_centroid = None

    for curve in curve_loop:
        # check if the curve is a line
        if not isinstance(curve, Curve):
            raise ValueError("Curve loop contains non-linear curves.")
        
        # create a vector from the centroid to the first point of the curve loop
        vector_to_centroid = centroid - curve.GetEndPoint(0)

        break

    # normalize the vector and multiply by the offset distance
    offset_vector = vector_to_centroid.Normalize() * offset_distance
    
    # create a transform using the offset vector
    transform = Transform.CreateTranslation(offset_vector)
    
    # create a new curve loop by transforming the original curve loop
    new_curve_loop = create_curve_loops_through_transform([curve_loop], transform, convert_net_list=False)[0]
    
    return new_curve_loop
