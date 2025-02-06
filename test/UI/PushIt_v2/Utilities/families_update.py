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


from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Revit.Common.failure_handling import process_failures
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)

from PushIt_v2.Models.Room import Room
from PushIt_v2.Utilities.shared_parameters import set_shared_parameter_value_by_guid
from PushIt_v2.Utilities.families_get import extract_single_family_data
from duHast.Utilities.date_stamps import get_date_stamp, FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC

from Autodesk.Revit.DB import Transaction

def update_single_family(doc, family_instance, room, shared_parameter_data, safety_off=False):
    """
    Updates a single family instance with room data

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: The family instance to be updated.
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :param room: The room data.
    :type room: Room
    :param shared_parameter_data: The shared parameter data.
    :type shared_parameter_data: [SharedParameterData]

    :return: Result class instance.
    :rtype: Result
    """
    
    return_value = Result()

    # expects a family instance and a room object
    if isinstance(room, Room) == False:
        raise TypeError(
            "room needs to be of type Room. Got {} instead".format(type(room))
        )

    # set up an action which can be executed in a transaction which updates the family instance parameters
    def action():
        action_return_value = Result()
        try:
            
            room_id = room.id.id
            # check safety off?
            if safety_off :
                user_name = doc.Application.Username
                # append the date stamp to the room id
                room_id = "{}::{}<{}>".format(room_id, user_name, get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
            
            # update the room id
            action_return_value.update(
                set_shared_parameter_value_by_guid(
                    doc, family_instance, room.id.parameter_guid, room_id
                )
            )

            # update the area briefed
            action_return_value.update(
                set_shared_parameter_value_by_guid(
                    doc, family_instance, room.area_briefed.parameter_guid, room.area_briefed.value
                )
            )

            # update the other properties
            for other_property in room.other_properties:
                action_return_value.update(
                    set_shared_parameter_value_by_guid(
                        doc, family_instance, other_property.parameter_guid, other_property.value
                    )
                )
            action_return_value.append_message("Updated family instance parameters")

        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to update family instance parameters: {}".format(e)
            )

        return action_return_value

    # set up a transaction
    transaction = Transaction(
                doc,
                "pushing it: {}".format(
                    room.id.id
                ),
            )
    
    # execute the action in a transaction
    dummy = in_transaction_with_failure_handling(
        transaction= transaction, 
        action=action, 
        failure_config = FailureHandlingConfig(), 
        failure_processing_func = process_failures)
    
    return_value.update(dummy)

    # get the family data after the update
    family_after_update = extract_single_family_data(
        doc=doc, 
        family_instance=family_instance, 
        shared_parameter_data=shared_parameter_data
    )
    
    return_value.result.append(family_after_update)

    return return_value
