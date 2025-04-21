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
from pushIt_associated.get_a_room.nested_families import create_new_extrusion_from_outlines, add_2D_outline
from pushIt_associated.get_a_room.host_family import rename_nested_families, hook_up_shared_parameters, update_overall_dimension_parameter_values

def create_bay_family(doc, filled_region, bounding_box, output_directory):
    
    # set up a status tracker
    return_value = Result()

    # setup family place holders
    bay_nested_family_doc = None
    bay_nested_coarse_family_doc = None
    bay_wall_family_doc = None

    try:
        # open the bay nested family and update the extrusion outline
        fam_result = get_family_from_template(doc, family_template_path=settings.FAMILY_TEMPLATE_GENERIC_BAY_NESTED_PATH)
        if fam_result.status == False:
            message = "Failed to create bay family: {}".format(fam_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Bay family created from template: {}".format(settings.FAMILY_TEMPLATE_GENERIC_BAY_NESTED_PATH))
        # get the family document
        bay_nested_family_doc = fam_result.result[0]

        # update the extrusion outline
        # get the filled region curve loops
        filled_region_curve_loops = get_filled_region_curve_loops(filled_region)
        
        # create a new extrusion in the family
        update_extrusion_result = create_new_extrusion_from_outlines(
            bay_nested_family_doc,  
            filled_region_curve_loops[0],
            settings.HEIGHT_PARAMETER_NAME,
            is_visible_coarse_detail = False,
        )
        # check if the update extrusion was successful
        if update_extrusion_result.status == False:
            message = "Failed to update extrusion outline: {}".format(update_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay family extrusion outline updated")
        # save the family to the output directory
        nested_bay_family_name = "GEN_Inner_Nested_Bay_{}_{}".format(get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_nested_bay_family_result = save_as_family(
            doc=bay_nested_family_doc, 
            target_directory_path=output_directory, 
            current_full_file_name= nested_bay_family_name, 
            name_data=[[ nested_bay_family_name, nested_bay_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_nested_bay_family_result.status == False:
            message = "Failed to save bay family: {}".format(save_nested_bay_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Nested Bay family saved to: {}".format(output_directory))
        # close the family document
        bay_nested_family_doc.Close(False)

        # open the bay nested family coarse template
        fam_result_bay_coarse = get_family_from_template(doc, family_template_path=settings.FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE_PATH )
        if fam_result_bay_coarse.status == False:
            message = "Failed to create nested bay coarse family: {}".format(fam_result_bay_coarse.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay coarse family created from template: \n{}".format(settings.FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE_PATH))
        # get the family document
        bay_nested_coarse_family_doc = fam_result_bay_coarse.result[0]

        # update the extrusion outline
        update_extrusion_result = create_new_extrusion_from_outlines(
            bay_nested_coarse_family_doc,  
            filled_region_curve_loops[0],
            settings.HEIGHT_PARAMETER_NAME,
            is_visible_coarse_detail=True,
        )
        
        # check if the update extrusion was successful
        if update_extrusion_result.status == False:
            message = "Failed to update extrusion outline: {}".format(update_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay coarse family extrusion outline updated")
       
        # update add 2D lines
        add_2d_lines_result = add_2D_outline(bay_nested_coarse_family_doc,  filled_region_curve_loops[0])
        # check if the lines where added successful
        if add_2d_lines_result.status == False:
            message = "Failed to add 2D outline: {}".format(add_2d_lines_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay coarse family outline updated")

        # save the family to the output directory
        nested_bay_coarse_family_name = "GEN_Inner_Nested_Bay_Coarse_{}_{}".format(get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_nested_bay_coarse_family_result = save_as_family(
            doc=bay_nested_coarse_family_doc, 
            target_directory_path=output_directory, 
            current_full_file_name= nested_bay_coarse_family_name, 
            name_data=[[ nested_bay_coarse_family_name, nested_bay_coarse_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_nested_bay_coarse_family_result.status == False:
            message = "Failed to save coarse bay family: {}".format(save_nested_bay_coarse_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Nested Bay coarse family saved to: {}".format(output_directory))
        # close the family document
        bay_nested_coarse_family_doc.Close(False)

        # open the bay wall family template
        fam_wall_result = get_family_from_template(doc, family_template_path=settings.FAMILY_TEMPLATE_WALL_BAY_PATH)
        if fam_wall_result.status == False:
            message = "Failed to create wall bay family: {}".format(fam_wall_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Bay wall family created from template: {}".format(settings.FAMILY_TEMPLATE_WALL_BAY_PATH))
        # get the family document
        bay_wall_family_doc = fam_wall_result.result[0]

        # reload the nested families
        # first rename the current families with the new names
        family_name_mapper = {
            settings.FAMILY_TEMPLATE_GENERIC_BAY_NESTED: nested_bay_family_name,
            settings.FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE: nested_bay_coarse_family_name,
        }
        rename_result = rename_nested_families(doc=bay_wall_family_doc, family_name_mapper=family_name_mapper)
        # check if the rename was successful
        if rename_result.status == False:
            message = "Failed to rename nested families: {}".format(rename_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay wall family: nested families renamed.")

        # reload the nested families
        reload_result = reload_all_families(
            doc=bay_wall_family_doc,
            library_location=output_directory,
            include_sub_folders=False,
        )

        # check if the rename was successful
        if reload_result.status == False:
            message = "Failed to reload nested families: {}".format(reload_result.message)
            return_value.update_sep(False, message)
            return return_value
        return_value.append_message("Reloaded nested families successfully")

        # hook up shared parameters to nested families
        hook_up_result = hook_up_shared_parameters(doc=bay_wall_family_doc)

        # update the with and depth  parameters based on filled region bounding box dims
        # update the height parameter ( set to 2.7m default)
        update_overall_dims_result = update_overall_dimension_parameter_values(
            doc=bay_wall_family_doc, bounding_box=bounding_box, filled_region=filled_region)
        
        # check if the update was successful
        if update_overall_dims_result.status == False:
            message = "Failed to update overall dimension parameters: {}".format(update_overall_dims_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        # save the wall family to the output directory first
        wall_bay_family_name = "WLL_Bay_{}_{}".format(get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_wall_bay_family_result = save_as_family(
            doc=bay_wall_family_doc, 
            target_directory_path=output_directory, 
            current_full_file_name= wall_bay_family_name, 
            name_data=[[ wall_bay_family_name,wall_bay_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_wall_bay_family_result.status == False:
            message = "Failed to save wall bay family: {}".format(save_wall_bay_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        # close the wall family document
        bay_wall_family_doc.Close(False)

        # add the family path to the result object and return it
        return_value.append_message("Bay wall family saved to: {}".format(output_directory))
        return_value.result.append("{}{}.rfa".format(settings.FAMILY_OUT_DIRECTORY, wall_bay_family_name))

    except Exception as e:
        message = "Failed to create bay family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value