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
from duHast.Revit.Common.design_set_options import (
    get_active_design_option,
    get_design_set_of_active_design_option,
)
from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase
from duHast.Utilities.files_io import file_exist

from PushIt.Models.Room import Room
from PushIt.Models.RoomsContainer import RoomsContainer
from PushIt.Objects.Settings import Settings
from PushIt.Utilities import event_names

from Autodesk.Revit.DB import Element


"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class representing the revit model.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It contains 

- the rooms container, 
- the settings object, 
- the room of interest, 
- the data file path intermittent storage,
- the current design option and design set names,

It inherits from ViewModelBase in order to be able to use event handlers when the rooms have changed.

"""


class RevitModel(ViewModelBase, Base):

    def __init__(self, settings_file_path=None):
        """
        Constructor for the RevitModel class.
        """

        super(RevitModel, self).__init__()

        # properties
        # the container for all rooms read from data file
        self._rooms_container = RoomsContainer()

        # the app settings object
        self._settings = Settings(settings_file_path=settings_file_path)

        # the room selected by the user in the UI
        self._room_of_interest = None

        # data file path intermittent storage
        self._data_file_path_intermittent = None

        # flag to check if the data path requires an update of the rooms
        # is set to false when the intermittent data path is:
        # - the same as the current data path
        # - the file does not exist
        # is set to true when the data path is changed and the file exists
        # and at start up
        self._data_path_requires_update_of_rooms = True

        # active design option and design set names
        self._active_design_option_name = "-"
        self._active_design_set_name = "Main Model"

        # event handlers
        # event handler to check if the room data file path has changed
        self.add_PropertyChanged(self.check_data_path_updates)

    @property
    def settings(self):
        return self._settings

    @property
    def active_design_option_name(self):
        return self._active_design_option_name

    @property
    def active_design_set_name(self):
        return self._active_design_set_name

    @property
    def room_of_interest(self):
        return self._room_of_interest

    @room_of_interest.setter
    def room_of_interest(self, value):
        if not (isinstance(value, Room)):
            raise ValueError(
                "Value must be of type Room, got {} instead.".format(type(value))
            )
        self._room_of_interest = value

    def _update_room_data_with_family_data(self, room_data, families):
        """
        Assign families to rooms based on their room_id.
        Only rooms with matching room_id and all other properties matching, with exception of area designed, will be assigned.

        :param room_data: The room data.
        :type room_data: [Room]
        :param families: The families.
        :type families: [RFamily]

        :return: The updated room data.
        :rtype: [Room]
        """

        # loop over family instances and assign to rooms based on their room_id,
        # all other matching properties, design option and design set

        # Create a dictionary to keep track of families by their room ID
        family_dict = {}
        for family in families:
            room_id = family.room_id
            if room_id not in family_dict:
                family_dict[room_id] = []
            family_dict[room_id].append(family)

        # Assign families to rooms
        for room in room_data:
            if room.id.id in family_dict:
                # clear any families from the room
                room.clear_placed_families()

                # loop over the families and add them to the room if they match
                # and conditions are met
                for family in family_dict[room.id.id]:

                    # check if the family should be added to the room
                    add_family = False
                    # check if the family is placed in the active design option / set
                    if (
                        family.design_option == self._active_design_option_name
                        and family.design_set == self._active_design_set_name
                    ):
                        add_family = True

                    # check if the family is placed in the main model
                    elif (
                        family.design_set == "Main Model"
                        and family.design_option == "-"
                    ):
                        add_family = True

                    # check if the family is placed in another design sets primary design option
                    # and the main model is active
                    elif (
                        self._active_design_set_name =="Main Model"
                        and family.design_option_is_primary is True
                    ):
                        add_family = True

                    # check if the family is in a primary design option which does not match the active design set
                    elif (
                        self._active_design_set_name != family.design_set 
                        and family.design_option_is_primary is True
                    ):
                        add_family = True

                    # only add the family to the room if any of the above conditions are met
                    if add_family:
                        # check if family properties match room properties when
                        # adding a family to a room, except for area designed
                        # if they do, add the family to the room otherwise skip
                        room.add_placed_family(family)

                # Remove the matched families from the dictionary to speed up the search
                if room.id.id in family_dict:
                    del family_dict[room.id.id]
            else:
                # if no matching family instances are found
                # clear any families which might have been there at some point from the room
                room.clear_placed_families()
        return room_data

    def _set_active_design_option_and_design_set(self, doc):
        """
        Set the active design option and design set names.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        """

        # get the active design option and design set
        active_design_option = get_active_design_option(doc)
        active_design_set = get_design_set_of_active_design_option(doc)

        # set class properties
        self._active_design_option_name = (
            "-" if active_design_option is None else active_design_option.Name
        )
        self._active_design_set_name = (
            "Main Model"
            if active_design_set is None
            else Element.Name.GetValue(active_design_set)
        )

    def check_data_path_updates(self, sender, property_changed_args):
        """
        Checks if the data file path has changed and updates the room data accordingly.

        :param sender: The sender of the event.
        :type sender: object
        :param property_changed_args: The property changed event arguments.
        :type property_changed_args: PropertyChangedEventArgs
        """

        try:
            # check if data path has changed
            if (
                property_changed_args.PropertyName
                != event_names.VIEW_MODEL_DATA_FILE_PATH
            ):
                return

            # check if the data file path has changed
            if self._data_file_path_intermittent == self._settings.rooms_data_file_path:
                # reset the intermittent storage
                self._data_file_path_intermittent = None
                # set the flag to avoid unnecessary updates
                self._data_path_requires_update_of_rooms = False
                # no change
                return

            # check if the file path points to a valid file
            if file_exist(self._data_file_path_intermittent) is False:
                # reset the intermittent storage
                self._data_file_path_intermittent = None
                # set the flag to avoid unnecessary updates
                self._data_path_requires_update_of_rooms = False
                # changed but invalid file path
                return

            # update the settings file path
            self._settings.rooms_data_file_path = self._data_file_path_intermittent

            # reset the intermittent storage
            self._data_file_path_intermittent = None

            # set the flag to update the rooms
            self._data_path_requires_update_of_rooms = True

        except Exception as e:
            print("Error in check_data_path_updates: {}".format(e))

    def get_all_rooms(self):
        """
        Get all rooms from the model.

        :return: All rooms.
        :rtype: [Room]
        """

        return self._rooms_container.get_all_rooms()

    def get_room_by_id(self, room_id):
        """
        Get a room by its id.

        :param room_id: The room id.
        :type room_id: str

        :return: The room.
        :rtype: Room
        """

        return self._rooms_container.get_room_by_id(room_id)

    def add_room(self, room_model):
        """
        Add a room to the model.

        :param room_model: The room to add.
        :type room_model: Room
        """

        # check type
        if isinstance(room_model, Room) == False:
            raise TypeError(
                "room_model needs to be of type Room, got {} instead".format(
                    type(room_model)
                )
            )

        # add the room to the container and check for conflicts
        self._rooms_container.add_room(room_model)

    def clear_rooms(self):
        """
        Clear all rooms from the model.
        """

        self._rooms_container.clear_rooms()

    def remove_placed_family_from_room(self, family_instance):
        """
        Remove a placed family from a room.

        :param family_instance: The family instance to remove.
        :type family_instance: RFamily
        """

        self._rooms_container.remove_placed_family_from_room(family_instance)
