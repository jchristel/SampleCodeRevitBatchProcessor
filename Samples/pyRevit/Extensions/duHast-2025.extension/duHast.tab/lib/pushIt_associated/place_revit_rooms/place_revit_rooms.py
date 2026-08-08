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
from duHast.Revit.Common.Geometry.geometry import get_coordinate_system_translation_and_rotation

from pushIt_associated.place_revit_rooms.user_selection import get_model_selection
from pushIt_associated.utils.get_push_it_room_data_by_selection import get_push_it_rooms_data
from pushIt_associated.place_revit_rooms.create_rooms import create_rooms_from_push_it_instances

# debug flag
DEBUG = True

def get_model_insertion_method(forms):
    """
    Get the model insertion method from the user.

    :return: The model insertion method.
    :rtype: str
    """
    ops = ["Origin to Origin","By Shared Coordinates"]
    configs = {
        "Origin to Origin": {"background": "#FF0000"},
        "By Shared Coordinates" : {"background": "#00FF00"},
    }
    ui_options = forms.CommandSwitchWindow.show(
            ops,  message="Select the model insertion method.", config=configs
        )
    
    if ui_options is None:
        message = "No model insertion method selected."
        print_error(message)
        return None
    
    if ui_options == "Origin to Origin":
        print("Selected model insertion method: {}".format(ui_options))
        return True
    else:
        print("Selected model insertion method: {}".format(ui_options))
        return False
    

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

        - `result.status` (bool): True if the rooms where created and all parameter data transferred successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation.
        - `result.result` (list): The rooms created.
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

    print("Selected model: {}".format(push_it_elements_model.Title))

    # get push it data
    get_data_result = get_push_it_rooms_data(push_it_elements_model, forms)
    # check we got data
    if( get_data_result.status is False):
        message = "PushIt data retrieval failed: {}".format(get_data_result.message)
        return_value.update_sep(False, message)
        print_error(message)
        return return_value

    # get rotation and translation of the coordinate system
    # this is the translation and rotation of the coordinate system of the pushIt model
    # not required if models are linked using origin to origin, but if the models are linked using shared coordinates, this is required to place the rooms in the correct location
    model_insertion_method = get_model_insertion_method(forms)
    
    if model_insertion_method is None:
        message = "No model insertion method selected."
        return_value.update_sep(False, message)
        print_error(message)
        return return_value
    
    translation, rotation = None, None
    
    if model_insertion_method is False:
        translation, rotation = get_coordinate_system_translation_and_rotation(push_it_elements_model)
    

    if DEBUG:
        print("Translation: ", translation)
        print("Rotation: ", rotation)


    # place the rooms in the current model and transfer the parameter data
    create_result = create_rooms_from_push_it_instances(
        doc, 
        get_data_result.result, 
        rotation=rotation, 
        translation=translation,
        forms=forms
    )
    
    # report how many rooms made it into the model before checking the status
    # a room can be created but still fail to receive all its parameter values
    print("Created: {} rooms".format(len(create_result.result)))

    # drop the per room creation confirmation, otherwise it drowns out anything worth reading
    messages_of_interest = [
        message
        for message in create_result.message_as_list
        if message != "Room created successfully."
    ]

    # check if any errors occurred during the creation of the rooms or the transfer of parameter values
    if( create_result.status is False):
        message = "Room creation failed: {}".format("\n".join(messages_of_interest))
        return_value.update_sep(False, message)
        print_error(message)
        return return_value

    if DEBUG:
        for message in messages_of_interest:
            print(message)

    # store the created rooms so a caller can act on them
    return_value.result = create_result.result
    return_value.append_message("Created: {} rooms".format(len(create_result.result)))

    print("finished!")

    return return_value

