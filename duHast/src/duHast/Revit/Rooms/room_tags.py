"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit rooms tags. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import Autodesk.Revit.DB as rdb
from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res


def move_tag_to_room(doc, tag_id):
    """
    Moves a room tag to the associated rooms location point.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tag_id: The element id of the tag to be moved to the room.
    :type tag_id: Autodesk.Revit.DB.ElementId
    :return:
        Result class instance.
        - Tag moving status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name and number of the room.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain the name and number of the room and the exception message.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    rt = doc.GetElement(tag_id)
    room_tag_point = rt.Location.Point
    room_location_point = rt.Room.Location.Point
    room_data = str(rt.Room.Number) + " " + str(rdb.Element.Name.GetValue(rt.Room))
    translation = room_location_point - room_tag_point

    def action():
        action_return_value = res.Result()
        try:
            rt.Location.Move(translation)
            action_return_value.message = "Moved tag to room: {}".format(room_data)
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to move tag to room: {} with exception: {}".format(
                    room_data, e
                ),
            )
        return action_return_value

    transaction = rdb.Transaction(doc, "Moving room tag to room : {}".format(room_data))
    return_value.update(rTran.in_transaction(transaction, action))
    return return_value
