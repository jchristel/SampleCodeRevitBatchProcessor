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

from pushIt_associated.utils.get_push_it_room_data_by_selection import get_push_it_rooms_data
from pushIt_associated.area_by_room_verification.update_pushit_rooms import  update_push_it_instances_from_rooms


def push_it_area_by_room_verification_entry(doc, uiapp,output, forms):
    """
    This function places a revit room into the same location as a push it room and writes the area of the Revit room into the mock room.
    
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

    print_header("Update PushIt rooms by area verification.")

    push_it_elements_model = doc

    # get push it data
    get_data_result = get_push_it_rooms_data(push_it_elements_model, forms)
    # check we got data
    if( get_data_result.status is False):
        message = "PushIt data retrieval failed: {}".format(get_data_result.message)
        return_value.update_sep(False, message)
        print_error(message)
        return return_value

    # update: this is not required since we are assuming the push it elements are in the same model as the revit rooms
    # use None for rotation and translation instead 
    rotation, translation = None, None

    # place the rooms in the current model and transfer the parameter data
    create_and_update_result =  update_push_it_instances_from_rooms(doc, get_data_result.result, rotation=rotation, translation=translation)
    
    # check if any errors occurred during the creation of the rooms
    if( create_and_update_result.status is False):
        message = "Room creation failed: {}".format( create_and_update_result.message)
        return_value.update_sep(False, message)
        #print_error(message)
        return return_value
    
    print("Successfully updated push it rooms")

    print("finished!")