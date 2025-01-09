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
from duHast.Revit.Common.design_set_options import get_active_design_option, get_design_set_of_active_design_option
from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase

from PushIt.Models.Room import Room
from PushIt.Models.RoomsContainer import RoomsContainer
from PushIt.Objects.Settings import Settings
from PushIt.Utilities.load_rooms import load_rooms_from_file
from PushIt.Utilities.get_families import get_families_in_model
from PushIt.Utilities.event_names import REVIT_MODEL_ROOMS_UPDATED

from Autodesk.Revit.DB import Element


# inherits from ViewModelBase in order to be able to use event handlers when the
# rooms have changed

class RevitModel(ViewModelBase, Base):

    def __init__(self, settings_file_path=None):
        """
        Constructor for the RevitModel class.
        """

        super(RevitModel, self).__init__()

        # the container for all rooms read from data file
        self._rooms_container = RoomsContainer()

        # the app settings object
        self._settings = Settings(settings_file_path=settings_file_path)

        # the room selected by the user in the UI
        self._room_of_interest = None

    @property
    def settings(self):
        return self._settings

    # @settings.setter
    # def settings(self, value):
    #     # type checking
    #     if not (isinstance(value, Settings)):
    #         raise ValueError(
    #             "Value must be of type Setting, got {} instead.".format(type(value))
    #         )

    #     # store settings in class
    #     self._settings = value

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

    def _update_room_data_with_family_data(self,
                                           room_data, 
                                           families,
                                           active_design_option,
                                           active_design_set):
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

        # get the active design option and design set names
        active_design_option_name = "" if active_design_option is None else active_design_option.Name
        active_design_set_name = Element.Name.GetValue(active_design_set)
        
        # loop over family instances and assign to rooms based on their room_id

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
                for family in family_dict[room.id.id]:
                    
                    # check if the family should be added to the room
                    add_family = False
                    # check if the family is placed in the active design option / set
                    if family.design_option_name == active_design_option_name and family.design_set_name == active_design_set_name:
                        add_family = True
                        
                    # check if the family is placed in the main model
                    elif family.design_set_name == "Main Model" and family.design_option_name == "":
                        add_family = True
                    
                    # check if the family is placed in another design sets primary design option
                    elif family.design_set_name == active_design_option_name and family.design_option_is_primary is True:
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

    def populate_room_data(self, doc):
        """
        Populate the room data from file and matched families from the Revit document to rooms.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        """

        # debug:
        # self._settings.rooms_data_file_path = r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\test\UI\PushIt\Samples\Data_Extended.csv"
        # load rooms from file if file path is set
        if self._settings.rooms_data_file_path:
            # clear room data
            self.clear_rooms()
            
            # load rooms from file
            rooms_result = load_rooms_from_file(self._settings.rooms_data_file_path)
            if rooms_result.status is False:
                raise ValueError(
                    "Failed to load rooms from file: {}".format(rooms_result.message)
                )

            # get elements from the document
            # check if the target categories are set
            if self._settings.push_it_revit_target_categories is None:
                # set a default value to walls
                self._settings.push_it_revit_target_categories = ["Walls"]

            # get the elements from the document
            families = get_families_in_model(
                doc,
                self._settings.push_it_revit_target_categories,  # the target categories
                rooms_result.result[
                    0
                ],  # a room object to get the properties we are interested in
            )

            # get the active design option and design set
            active_design_option = get_active_design_option(doc)
            active_design_set = get_design_set_of_active_design_option(doc)

            # update the rooms data with placed family data
            room_data = self._update_room_data_with_family_data(
                rooms_result.result, families, active_design_option, active_design_set
            )

            # add the rooms to the model
            for room in room_data:
                self.add_room(room)
            
            
            #print("raising property changed event to update the UI..")
            # raise property changed event to update the UI
            self.RaisePropertyChanged(REVIT_MODEL_ROOMS_UPDATED)
            
        else:
            print("No room data file path set, skipping room data loading.")

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
