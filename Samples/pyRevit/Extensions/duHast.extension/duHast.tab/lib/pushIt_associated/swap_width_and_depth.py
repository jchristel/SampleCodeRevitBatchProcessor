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

from duHast.Revit.UI.custom_selection_user import get_user_selection
from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name
from duHast.Revit.Common.parameter_set_utils import set_parameter_value_by_name
from duHast.Revit.Family.family_instance_translate import rotate_around_origin, RADIAN_ANGLE_90DEGREES
from duHast.Revit.Common.transaction import in_transaction

# parameter pairs to swap values for
PARAMETER_VALUE_SWAP_MAPPING = [["HSL_WIDTH", "HSL_DEPTH"]]

# categories to be supported by the command ( should b read from settings in future version!)
SUPPORTED_CATEGORIES = ["Walls","Columns"]


def selection_filter(elem):
    """
    Returns True if the element is of supported categories, otherwise False.

    :param elem: A revit element
    :type elem: Autodesk.Revit.DB.Element
    :return: True if the element is of supported categories, otherwise False
    :rtype: bool
    """

    if elem.Category.Name in SUPPORTED_CATEGORIES:
        return True
    else:
        return False


def swap_element_parameter_values(elem, parameter_value_swap_mapping):

    # read the elements instance parameters to be swapped
    for param_pair in parameter_value_swap_mapping:
        # get the parameter values
        param1_value = get_parameter_value_by_name(elem, param_pair[0])
        param2_value = get_parameter_value_by_name(elem, param_pair[1])

        # if the value does not exist on the selected element its None
        if param1_value is None or param2_value is None:
            print("One of the parameters [{}, {}] does not exist on the selected element. Ignoring pairing".format(param_pair[0], param_pair[1]))
            continue

        # set the revised parameter values
        print("Swapping values for element: {} - {} and {} - {}".format(param_pair[0], param1_value, param_pair[1], param2_value))

        try:
            # set the revised parameter values
            set_result1 = set_parameter_value_by_name(elem, param_pair[0], param2_value)
            set_result2 = set_parameter_value_by_name(elem, param_pair[1], param1_value)

            # check if the parameter values where set
            if set_result1.status == True and set_result2.status == True:
                print("Swapped values for element: {} - {} and {} - {}".format(param_pair[0], param1_value, param_pair[1], param2_value))
            elif set_result1.status == False or set_result2.status == False:
                print("Failed to swap values for element: {} - {} and {} - {}".format(param_pair[0], param1_value, param_pair[1], param2_value))
                print("Failed to set parameter values: {} and {}".format(set_result1.message, set_result2.message))


            # rotate the element by 90 degrees
            if set_result1.status == True and set_result2.status == True:
                rotate_result = rotate_around_origin(elem, RADIAN_ANGLE_90DEGREES, in_transaction)
                if rotate_result.status == True:
                    print("Rotated element by 90 degrees")
                elif rotate_result.status == False:
                    print("Failed to rotate element by 90 degrees: {}".format(rotate_result.message))

        except Exception as e:
            print("Failed to swap values for element: {} - {} and {} - {}".format(param_pair[0], param1_value, param_pair[1], param2_value))
            print("Exception: {}".format(e))
            continue


def swap_width_and_depth_entry(doc,  uiapp, output, forms):
    """
    Reports on families in a library location based on xml part atom exports.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """
    
    # set up a status tracker
    return_value = Result()

    # get user to select push it rooms
    mock_rooms_selected_result = get_user_selection(
        doc=doc,
        uidoc=uiapp.ActiveUIDocument,
        ui_text="Select push it rooms",
        selection_filter=selection_filter,
    )

    # check if mock rooms where selected
    if mock_rooms_selected_result.status == False:
        return_value.update(mock_rooms_selected_result)
        print("Failed to select rooms: {}".format(mock_rooms_selected_result.message))
        return return_value

    # get the actual push it mock rooms selected
    mock_rooms_selected = mock_rooms_selected_result.result[0]
    if len(mock_rooms_selected) == 0:
        message = "No push it where selected."
        return_value.update_sep(False, message)
        print(message)
        return return_value
    
    # set up a progress counter
    counter = 1

    # set up progress bar and start swapping
    with forms.ProgressBar(
        title="Swapping: {value} of {max_value}",
        cancellable=True,
    ) as pb:
        
        for mock_room_elem in mock_rooms_selected:
            pb.update_progress(len( mock_rooms_selected), len(mock_rooms_selected))
            
            swap_element_parameter_values(mock_room_elem, PARAMETER_VALUE_SWAP_MAPPING)
            
            # update progress
            counter = counter + 1
            
            # cancelled?
            if pb.cancelled:
                message = "User cancelled."
                print(message)
                return_value.update_sep(False, message=message)
                # leave loop
                break
    