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

from duHast.Revit.DetailItems.filled_regions import  get_filled_region_curve_loops
from duHast.Revit.Common.Geometry.curve_loops import get_area_from_closed_curve_loop

def get_filled_region_area(doc, filled_region):
    """
    Get the area of a filled region
    
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
        # check if the area was found
        if area_outer_result.status == False:
            message = "Failed to get outer area: {}".format(area_outer_result.message)
            return_value.update_sep(False, message)
            # return -1 as area
            return_value.result.append(area)
            return return_value
        
        # get the area of the outer loop
        area_outer = area_outer_result.result[0]
        
        # assume the second loop is the inner loop
        if len(filled_region_curve_loops) == 2:
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
            area = area + area_wall_half
            
        else:
            # single loop filled region
            return_value.append_message("Filled region has only one loop.")
            return_value.result.append(area_outer)
        
    except Exception as e:
        message = "Failed to get area: {}".format(e)
        return_value.result.append(area)
        return_value.update_sep(False, message)
    return return_value
