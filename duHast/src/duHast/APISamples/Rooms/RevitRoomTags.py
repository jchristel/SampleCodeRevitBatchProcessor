'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit rooms tags. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Common import transaction as rTran
from duHast.Utilities import Result as res


def move_tag_to_room(doc, tag_id):
    '''
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
    '''

    return_value = res.Result()
    rt = doc.GetElement(tag_id)
    room_tag_point = rt.Location.Point
    room_location_point = rt.Room.Location.Point
    room_data = str(rt.Room.Number) + ' ' + str(rdb.Element.Name.GetValue(rt.Room))
    translation =  room_location_point - room_tag_point
    def action():
        action_return_value = res.Result()
        try:
            rt.Location.Move(translation)
            action_return_value.message = 'Moved tag to room ' + room_data
        except Exception as e:
            action_return_value.update_sep(False, 'Failed to move tag to room ' + room_data + ' with exception: ' + str(e))
        return action_return_value
    transaction = rdb.Transaction(doc, 'Moving room tag to room : ' + room_data)
    return_value.update(rTran.in_transaction(transaction, action))
    return return_value