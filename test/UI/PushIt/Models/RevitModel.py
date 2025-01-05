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

from duHast.Utilities.Objects.base import Base

from PushIt.Models.Room import Room
from PushIt.Models.RoomsContainer import RoomsContainer
from PushIt.Objects.Settings import Settings


class RevitModel(Base):

    def __init__(self):
        """
        Constructor for the RevitModel class.
        """

        super(RevitModel, self).__init__()

        self._rooms_container = RoomsContainer()
        self._settings = Settings()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        if not (isinstance(value, Settings)):
            raise ValueError(
                "Value must be of type Setting, got {} instead.".format(type(value))
            )
        self._settings = value

    def get_all_rooms(self):
        """
        Get all rooms from the model.
        """
        return self._rooms_container.get_all_rooms()

    def get_room_by_id(self, room_id):
        """
        Get a room by its id.
        """
        return self._rooms_container.get_room_by_id(room_id)
    
    def add_room(self, room_model):
        # check type
        if isinstance(room_model, Room) == False:
            raise TypeError(
                "room_model needs to be of type Room, got {} instead".format(
                    type(room_model)
                )
            )

        # add the room to the container and check for conflicts
        self._rooms_container.add_room(room_model)

    def push_data(self, families):
        for fam in families:
            # check type
            if isinstance(fam, Room) == False:
                raise TypeError(
                    "family needs to be of type Room, got {} instead".format(type(fam))
                )

            # reload ...
