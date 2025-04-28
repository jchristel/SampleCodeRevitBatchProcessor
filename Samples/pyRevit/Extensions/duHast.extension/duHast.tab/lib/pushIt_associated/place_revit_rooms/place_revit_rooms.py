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
from duHast.pyRevit.console_output import print_header, print_error


from pushIt_associated.place_revit_rooms.user_selection import get_model_selection


from pushIt_associated.utilities import (
    get_unique_id_parameter_from_data_file,
    get_parameters_and_guids_from_data_file,
    get_data_path_and_supported_categories, 
    get_family_instances_of_supported_categories,
    convert_family_instances_to_storage,
)


def place_revit_rooms_entry(doc, uiapp,output, forms):
    """
    This function places revit rooms in the current Revit model based on pushIt rooms.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The Revit UI application
    :type uiapp: Autodesk.Revit.UI.UIApplication
    :param output: The pyRevit output window
    :type output: pyRevit.output
    :param forms: The pyRevit forms module
    :type forms: pyRevit.forms
    :return: Result class instance.

        - `result.status` (bool): True if the families where created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation.
        - `result.result` (list): File path to wall host family.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """
    
    # set up a status tracker
    return_value = Result()

    print_header("Place Revit rooms.")

    # get the user to select whether to use this model or a link to get the rooms from
    push_it_elements_model = get_model_selection(doc, forms=forms)
    if push_it_elements_model is None:
        message = "No model selected."
        return_value.update_sep(False, message)
        print_error(message)
        return return_value

    print("Selected model: ", push_it_elements_model.Title)

    # read the settings file to get categories such as supported walls, doors, windows, etc. and the data path
    data_path, supported_category_names = get_data_path_and_supported_categories()
    if data_path is None or supported_category_names is None:
        message = "Invalid data path or supported categories"
        return_value.update_sep(False, message)
        print_error(message)
        return return_value

    # read the current SoA file and get the parameter guids for value transfers
    parameter_data = get_parameters_and_guids_from_data_file(data_path)
    #print("Parameter data: ", parameter_data)

    # get the unique id parameter from the data file
    unique_id_parameter_name, unique_id_parameter_guid = get_unique_id_parameter_from_data_file(data_path)
    
    # get the rooms from the pushIt model ( including parameter data )
    revit_family_instances_result = get_family_instances_of_supported_categories(doc,  supported_category_names)

    if revit_family_instances_result.status is False:
        message = "No family instances found in the selected model."
        return_value.update_sep(False, message)
        print_error(message)
        return return_value

    # convert revit family instances to storage so it can be displayed in the UI
    converted_fam_instances_result = convert_family_instances_to_storage(doc, revit_family_instances_result.result,parameter_data,  unique_id_parameter_guid, forms)
    if converted_fam_instances_result.status is False:
        message = "Family instances conversion failed: {}".format(converted_fam_instances_result.message)
        return_value.update_sep(False, message)
        print_error(message)
        return return_value

    converted_fam_instances = converted_fam_instances_result.result
    print("Converted family instances: {} of {} ".format(len(converted_fam_instances), len((revit_family_instances_result.result))))
    
    # get the user to choose which rooms to place
    
    # analyze the rooms selected to place ( can I get the centroid of the room family from a link? )
    
    # place the rooms in the current model and transfer the parameter data

