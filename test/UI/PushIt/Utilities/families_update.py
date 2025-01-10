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
from PushIt.Models.Room import Room
from PushIt.Utilities.shared_parameters import set_shared_parameter_value_by_guid


def update_single_family(doc, family_instance, room, shared_parameter_data):

    # expects a family instance and a room object
    if isinstance(room, Room) == False:
        raise TypeError(
            "room needs to be of type Room. Got {} instead".format(type(room))
        )

    # set up place holder for the area designed value
    area_designed = get_parameter_value_by_name(
        family_instance, shared_parameter_data[2].keys()[0]
    )

    # set up an action which can be executed in a transaction which updates the family instance parameters
    def action():
        action_return_value = Result()
        try:
            # update the room id
            action_return_value.update(
                set_shared_parameter_value_by_guid(
                    doc, family_instance, room.id.parameter_guid, room.id.value
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

            # read the area designed value

        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to update family instance parameters: {}".format(e)
            )

        return action_return_value

    # TODO: read the area designed value !!
    # expects and RFamiliy object in Result.result list
    return_value = Result()

    return return_value
