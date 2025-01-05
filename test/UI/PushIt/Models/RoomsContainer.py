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

from PushIt.Models.Room import Room
from PushIt.Exceptions.RoomConflictException import RoomsConflictException

from duHast.Utilities.Objects.base import Base


class RoomsContainer(Base):

    def __init__(self):
        """
        Initializes a new instance of the RoomsContainer class.

        This class is used to store all rooms retrieved from an external to Revit data source in a container.
        """
        super(RoomsContainer, self).__init__()

        # ini list
        self._rooms = []

    def get_all_rooms(self):
        """
        Gets all rooms stored in the container.

        :return: A list of all rooms stored in the container.
        :rtype: list
        """

        return self._rooms

    def get_room_by_id(self, room_id):
        """
        Get a room by its id.
        """
        
        for room in self._rooms:
            if room.id.id == room_id:
                return room

        return None
    
    def add_room(self, room_instance):
        """
        Adds a new room to the container.

        :param room_instance: The room instance to be added.
        :type room_instance: Room
        :raises TypeError: If room_instance is not of type Room
        :raises RoomsConflictException: If the new room conflicts with an existing room in the container.
        """

        # type checking
        if isinstance(room_instance, Room) == False:
            raise TypeError(
                "room_instance needs to be of type Room, got {} instead".format(
                    type(room_instance)
                )
            )

        # check if any reservations conflicts with the new one
        for existing_room in self._rooms:
            if existing_room.Conflicts(room_instance):
                raise RoomsConflictException(
                    message="New room conflicts existing room",
                    existing_room=existing_room,
                    new_room=room_instance,
                )

        self._rooms.append(room_instance)
