"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
NVVM Rooms by Model Model class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2nd level class in NVVM model schema. 

This class is responsible for initializing the a list of Room class instances.

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


class RoomsByModel(object):

    rooms = None

    def __init__(self):
        self.rooms = []

    def add_room(self, room):
        """
        Adds a room to the list of rooms.

        :param room: The room to add
        :type room: Room
        """
        for existing_room in self.rooms:
            if existing_room.conflicts(room):
                raise ValueError("The room conflicts with an existing room in the model.")

        self.rooms.append(room)

    def get_rooms_by_level_name(self, level_name):
        """
        Returns a list of rooms that are on the given level.

        :param level_name: The name of the level
        :type level_name: str
        :return: A list of rooms that are on the given level
        :rtype: list[Room]
        """
        return [room for room in self.rooms if room.level == level_name]

    def get_rooms_by_phase_name(self, phase_name):
        """
        Returns a list of rooms that are in the given phase.

        :param phase_name: The name of the phase
        :type phase_name: str
        :return: A list of rooms that are in the given phase
        :rtype: list[Room]
        """
        return [room for room in self.rooms if room.phase == phase_name]
