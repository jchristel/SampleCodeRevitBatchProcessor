"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
NVVM Revit Room class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Middle class in NVVM model schema. 

This class is responsible for initializing the RoomId class and storing some room properties.

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from RoomId import RoomId


class Room(object):

    def __init__(self, room_id, room_name, room_number, phase, level):

        if not isinstance(room_id, RoomId):
            raise TypeError("room_id must be of type RoomId")

        self.room_id = room_id
        self.room_name = room_name
        self.room_number = room_number
        self.phase = phase
        self.level = level

    def conflicts(self, other_room):
        """
        Checks if the room conflicts with another room.

        :param other_room: The other room to check
        :type other_room: Room
        :return: True if the rooms conflict, False otherwise
        :rtype: bool
        """

        if (
            self.room_id == other_room.room_id
            and self.level == other_room.level
            and self.phase == other_room.phase
            and self.room_number == other_room.room_number
            and self.room_name == other_room.room_name
        ):
            return True

        return False
