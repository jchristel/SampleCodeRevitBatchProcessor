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

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class updating the data model with revit family instances representing rooms from the Revit model.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from PushIt.RevitActions.RevitActionBase import RevitActionBase
from PushIt.Utilities.shared_parameters import (
    get_shared_parameter_data,
)
from PushIt.Utilities.families_get import (
    get_families_in_model,
)
from PushIt.Models.Room import Room
from PushIt.Models.RoomId import RoomID
from PushIt.Utilities.families_update import update_single_family
from Autodesk.Revit.DB import ElementId
from PushIt.Utilities import event_names


class UpdateDataModelFromRevit(RevitActionBase):

    def __init__(self, revit_model):
        """
        Constructor for the Revit Action class.
        """

        super(UpdateDataModelFromRevit, self).__init__(revit_model=revit_model)


    def get_stale_families(self, families):
        """
        Returns the families that are stale in the data model. (their room id does not match any room in the data model)

        :param families: The families.
        :type families: [RFamily]

        :return: A list of families that are stale in the data model.
        :rtype: [RFamily]
        """

        # Create a dictionary to keep track of families by their room ID
        family_dict = {}
        for family in families:
            room_id = family.room_id
            if room_id not in family_dict:
                family_dict[room_id] = []
            family_dict[room_id].append(family)
            
        # loop over family instances and find families where the room id has no match in the data model
        families_to_wipe  = []
        for fam_id, families in family_dict.items():
            if self.revit_model._rooms_container.get_room_by_id(fam_id) is None:
                families_to_wipe= families_to_wipe + families
        
        return families_to_wipe
                
    
    
    def execute(self, doc):
        
        # check if any rooms are loaded in the data model
        rooms_in_data_model = self.revit_model._rooms_container.get_all_rooms()
        if len(rooms_in_data_model) == 0:
            return

        # get the elements from the document
        families = get_families_in_model(
            doc,
            self.revit_model._settings.push_it_revit_target_categories,  # the target categories
            rooms_in_data_model[
                0
            ],  # a room object to get the properties we are interested in
        )
        
        # get the shared parameter mapping to room properties ( select the first room in the model)
        shared_parameter_data = get_shared_parameter_data(
            doc=doc, room=self.revit_model._rooms_container.get_all_rooms()[0]
        )
        
        # check if any stale data in the model
        families_to_wipe = self.get_stale_families(rooms_in_data_model, families)
        if len(families_to_wipe) == 0:
            return
        
        # wipe data
        
        # setup an empty room object to wipe the data
        empty_room = Room(id=RoomID(id=""), area_briefed="", area_designed="", other_properties=[])
        
        # loop over families and look for matches in the data model based on the room id
        for family in families_to_wipe:
            # update the element in Revit with the new room properties
            update_single_family_result = update_single_family(
                doc=doc,
                family_instance=doc.GetElement(ElementId(family.revit_element_id)),
                room=empty_room,
                shared_parameter_data=shared_parameter_data,
            )

            if update_single_family_result is False:
                print("Failed to update family: ", family)
                continue