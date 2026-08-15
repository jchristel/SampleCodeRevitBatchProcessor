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
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user
from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Revit.Rooms.room_common_parameters import get_room_num_name_comb, get_room_level, get_room_phase

from rooms.wall_utils import (
    get_wall_segments_of_rooms,  
    build_segment_and_room_to_wall_id,
    update_walls_with_room_number_of_longest_segment,
    get_wall_parameters,
    get_wall_parameter_by_id,
)

from Autodesk.Revit.DB import Element, SharedParameterElement

def room_name_builder_ui(doc, element):
    """
    Builds the room name using the provided string.

    :param element: The room element.
    :type element: Autodesk.Revit.DB.Element
    :param sheet_name_string: The string to build the sheet name.
    :type sheet_name_string: str
    :return: The built sheet name.
    :rtype: str
    """

    
    room_name = []

    room_name.append(get_room_num_name_comb(element))
    room_name.append(get_room_phase(doc, element))
    room_name.append(get_room_level(doc, element))

    # join the chunks with a space and return the sheet name
    room_name_string = "_".join(room_name)

    # Build the sheet name using the provided string
    return room_name_string


def walls_to_rooms_entry(doc, output, forms):
    """
    Writes the room number into a user selected parameter on the walls bounding each user
    selected room.

    Where a wall bounds more than one room, the room with the longest shared boundary segment
    wins.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if families where reported without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:

        print_header("Walls by rooms.")

        # get user selected library reports

        def action(element):
            """
            Action to be performed on each element in the selection.

            :param element: The selected element.
            :type element: Autodesk.Revit.DB.Element
            """
            return  room_name_builder_ui(doc, element=element) 

        # get the user to select which sheet to export
        selected_room_ids=get_element_selection_from_user(
            doc=doc,
            forms=forms,
            element_getter=get_all_rooms,
            element_selection_description="Select rooms to find walls for",
            ui_element_name_builder= action,
        )

        # convert ids to rooms
        if not selected_room_ids or len(selected_room_ids) == 0:
            message = "No rooms selected."
            print_error(message)
            return_value.update_sep(False, message=message)
            return return_value

        # convert selected ids to rooms
        rooms_selected = [doc.GetElement(room_id) for room_id in selected_room_ids]

        def action_para_selection(element):
            key = "{} ({})".format(element.Definition.Name, element.Id)
            return key
           
        # get a target parameter name
        selected_parameter_ids=get_element_selection_from_user(
            doc=doc,
            forms=forms,
            element_getter=get_wall_parameters,
            element_selection_description="Select wall target parameter to update with room number",
            multiselect = False,
            ui_element_name_builder=action_para_selection,
        )

        # check if the user selected a parameter
        if not selected_parameter_ids:
            message = "No parameter selected."
            print_error(message)
            return_value.update_sep(False, message=message)
            return return_value
        
        selected_parameter = get_wall_parameter_by_id (doc,selected_parameter_ids[0])
        if not selected_parameter:
            message = "Selected parameter not found in document."
            print_error(message)
            return_value.update_sep(False, message=message)
            return return_value

        target_parameter_name = None

        if(isinstance(selected_parameter, SharedParameterElement)):
           target_parameter_name = Element.Name.GetValue(selected_parameter)
        else:
            target_parameter_name = selected_parameter.Definition.Name
        
        print("\nSelected parameter: {}".format(target_parameter_name))

        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Processing rooms: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            # get the room segments
            wall_segments_result = get_wall_segments_of_rooms(doc=doc, rooms= rooms_selected, pb=pb)

            # check if the result is successful
            if not wall_segments_result.status:
                return_value.update_sep(False, "Failed to get wall segments: {}".format(wall_segments_result.message))
                return return_value
            
            # give user feed back
            print("\nFound {} rooms with wall segments".format(len(wall_segments_result.result[0])))

            # loop over wall id and length by room and build a dictionary of room number and wall id and length
            segment_length_and_room_by_wall_id = build_segment_and_room_to_wall_id(wall_segments_result.result[0])

            # give user feed back
            #print("\n", segment_length_and_room_by_wall_id)

            # update the walls with the room number of the longest segment the wall is bounding a room by
            update_result= update_walls_with_room_number_of_longest_segment(
                doc, 
                segment_length_and_room_by_wall_id, 
                pb, 
                target_parameter_name
            )
            print(update_result)


    except Exception as e:
        return_value.update_sep(
            False, "Failed to find walls by room: {}".format(e)
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value