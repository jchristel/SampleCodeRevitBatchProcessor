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
from PushIt.Utilities.rooms_load import load_rooms_from_file
from PushIt.Utilities.families_get import (
    get_families_in_model,
    extract_single_family_data,
)
from PushIt.Utilities.families_update import update_single_family
from PushIt.Utilities.shared_parameters import (
    check_shared_parameters_are_in_document,
    get_shared_parameter_data,
)
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
                room.clear_families()

                # loop over the families and add them to the room if they match
                # and conditions are met
                for family in family_dict[room.id.id]:

                    # check if the family should be added to the room
                    add_family = False
                    # check if the family is placed in the active design option / set
                    if (
                        family.design_option_name == self._active_design_option_name
                        and family.design_set_name == self._active_design_set_name
                    ):
                        add_family = True

                    # check if the family is placed in the main model
                    elif (
                        family.design_set_name == "Main Model"
                        and family.design_option_name == ""
                    ):
                        add_family = True

                    # check if the family is placed in another design sets primary design option
                    elif (
                        family.design_set_name == self._active_design_option_name
                        and family.design_option_is_primary is True
                    ):
                        add_family = True

                    # only add the family to the room if any of the above conditions are met
                    if add_family:
                        # check if family properties match room properties when
                        # adding a family to a room, except for area designed
                        # if they do, add the family to the room otherwise skip
                        room.add_family(family)

                # Remove the matched families from the dictionary to speed up the search
                del family_dict[room_id]

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
            "" if active_design_option is None else active_design_option.Name
        )
        self._active_design_set_name = (
            "Main Model"
            if active_design_set is None
            else Element.Name.GetValue(active_design_set)
        )

    def _check_shared_parameters(self, doc, room):
        """
        Check if the shared parameters exist in the document and are bound to the correct categories.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        """

        # check if the shared parameters exist in the document and are bound to the correct categories
        # if not, return False

        check_shared_parameters_result = check_shared_parameters_are_in_document(
            doc,
            room,
            self._settings.push_it_revit_target_categories,
        )

        if check_shared_parameters_result.status is False:
            # TODO: pop up a message box to inform the user
            return False

        return True

    def push_single_room_data_to_revit(self, doc, selected_element_id):
        """
        Pushes single room data into selected element in Revit only.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        :param selected_element_id: The selected element id.
        :type selected_element_id: ElementId
        """

        # check if the room of interest is set
        if self._room_of_interest is None:
            return

        # get the selected elements from the revit ui:
        selected_element = doc.GetElement(selected_element_id)

        # check if the selected element is of the correct category(s)
        if (
            selected_element.Category.Name
            not in self._settings.push_it_revit_target_categories
        ):
            print(
                "Selected element cat: {} is not supported.".format(
                    selected_element.Category.Name
                )
            )
            print(
                "Supported categories: {}".format(
                    self._settings.push_it_revit_target_categories
                )
            )

        # get the shared parameter data
        shared_parameter_data = get_shared_parameter_data(
            doc=doc, room=self._room_of_interest
        )

        # get the room related properties from the element so matching room in data model can be updated
        # the element can be removed from the room
        # and the new element can be added to the room
        revit_family_instance_old = extract_single_family_data(
            family_instance=selected_element,
            shared_parameter_data=shared_parameter_data,
        )

        # update the element in Revit with the new room properties
        update_single_family_result = update_single_family(
            doc=doc,
            family_instance=selected_element,
            room=self._room_of_interest,
            shared_parameter_data=shared_parameter_data,
        )

        # add the revit element to the room
        if update_single_family_result.status is True:
            self._room_of_interest.add_placed_family(
                update_single_family_result.result[0]
            )

        # remove previously pushed element from the room in data model
        self.remove_placed_family_from_room(revit_family_instance_old)

        # raise property changed event to update the UI
        self.RaisePropertyChanged(event_names.REVIT_MODEL_ROOMS_UPDATED)

    def update_all_room_data_from_revit_only(self, doc):
        """
        Update all room data from room place holders in Revit only.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        """

        # check if any rooms are loaded in the data model
        rooms_in_data_model = self._rooms_container.get_all_rooms()
        if len(rooms_in_data_model) == 0:
            return

        # get the elements from the document
        families = get_families_in_model(
            doc,
            self._settings.push_it_revit_target_categories,  # the target categories
            rooms_in_data_model[
                0
            ],  # a room object to get the properties we are interested in
        )

        # set the active design option and design set names
        self._set_active_design_option_and_design_set(doc)

        # update the rooms data with placed family data
        room_data = self._update_room_data_with_family_data(
            rooms_in_data_model, families
        )

        # clear the old rooms
        self.clear_rooms()

        # add the updated rooms to the model
        for room in room_data:
            self.add_room(room)

        # raise property changed event to update the UI
        self.RaisePropertyChanged(event_names.REVIT_MODEL_ROOMS_UPDATED)

    def populate_room_data(self, doc):
        """
        Populate the room data from file and matched families from the Revit document to rooms.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        """

        # load rooms from file if file path is set and an update is required
        if (
            self._settings.rooms_data_file_path
            and self._data_path_requires_update_of_rooms
        ):
            # check if the file exists
            if file_exist(self._settings.rooms_data_file_path) is False:
                return

            # clear room data
            self.clear_rooms()

            # load rooms from file
            rooms_result = load_rooms_from_file(self._settings.rooms_data_file_path)
            if rooms_result.status is False:
                raise ValueError(
                    "Failed to load rooms from file: {}".format(rooms_result.message)
                )

            # check if property shared parameters exist in the document and are bound to the correct categories
            if self._check_shared_parameters(doc, room=rooms_result.result[0]) is False:
                raise ValueError(
                    "Shared parameters do not exist in the document or are not bound to the correct categories."
                )

            # get elements from the document
            # check if the target categories are set
            # if self._settings.push_it_revit_target_categories is None:
            # set a default value to walls
            #    self._settings.push_it_revit_target_categories = ["Walls"]

            # get the elements from the document
            families = get_families_in_model(
                doc,
                self._settings.push_it_revit_target_categories,  # the target categories
                rooms_result.result[
                    0
                ],  # a room object to get the properties we are interested in
            )

            # set the active design option and design set names
            self._set_active_design_option_and_design_set(doc)

            # update the rooms data with placed family data
            room_data = self._update_room_data_with_family_data(
                rooms_result.result, families
            )

            # add the rooms to the model
            for room in room_data:
                self.add_room(room)

            # print("raising property changed event to update the UI..")
            # raise property changed event to update the UI
            self.RaisePropertyChanged(event_names.REVIT_MODEL_ROOMS_UPDATED)

        else:
            print("No room data file path set, skipping room data loading.")

    def check_data_path_updates(self, sender, property_changed_args):
        """
        Checks if the data file path has changed and updates the room data accordingly.

        :param sender: The sender of the event.
        :type sender: object
        :param property_changed_args: The property changed event arguments.
        :type property_changed_args: PropertyChangedEventArgs
        """

        # check if data path has changed
        if property_changed_args.PropertyName != event_names.VIEW_MODEL_DATA_FILE_PATH:
            return

        # check if the data file path has changed
        if self._data_file_path_intermittent == self._settings.rooms_data_file_path:
            # reset the intermittent storage
            self._data_file_path_intermittent = None
            # set the flag to avoid unnecessary updates
            self._data_path_requires_update_of_rooms = False

        # check if the file path points to a valid file
        if file_exist(self._data_file_path_intermittent) is False:
            # reset the intermittent storage
            self._data_file_path_intermittent = None
            # set the flag to avoid unnecessary updates
            self._data_path_requires_update_of_rooms = False

        # update the settings file path
        self._settings.rooms_data_file_path = self._data_file_path_intermittent
        # reset the intermittent storage
        self._data_file_path_intermittent = None
        # set the flag to update the rooms
        self._data_path_requires_update_of_rooms = True

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
