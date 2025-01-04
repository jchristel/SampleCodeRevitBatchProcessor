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

from PushIt.Models.RoomId import RoomID
from PushIt.Models.RoomProperty import RoomProperty


class Room(Base):

    def __init__(self, id, area_briefed, area_designed, other_properties=None):
        """
        Initializes a new instance of the Room class.
        """

        super(Room, self).__init__()

        # set the id
        if isinstance(id, RoomID) == False:
            raise TypeError(
                "id needs to be of type RoomID. Got {} instead".format(type(id))
            )
        self.id = id

        # check type
        if isinstance(area_briefed, RoomProperty) == False:
            raise TypeError(
                "area briefed needs to be of type RoomProperty, got {} instead".format(
                    type(area_briefed)
                )
            )
        self.area_briefed = area_briefed

        # check type
        if isinstance(area_designed, RoomProperty) == False:
            raise TypeError(
                "area designed needs to be of type RoomProperty, got {} instead".format(
                    type(area_designed)
                )
            )
        self.area_designed = area_designed

        # check type
        if other_properties is not None:
            if isinstance(other_properties, list) == False:
                raise TypeError(
                    "other_properties needs to be of type list, got {} instead".format(
                        type(other_properties)
                    )
                )
            self.other_properties = other_properties
        else:
            self.other_properties = []

        # contains the family instances in the model that match this room
        # can be more than one if the room was copied
        self._revit_matches = []

    def Conflicts(self, room_instance):
        """
        Checks if the room conflicts with another room based on the room id.
        """

        # check type
        if isinstance(room_instance, Room) == False:
            raise TypeError(
                "room_instance needs to be of type Room, got {} instead".format(
                    type(room_instance)
                )
            )

        # check the  id
        if room_instance.id != self.id:
            return False
        else:
            return True

    def add_property(self, property):
        """
        Adds a property to the room.

        :param property: The property to add.
        """

        # check type
        if isinstance(property, RoomProperty) == False:
            raise TypeError(
                "property needs to be of type RoomProperty, got {} instead".format(
                    type(property)
                )
            )

        self.other_properties.append(property)

    def get_property_names(self):
        """
        Returns the names of the properties of the room.
        """

        default_properties = ["room id", "area briefed", "area designed"]
        additional_properties = [prop.name for prop in self.other_properties]
        return default_properties + additional_properties

    def get_property_value(self, property_name):
        """
        Returns the value of the property of the room.

        :param property_name: The name of the property.
        :return: The value of the property.
        """

        if property_name == "room id":
            return self.id.id
        elif property_name == "area briefed":
            return self.area_briefed.value
        elif property_name == "area designed":
            return self.area_designed.value
        else:
            for prop in self.other_properties:
                if prop.name == property_name:
                    return prop.value
        return None

    def get_revit_matches(self):
        """
        Returns the revit matches of the room.
        """
        return []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        # ini values
        if isinstance(value, RoomID) == False:
            raise TypeError(
                "id needs to be of type RoomID. Got {} instead".format(value)
            )
        self._id = value
