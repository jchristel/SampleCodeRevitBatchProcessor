"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit filled regions.
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

from duHast.Revit.DetailItems.Utility import detail_items_type_sorting as rDetailItemTypeSort
from duHast.Revit.DetailItems.detail_items import get_all_detail_types_by_category, FILLED_REGION_TYPE
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value, getter_double_as_double_converted_to_metric
from duHast.Revit.Common.Geometry.curve_loops import get_area_from_closed_curve_loop

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInParameter,
    FilledRegion,
    FilteredElementCollector,
)


def get_filled_regions_in_model(doc):
    """
    Gets all filled region instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list containing floor instances.
    :rtype: list Autodesk.Revit.DB.FilledRegion
    """

    return FilteredElementCollector(doc).OfClass(FilledRegion)


def get_all_filled_region_type_ids_available(doc):
    """
    Gets all filled region types ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing filled region types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    dic = rDetailItemTypeSort.build_detail_type_ids_dictionary(
        get_all_detail_types_by_category(doc)
    )
    if FILLED_REGION_TYPE in dic:
        return dic[FILLED_REGION_TYPE]
    else:
        return []



# --------------------------------------------- geometry ------------------

def get_filled_region_curve_loops(filled_region):
    """
    Gets the curve loops of a filled region.
    :param filled_region: A filled region instance.
    :type filled_region: Autodesk.Revit.DB.FilledRegion

    :return: A list of curve loops.
    :rtype: list Autodesk.Revit.DB.CurveLoop
    """

    # get the loops of a filled region's geometry
    curve_loops = filled_region.GetBoundaries()

    return curve_loops


def get_filled_region_loop_area(doc, view, filled_region, loop_index=0):
    """
    Gets loop area of a filled region.
    This will create a temporary filled region using just the loop and get the area.

    :param filled_region: A filled region instance.
    :type filled_region: Autodesk.Revit.DB.FilledRegion
    :param loop_index: The index of the loop to get the area for.
    :type loop_index: int
    
    :return: The area of the loop.
    :rtype: float
    """
    
    # set up a status tracker
    return_value = Result()
    
    try:
        # get the loops of a filled region's geometry
        curve_loops = get_filled_region_curve_loops(filled_region)
        
        if loop_index >= len(curve_loops):
            return_value.update_sep(False, "Loop index out of range.")
            return return_value

        # get the area of the filled region using the loop
        area_result = get_area_from_closed_curve_loop(
            doc=doc,
            view=view,
            curve_loop=curve_loops[loop_index],
        )

        # update the return value with the area
        return_value.update(area_result)
    except Exception as e:
        return_value.update_sep(False, "Failed to get filled region loop area with error: {}".format(e))
    
    return return_value

def get_filled_region_area(filled_region):
    """
    Gets the area of a filled region using the built-in parameter.
   
    :param filled_region: A filled region instance.
    :type filled_region: Autodesk.Revit.DB.FilledRegion

    :return: The area of the filled region.
    :rtype: float
    """

    # set up a status tracker
    return_value = Result()

    try:
       
        # get the area of the filled region
        area = get_built_in_parameter_value(
            element=filled_region,
            built_in_parameter_def=BuiltInParameter.HOST_AREA_COMPUTED,
            parameter_value_getter=getter_double_as_double_converted_to_metric,
        )
        
        # update the return value with the area
        return_value.result.append(area)
        return_value.append_message("Filled region area retrieved successfully.")
    except Exception as e:
        return_value.update_sep(False, "Failed to get filled region area with error: {}".format(e))

    return return_value