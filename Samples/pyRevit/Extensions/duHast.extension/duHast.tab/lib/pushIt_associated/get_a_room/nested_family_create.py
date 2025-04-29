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

import os

from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.utility import get_current_user_name
from duHast.Utilities.date_stamps import get_file_date_stamp, FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC


from duHast.Revit.Common.file_io import  save_as_family,  open_family

from pushIt_associated.get_a_room import settings
from pushIt_associated.get_a_room.nested_family_utils import create_new_extrusion_from_outlines, add_2D_outline, test_offset_curve_loop

from Autodesk.Revit.DB import CurveLoop

def create_coarse_detail_family(doc, family_config):
    """
    Creates a coarse detail family based on the provided family config.
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_config: The family config object
    :type family_config: FamilyTypeConfig

    :return: Result class instance.

        - `result.status` (bool): True if the family was created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation.
        - `result.result` (list): File name of family.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()
    nested_coarse_detail_family_doc = None
    nested_coarse_detail_family_name = None
    try:

        return_value.append_message("Creating nested {} coarse detail family:".format(family_config.room_type))
        # get the filled region curve loops
        filled_region_curve_loops = family_config.curve_loops

        # open the nested family coarse template
        fam_result_coarse = open_family(doc, family_path=family_config.generic_nested_coarse_path)
        if fam_result_coarse.status == False:
            message =  "Failed to create nested {} coarse detail family: {}".format(family_config.room_type,fam_result_coarse.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("...Nested {} coarse detail family created from template: \n{}".format(family_config.room_type, family_config.generic_nested_coarse_path))
        # get the family document
        nested_coarse_detail_family_doc = fam_result_coarse.result[0]

        # update the extrusion outline
        # if the filled region has two curve loops, use the inner loop only...
        loop_of_interest = filled_region_curve_loops[0] if len(filled_region_curve_loops) == 1 else filled_region_curve_loops[1]
        
        # test if loop is valid by drawing a filled region
        test_result = test_offset_curve_loop(nested_coarse_detail_family_doc, loop_of_interest,120)

        if test_result.status == False:
            message = "Failed to create offset curve loop: {} using default curve instead".format(test_result.message)
            return_value.append_message( message)
        else:
            message = "Successfully create offset curve loop"
            return_value.append_message( message)
            loop_of_interest = test_result.result[0]
        
        # work with the loop of interest
        extrusion_curve_loops = List[CurveLoop]()
        extrusion_curve_loops.Add(loop_of_interest)

        # create a new extrusion in the family
        create_extrusion_result = create_new_extrusion_from_outlines(
            nested_coarse_detail_family_doc,  
            extrusion_curve_loops,
            None, # provide none to have the default extrusion height of 10mm
            is_visible_coarse_detail=True,
        )
        
        # check if the update extrusion was successful
        if create_extrusion_result.status == False:
            message = "Failed to create new extrusion in nested {} coarse detail family : {}".format(family_config.room_type, create_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("...Nested {} coarse detail family extrusion created".format(family_config.room_type))
       
        # add 2D lines to the family
        add_2d_lines_result = add_2D_outline(nested_coarse_detail_family_doc, loop_of_interest, True)
        # check if the lines where added successful
        if add_2d_lines_result.status == False:
            message = "Failed to add 2D outline: {} to {} coarse detail family".format(family_config.room_type, add_2d_lines_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("...Nested {} coarse detail family extrusion created".format(family_config.room_type))

        # save the family to the output directory
        nested_coarse_detail_family_name = "GEN_Inner_Nested_{}_Coarse_{}_{}".format(family_config.room_type, get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_nested_coarse_family_result = save_as_family(
            doc=nested_coarse_detail_family_doc, 
            target_directory_path=family_config.output_directory, 
            current_full_file_name= nested_coarse_detail_family_name, 
            name_data=[[ nested_coarse_detail_family_name, nested_coarse_detail_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_nested_coarse_family_result.status == False:
            message = "Failed to save Nested {} coarse detail family: {}".format(family_config.room_type,save_nested_coarse_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("...Nested {} coarse detail family saved to: \n{}".format(family_config.room_type, family_config.output_directory))
        # close the family document
        nested_coarse_detail_family_doc.Close(False)

        # add the full host family path to the return value
        return_value.result = [nested_coarse_detail_family_name]
        return_value.append_message("Nested {} coarse detail family created successfully.".format(family_config.room_type))
    except Exception as e:
        message = "Failed to create coarse detail {} family: {}".format(family_config.room_type, e)
        return_value.update_sep(False, message)
    finally:
        # close the family document if it was opened
        if nested_coarse_detail_family_doc  and nested_coarse_detail_family_doc.IsValidObject:
            nested_coarse_detail_family_doc.Close(False)
    
    return return_value
   

def create_medium_and_fine_detail_family(doc, family_config):
    """
    Creates a medium and fine detail family based on the provided family config.
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_config: The family config object
    :type family_config: FamilyTypeConfig

    :return: Result class instance.

        - `result.status` (bool): True if the family was created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation.
        - `result.result` (list): File name of nested family.

    On exception:

        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.

    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()
    nested_medium_and_fine_family_doc = None
    nested_medium_and_fine_detail_family_name = None

    try:
        # open the medium and fine detail nested family and update the extrusion outline
        fam_result = open_family(doc, family_path=family_config.generic_nested_path)
        if fam_result.status == False:
            message = "Failed to create nested {} medium and fine detail family: {}".format(family_config.room_type, fam_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("...Nested {} medium and fine detail family created from template: \n{}".format(family_config.room_type, family_config.generic_nested_path))
        
        # get the family document
        nested_medium_and_fine_family_doc = fam_result.result[0]

        # update the extrusion outline
        # get the filled region curve loops...if there are two loops, use the inner loop only
        filled_region_curve_loops = family_config.curve_loops if len(family_config.curve_loops) == 1 else [family_config.curve_loops[1]]
        
        # create a new extrusion in the family
        create_extrusion_result = create_new_extrusion_from_outlines(
            nested_medium_and_fine_family_doc,  
            filled_region_curve_loops,
            None,  # provide none to have the default extrusion height of 10mm
            is_visible_coarse_detail = False,
        )
        # check if the update extrusion was successful
        if create_extrusion_result.status == False:
            message = "Failed to create new extrusion in nested {} medium and fine detail family : {}".format(family_config.room_type,create_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("...Nested {} medium and fine detail family extrusion created".format(family_config.room_type))
        
        # save the family to the output directory
        nested_medium_and_fine_detail_family_name = "GEN_Inner_Nested_{}_{}_{}".format(family_config.room_type, get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_nested_medium_and_fine_detail_family_result = save_as_family(
            doc=nested_medium_and_fine_family_doc, 
            target_directory_path=family_config.output_directory, 
            current_full_file_name= nested_medium_and_fine_detail_family_name, 
            name_data=[[ nested_medium_and_fine_detail_family_name, nested_medium_and_fine_detail_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_nested_medium_and_fine_detail_family_result.status == False:
            message = "Failed to save Nested {} medium and fine detail family: {}".format(family_config.room_type,save_nested_medium_and_fine_detail_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("...Nested {} medium and fine detail family saved to: {}".format(family_config.room_type,family_config.output_directory))
        
        # close the family document
        nested_medium_and_fine_family_doc.Close(False)

        # add the full host family path to the return value
        return_value.result = [nested_medium_and_fine_detail_family_name]
        return_value.append_message("Nested {} medium and fine  detail family created successfully.".format(family_config.room_type))

    except Exception as e:
        message = "Failed to create medium and fine detail {} family: {}".format(family_config.room_type, e)
        return_value.update_sep(False, message)
    finally:
        # close the family document if it was opened
        if nested_medium_and_fine_family_doc and  nested_medium_and_fine_family_doc.IsValidObject:
            nested_medium_and_fine_family_doc.Close(False)
    
    return return_value
