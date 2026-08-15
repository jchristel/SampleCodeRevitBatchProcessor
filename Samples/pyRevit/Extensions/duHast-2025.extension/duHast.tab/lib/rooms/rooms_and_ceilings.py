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


from rooms.ceilings_create import create_ceiling_by_room


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



def ceilings_to_rooms_entry(doc, output, forms):
    """
    Creates a ceiling matching the boundary of each user selected room.

    The ceiling type is resolved from the room's ceiling finish parameter, falling back to a
    default type. Ceiling elevation and the phase the ceiling is created in are set by the
    module level constants.

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

        print_header("Ceiling by rooms.")

        # get user selected library reports
        print("Select rooms to model ceilings for:")

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
            element_selection_description="Select rooms to create ceilings for",
            ui_element_name_builder= action,
        )

        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Adding ceilings: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            # iterate over the selected room ids
            for i, room_id in enumerate(selected_room_ids):
                # get the room element
                room = doc.GetElement(room_id)

                # build the room name
                room_name = room_name_builder_ui(doc, element=room)

                # print the room name to the console
                print_header("Processing room: {}".format(room_name))

                # create the ceiling by room
                process_room_result = create_ceiling_by_room(doc, room)
                print(process_room_result.message)


                # cancelled?
                if pb.cancelled:
                    message = "User cancelled."
                    print_error(message)
                    return_value.update_sep(False, message=message)
                    # leave loop
                    break

                # update progress bar
                pb.update_progress(i, len(selected_room_ids))
                


    except Exception as e:
        return_value.update_sep(
            False, "Failed to draw ceilings by room: {}".format(e)
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value
