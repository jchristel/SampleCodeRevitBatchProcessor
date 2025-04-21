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
from duHast.Utilities.utility import get_current_user_name
from duHast.Utilities.date_stamps import get_file_date_stamp, FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC

from duHast.Revit.Common.file_io import  save_as_family, get_family_from_template
from duHast.Revit.DetailItems.filled_regions import  get_filled_region_curve_loops
from duHast.Revit.Family.family_reload import reload_all_families

from pushIt_associated.get_a_room import settings
from pushIt_associated.get_a_room.nested_family_utils import create_new_extrusion_from_outlines, add_2D_outline
from pushIt_associated.get_a_room.host_family_utils import rename_nested_families, hook_up_shared_parameters, update_overall_dimension_parameter_values
from pushIt_associated.get_a_room.Objects.FamilyTypeConfig import FamilyTypeConfig

def create_get_a_room_family(doc, family_config):
    
    # set up a status tracker
    return_value = Result()

    # setup family place holders
    nested_medium_and_fine_family_doc = None
    nested_coarse_detail_family_doc = None
    wall_host_family_doc = None

    try:
        
        # type checking
        if(not isinstance(family_config, FamilyTypeConfig)):
            message = "FamilyTypeConfig object is not valid: {}".format(type(family_config))
            return_value.update_sep(False, message)
            return return_value
        
        # open the medium and fine detail nested family and update the extrusion outline
        fam_result = get_family_from_template(doc, family_template_path=family_config.generic_nested_path)
        if fam_result.status == False:
            message = "Failed to create nested {} medium and fine detail family: {}".format(family_config.room_type, fam_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Nested {} medium and fine detail family created from template: \n{}".format(family_config.room_type, family_config.generic_nested_path))
        
        # get the family document
        nested_medium_and_fine_family_doc = fam_result.result[0]

        # update the extrusion outline
        # get the filled region curve loops
        filled_region_curve_loops = get_filled_region_curve_loops(family_config.filled_region)
        
        # create a new extrusion in the family
        create_extrusion_result = create_new_extrusion_from_outlines(
            nested_medium_and_fine_family_doc,  
            filled_region_curve_loops,
            settings.HEIGHT_PARAMETER_NAME,
            is_visible_coarse_detail = False,
        )
        # check if the update extrusion was successful
        if create_extrusion_result.status == False:
            message = "Failed to create new extrusion in nested {} medium and fine detail family : {}".format(family_config.room_type,create_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Nested {} medium and fine detail family extrusion created".format(family_config.room_type))
        
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

        return_value.append_message("Nested {} medium and fine detail family saved to: {}".format(family_config.room_type,family_config.output_directory))
        # close the family document
        nested_medium_and_fine_family_doc.Close(False)

        # open the bay nested family coarse template
        fam_result_coarse = get_family_from_template(doc, family_template_path=settings.FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE_PATH )
        if fam_result_coarse.status == False:
            message =  "Failed to create nested {} coarse detail family: {}".format(family_config.room_type,fam_result_coarse.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Nested {} coarse detail family created from template: \n{}".format(family_config.room_type, family_config.generic_nested_coarse_path))
        # get the family document
        nested_coarse_detail_family_doc = fam_result_coarse.result[0]

        # update the extrusion outline
        create_extrusion_result = create_new_extrusion_from_outlines(
            nested_coarse_detail_family_doc,  
            filled_region_curve_loops,
            settings.HEIGHT_PARAMETER_NAME,
            is_visible_coarse_detail=True,
        )
        
        # check if the update extrusion was successful
        if create_extrusion_result.status == False:
            message = "Failed to create new extrusion in nested {} coarse detail family : {}".format(family_config.room_type, create_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Nested {} coarse detail family extrusion created".format(family_config.room_type))
       
        # update add 2D lines
        add_2d_lines_result = add_2D_outline(nested_coarse_detail_family_doc,  filled_region_curve_loops, True)
        # check if the lines where added successful
        if add_2d_lines_result.status == False:
            message = "Failed to add 2D outline: {} to {} coarse detail family".format(family_config.room_type, add_2d_lines_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Nested {} coarse detail family extrusion created".format(family_config.room_type))

        # save the family to the output directory
        nested_coarse_detail_family_name = "GEN_Inner_Nested_{}_Coarse_{}_{}".format(family_config.room_type, get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_nested_bay_coarse_family_result = save_as_family(
            doc=nested_coarse_detail_family_doc, 
            target_directory_path=family_config.output_directory, 
            current_full_file_name= nested_coarse_detail_family_name, 
            name_data=[[ nested_coarse_detail_family_name, nested_coarse_detail_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_nested_bay_coarse_family_result.status == False:
            message = "Failed to save Nested {} coarse detail family: {}".format(family_config.room_type,save_nested_bay_coarse_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Nested {} coarse detail family saved to: \n{}".format(family_config.room_type, family_config.output_directory))
        # close the family document
        nested_coarse_detail_family_doc.Close(False)

        # open the bay wall family template
        fam_wall_result = get_family_from_template(doc, family_template_path=family_config.wall_host_path)
        if fam_wall_result.status == False:
            message = "Failed to create host {} family: {}".format(family_config.room_type,fam_wall_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Host {} family created from template: \n{}".format(family_config.room_type,family_config.wall_host_path))
        # get the family document
        wall_host_family_doc = fam_wall_result.result[0]

        # reload the nested families
        # first rename the current families with the new names
        family_name_mapper = {
            family_config.generic_nested_name: nested_medium_and_fine_detail_family_name,
            family_config.generic_nested_coarse_name: nested_coarse_detail_family_name,
        }
        rename_result = rename_nested_families(doc=wall_host_family_doc, family_name_mapper=family_name_mapper)
        # check if the rename was successful
        if rename_result.status == False:
            message = "Wall {} host family: Failed to rename nested families: {}".format(family_config.room_type, rename_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Wall {} host family: nested families renamed.".format(family_config.room_type))

        # reload the nested families
        reload_result = reload_all_families(
            doc=wall_host_family_doc,
            library_location=family_config.output_directory,
            include_sub_folders=False,
        )

        # check if the rename was successful
        if reload_result.status == False:
            message = "Wall {} host family: Failed to reload nested families: {}".format(family_config.room_type,reload_result.message)
            return_value.update_sep(False, message)
            return return_value
        return_value.append_message("Wall {} host family: Reloaded nested families successfully".format(family_config.room_type))

        # hook up shared parameters to nested families
        hook_up_result = hook_up_shared_parameters(doc=wall_host_family_doc)
        return_value.update(hook_up_result)

        # update the with and depth  parameters based on filled region bounding box dims
        # update the height parameter ( set to 2.7m default)
        update_overall_dims_result = update_overall_dimension_parameter_values(
            doc=wall_host_family_doc, 
            bounding_box=family_config.bounding_box, 
            filled_region=family_config.filled_region,
        )
        
        # check if the update was successful
        if update_overall_dims_result.status == False:
            message = "Wall {} host family: Failed to update overall dimension parameters: {}".format(family_config.room_type, update_overall_dims_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Wall {} host family: Updated overall dimension successfully".format(family_config.room_type))
        
        # save the wall family to the output directory first
        wall_host_family_name = "WLL_{}_{}_{}".format(family_config.room_type, get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_wall_host_family_result = save_as_family(
            doc=wall_host_family_doc, 
            target_directory_path=family_config.output_directory, 
            current_full_file_name= wall_host_family_name, 
            name_data=[[ wall_host_family_name,wall_host_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_wall_host_family_result.status == False:
            message = "Wall {} host family: Failed to save family: {}".format(family_config.room_type, save_wall_host_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Wall {} host family: Saved family successfully".format(family_config.room_type))
        
        # close the wall family document
        wall_host_family_doc.Close(False)

        # add the full host family path to the return value
        return_value.result = ["{}{}.rfa".format(family_config.output_directory, wall_host_family_name)]

    except Exception as e:
        message = "Failed to create {} family: {}".format(family_config.room_type, e)
        return_value.update_sep(False, message)
    return return_value