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
DEBUG = False


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
    translation, rotation = get_coordinate_system_translation_and_rotation(push_it_elements_model)

    if DEBUG:
        print("Translation: ", translation)
        print("Rotation: ", rotation)


    # place the rooms in the current model and transfer the parameter data
    create_result = create_rooms_from_push_it_instances(
        doc, 
        get_data_result.result, 
        rotation=rotation, 
        translation=translation
    )
    
    # check if any errors occurred during the creation of the rooms
    if( create_result.status is False):
        message = "Room creation failed: {}".format(create_result.message)
        return_value.update_sep(False, message)
        print_error(message)
        return return_value
    
    print("Created: {} rooms".format(len(create_result.result)))


    print("finished!")

