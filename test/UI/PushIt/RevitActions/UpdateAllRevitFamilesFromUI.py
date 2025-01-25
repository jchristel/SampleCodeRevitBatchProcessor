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
A class updating all revit family instances representing rooms based on the room data model.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All revit instances representing rooms are updated based on matching room data from the data model.


"""


from PushIt.RevitActions.RevitActionBase import RevitActionBase
from PushIt.Utilities.families_get import (
    get_families_in_model,
)
from PushIt.Utilities.shared_parameters import (
    get_shared_parameter_data,
)
from PushIt.Utilities.families_update import update_single_family
from PushIt.Utilities import event_names

from Autodesk.Revit.DB import ElementId

class UpdateAllRevitFamiliesFromUI(RevitActionBase):
    
    def __init__(self, revit_model):
        """
        Constructor for the Revit Action class.
        """

        super(UpdateAllRevitFamiliesFromUI, self).__init__(revit_model=revit_model)
        
       
    def execute(self, doc):
        """
        Execute the action.
        """
        
        # check if any rooms are loaded in the data model
        rooms_in_data_model = self.revit_model._rooms_container.get_all_rooms()
        if len(rooms_in_data_model) == 0:
            print("No rooms loaded in the data model. Please load rooms first.")
        
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
        
        
        # loop over families and look for matches in the data model based on the room id
        for family in families:
            
            # get the room object from the data model
            room = self.revit_model._rooms_container.get_room_by_id(family.room_id)
            
            # check if the room object is found
            if room is None:
                # no match next family
                continue
            
            # update the element in Revit with the new room properties
            update_single_family_result = update_single_family(
                doc=doc,
                family_instance=doc.GetElement(ElementId(family.revit_element_id)),
                room=room,
                shared_parameter_data=shared_parameter_data,
            )
        
            if update_single_family_result is False:
                print("Failed to update family: ", family)
                continue
        
        
        # set the active design option and design set names
        self.revit_model._set_active_design_option_and_design_set(doc)
        
        # get the elements from the document
        families_updated = get_families_in_model(
            doc,
            self.revit_model._settings.push_it_revit_target_categories,  # the target categories
            rooms_in_data_model[
                0
            ],  # a room object to get the properties we are interested in
        )
        
        # update the rooms data with placed family data
        room_data = self.revit_model._update_room_data_with_family_data(
            rooms_in_data_model, families_updated
        )

        # clear the old rooms
        self.revit_model.clear_rooms()

        # add the updated rooms to the model
        for room in room_data:
            self.revit_model.add_room(room)
            
        # let the model know about the updated families
        self.revit_model.RaisePropertyChanged(event_names.REVIT_MODEL_ROOMS_UPDATED)
    
