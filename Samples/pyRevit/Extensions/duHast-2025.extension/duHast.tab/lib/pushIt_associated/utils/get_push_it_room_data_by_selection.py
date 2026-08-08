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

from duHast.pyRevit.console_output import print_error

from pushIt_associated.utils.utilities import (
    get_unique_id_parameter,
    get_parameters_and_guids,
    get_push_it_data_source,
    get_family_instances_of_supported_categories,
    convert_family_instances_to_storage,
)

from pushIt_associated.place_revit_rooms.push_it_fam_analysis import get_push_it_families_centroid
from pushIt_associated.place_revit_rooms.user_selection import  get_push_it_room_selection

def get_push_it_rooms_data(push_it_elements_model, forms):
    """
    Get the pushIt rooms data from the selected model.

    :param push_it_elements_model: The model containing the pushIt elements.
    :return: A Result object containing the status and the pushIt rooms data.
    """

    # set up a status tracker
    return_value = Result()

    try:
        # read the settings file to get the configured data source ( CSV file or drofus property
        # mappings ) and enabled categories such as supported walls, doors, windows, etc.
        data_source = get_push_it_data_source()
        if data_source is None:
            message = "Invalid data source or supported categories"
            return_value.update_sep(False, message)
            print_error(message)
            return return_value

        supported_category_names = data_source.enabled_category_names

        # get the parameter guids for value transfers from the data source
        parameter_data = get_parameters_and_guids(data_source)
        if parameter_data is None or len(parameter_data) == 0:
            message = "No parameter data found in data source: {}".format(data_source.get_source_description())
            return_value.update_sep(False, message)
            print_error(message)
            return return_value

        # get the unique id parameter from the data source
        unique_id_parameter_name, unique_id_parameter_guid = get_unique_id_parameter(data_source)
        if unique_id_parameter_name is None or unique_id_parameter_guid is None:
            message = "No unique id parameter found in data source: {}".format(data_source.get_source_description())
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        
        # get the rooms from the pushIt model ( including parameter data )
        revit_family_instances_result = get_family_instances_of_supported_categories(push_it_elements_model,  supported_category_names)

        if revit_family_instances_result.status is False:
            message = "No family instances found in the selected model."
            return_value.update_sep(False, message)
            print_error(message)
            return return_value

        # convert revit family instances to storage so it can be displayed in the UI
        converted_fam_instances_result = convert_family_instances_to_storage(push_it_elements_model, revit_family_instances_result.result,parameter_data,  unique_id_parameter_guid, forms)
        if converted_fam_instances_result.status is False:
            message = "Family instances conversion failed: {}".format(converted_fam_instances_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value

        converted_fam_instances = converted_fam_instances_result.result
        return_value.append_message("Converted family instances: {} of {} ".format(len(converted_fam_instances), len((revit_family_instances_result.result))))
        
        # get the user to choose which rooms to place
        selected_rooms = get_push_it_room_selection(push_it_elements_model, converted_fam_instances,  unique_id_parameter_guid, forms)
        if selected_rooms is None or len(selected_rooms) == 0:
            message = "No rooms selected."
            return_value.update_sep(False, message)
            print_error("{} \nExiting".format(message))
            
            return return_value
        
        # give some user feedback
        return_value.append_message("Selected rooms to place: {} ".format(len(selected_rooms)))
        
        # analyze the rooms selected to place ( can I get the centroid of the room family from a link? )
        # not all rooms will return a centroid....
        updated_fams_result = get_push_it_families_centroid(push_it_elements_model,selected_rooms)

        # any family which failed here is dropped from the list, so if nothing came back
        # there is nothing left to place
        if updated_fams_result.result is None or len(updated_fams_result.result) == 0:
            message = "Failed to get the centroid of any of the {} selected rooms: {}".format(len(selected_rooms), updated_fams_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value

        # a failure on individual families is not fatal, carry on with the ones which made it
        # through but make sure the user knows some rooms will not get placed
        if updated_fams_result.status is False:
            message = "Failed to get the centroid of {} of {} selected rooms, those will not be placed: {}".format(
                len(selected_rooms) - len(updated_fams_result.result),
                len(selected_rooms),
                updated_fams_result.message,
            )
            return_value.append_message(message)
            print_error(message)

        # store the result
        return_value.result = updated_fams_result.result
    
    except Exception as e:
        message = "An error occurred while getting pushIt rooms data: {}".format(str(e))
        return_value.update_sep(False, message)
        print_error(message)

    return return_value