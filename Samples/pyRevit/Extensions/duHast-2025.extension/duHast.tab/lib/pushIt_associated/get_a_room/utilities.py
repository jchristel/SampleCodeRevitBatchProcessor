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


from duHast.Utilities.Objects.result import Result

from duHast.Revit.DetailItems.filled_regions import  get_filled_region_curve_loops , get_filled_region_area
from duHast.Revit.Common.Geometry.curve_loops import get_area_from_closed_curve_loop


# types of families
FAMILY_TYPE_NAME_ROOM = "Room"
FAMILY_TYPE_NAME_BAY = "Bay"

from Autodesk.Revit.DB import XYZ

def get_filled_region_with_two_loops_area(doc, filled_region):
    """
    Get the area of a filled region if there are 2 curve loops.
    The area is calculated by getting the area of the inner loop and adding to it the difference of area of outer loop minus the area of the inner loop.

    This needs to run in its own transaction since it creates a new filled region to get the area.
    Revit only calculates the area of the filled region when the transaction the filled region is created with is committed.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param filled_region: The filled region to get the area from
    :type filled_region: Autodesk.Revit.DB.FilledRegion
    
    :return: A result object with the area of the filled region
    :rtype: Result
    """
    
    # set up a status tracker
    return_value = Result()
    try:
        # set the default value
        area = -1.0
        # get the curve loops of the filled region
        filled_region_curve_loops = get_filled_region_curve_loops(filled_region)
        
        # get the outer area of the filled region
        area_outer_result = get_area_from_closed_curve_loop(
            doc= doc, 
            view = doc.ActiveView, 
            curve_loop = filled_region_curve_loops[0],
            filled_region_type_id = filled_region.GetTypeId(),
        )

        if area_outer_result.status == False:
            message = "Failed to get outer area: {}".format(area_outer_result.message)
            return_value.update_sep(False, message)
            # return -1 as area
            return_value.result.append(area)
            return return_value
        
        # get the area of the outer loop
        area_outer = area_outer_result.result[0]
        
        # assume the second loop is the inner loop
        if len(filled_region_curve_loops) != 2:
            return_value.append_message("Filled region has not 2 loops.")
            return_value.result.append(area_outer)
            return return_value

        # get the area of the filled region
        area_inner_result = get_area_from_closed_curve_loop(
            doc= doc, 
            view = doc.ActiveView, 
            curve_loop = filled_region_curve_loops[1],
            filled_region_type_id = filled_region.GetTypeId(),
        )
        
        # check if the area was found
        if area_inner_result.status == False:
            message = "Failed to get inner area: {}".format(area_inner_result.message)
            return_value.update_sep(False, message)
            # return -1 as area
            return_value.result.append(area)
            return return_value
        
        # get the area of the inner and outer loops
        area_inner = area_inner_result.result[0]
        
        # calculate the area of the filled region
        area_wall_half = (area_outer - area_inner)/2
        area = area_inner + area_wall_half
        
        # update the return value with the area
        return_value.append_message("Area of filled region: {}".format(area))
        return_value.result.append(area)
        
    except Exception as e:
        message = "Failed to get area: {}".format(e)
        return_value.result.append(area)
        return_value.update_sep(False, message)
    return return_value



def verify_filled_region(filled_region):
    """
    Verify if the filled region is valid:

    - has at least one loop
    - has at at maximum 2 loops
    - if 2 loops, those must be nested

    :param filled_region: The filled region to verify
    :type filled_region: Autodesk.Revit.DB.FilledRegion
    :return: True if the filled region complies with the rules, False otherwise
    :rtype: bool
    """
    
    # set up a status tracker
    return_value = Result()
    
    try:
        # get the filled region curve loops
        filled_region_curve_loops = get_filled_region_curve_loops(filled_region)
        # check if the filled region has curves
        if filled_region_curve_loops is None:
            message = "No curves found in filled region."
            return_value.update_sep(False, message)
            return return_value
        
        # reject any filled region with a curve loop count greater than 2
        if len(filled_region_curve_loops) > 2:
            message = "Filled region '{}' {} has more than 2 curves. Will be ignored.".format(filled_region.Name, filled_region.Id.IntegerValue)
            return_value.update_sep(False, message)
            return return_value
        
        # if (len(filled_region_curve_loops) == 2):
        #     # print the direction of each loop
        #     normal = XYZ(0, 0, 1)
        #     counter = 0
        #     over_all_ccw = True
        #     for curve_loop in filled_region_curve_loops:
        #         loop_is_ccw = curve_loop.IsCounterclockwise(normal)
        #         if counter ==0 :
        #             # set the first loop direction to overall
        #             over_all_ccw = loop_is_ccw
        #             # increase the counter
        #             counter += 1
        #         else:
        #             if loop_is_ccw == over_all_ccw:
        #                 # both loops are in the same direction...thats bad
        #                 message = "Filled region {} has 2 loops in the same direction".format(filled_region.Name)
        #                 return_value.update_sep(False, message)
        #                 return  return_value
        #else:
        # add the filled region to the filtered regions
        return_value.append_message("Filled region passes filter")
            
    except Exception as e:
        message = "Failed to verify filled region: {}".format(e)
        return_value.update_sep(False, message)
    
    return return_value