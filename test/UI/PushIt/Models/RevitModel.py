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

from PushIt.Utilities.load_rooms import load_rooms_from_file
from PushIt.Utilities.get_families import get_families_in_model


class RevitModel(Base):

    def __init__(self, settings_file_path=None):
        """
        Constructor for the RevitModel class.
        """

        super(RevitModel, self).__init__()

        # the container for all rooms read from data file
        self._rooms_container = RoomsContainer()

        # the app settings object
        self._settings = Settings(settings_file_path=settings_file_path)
        self._settings.add_PropertyChanged(self.on_settings_changed)

        # the room selected by the user in the UI
        self._room_of_interest = None

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        # type checking
        if not (isinstance(value, Settings)):
            raise ValueError(
                "Value must be of type Setting, got {} instead.".format(type(value))
            )
            
        # add the event handler to the settings object
        value.add_PropertyChanged(self.on_settings_changed)
        
        # store settings in class
        self._settings = value
    
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
                    room.add_family(family)
                # Remove the matched families from the dictionary to speed up the search
                del family_dict[room_id]
        
        return room_data
    
    def populate_room_data(self, doc):
        """
        Populate the room data from file and from the Revit document.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        """

        #debug:
        self._settings.rooms_data_file_path = r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\test\UI\PushIt\Samples\Data_Extended.csv"
        # load rooms from file if file path is set
        if self._settings.rooms_data_file_path:
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
                rooms_result.result[0], # a room object to get the properties we are interested in
            )
        
            # update the rooms data with placed family data
            room_data = self._update_room_data_with_family_data(rooms_result.result, families)
            
            # add the rooms to the model
            for room in room_data:
                self.add_room(room)
                
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
        
    def on_settings_changed(self, sender, property_name):
        """
        Event handler for settings changed event.
        Will save the settings to file.
        
        :param sender: The object that sent the event.
        :type sender: object
        :param property_name: The name of the property that changed.
        :type property_name: str
        """
        
        sender.save_settings()  

