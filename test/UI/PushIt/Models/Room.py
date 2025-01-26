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
from PushIt.Models.RevitFamily import RFamily


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

    def add_placed_family(self, family_instance):
        """
        Adds a placed family to the room.

        :param family_instance: The family instance to add.
        """

        # check type
        if isinstance(family_instance, RFamily) == False:
            raise TypeError(
                "family_instance needs to be of type FamilyInstance, got {} instead".format(
                    type(family_instance)
                )
            )

        # make sure the properties in the family match room properties with exception of the area designed

        # check if the room id matches
        if family_instance.room_id != self.id.id:
            return

        # check if the area briefed matches
        if family_instance.area_briefed != self.area_briefed.value:
            return

        # check if other properties match
        for prop in self.other_properties:
            # family instance properties are instances of RoomProperty:

            for prop_instance in family_instance.properties:
                if prop.parameter_guid == prop_instance.parameter_guid:
                    if prop.value != prop_instance.value:
                        return

        self._revit_matches.append(family_instance)

        # check how many placed matches there are
        # if one match update the area designed accordingly from the family instance
        # if multiple matches set the area designed to None
        if len(self._revit_matches) == 1:
            self.area_designed.value = family_instance.area_designed
        else:
            self.area_designed.value = None

    def clear_placed_families(self):
        """
        Clears the placed families of the room.
        """

        self._revit_matches = []

    def get_revit_matches(self):
        """
        Returns the revit matches of the room.
        """

        # for now return a list with a random length of 0 to 3 elements

        # Generate a random number between 0 and 3
        # num_elements = random.randint(0, 3)

        # Create a list with that many elements
        # revit_matches = ["Match: {}".format(i) for i in range(num_elements)]

        return self._revit_matches

    def remove_placed_family(self, family_instance):
        """
        Removes a placed family from the room.

        :param family_instance: The family instance to remove.
        """

        # check type
        if isinstance(family_instance, RFamily) == False:
            raise TypeError(
                "family_instance needs to be of type FamilyInstance, got {} instead".format(
                    type(family_instance)
                )
            )

        # check if the family instance is in the list
        if family_instance not in self._revit_matches:
            return

        # remove the family instance from the list
        self._revit_matches.remove(family_instance)

        # update the area designed
        if len(self._revit_matches) == 1:
            self.area_designed.value = self._revit_matches[0].area_designed
        elif len(self._revit_matches) == 0:
            self.area_designed.value = 0
        else:
            self.area_designed.value = None

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
