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

from PushIt_v2.RevitActions.RevitActionBase import RevitActionBase
from PushIt_v2.Utilities.families_get import (
    get_families_in_model,
)



class UpdateDataModelFromRevit(RevitActionBase):

    def __init__(self, revit_model):
        """
        Constructor for the Revit Action class.
        """

        super(UpdateDataModelFromRevit, self).__init__(revit_model=revit_model)

    def execute(self, doc):
        print("UpdateDataModelFromRevit: execute")
        return
        try:
           
            # check if any rooms are loaded in the data model
            rooms_in_data_model = self.revit_model._rooms_container.get_all_rooms()
            if len(rooms_in_data_model) == 0:
                print("No rooms in the data model to update with Revit data.")
                return

            # get the elements from the document
            families = get_families_in_model(
                doc,
                self.revit_model._settings.push_it_revit_target_categories,  # the target categories
                rooms_in_data_model[
                    0
                ],  # a room object to get the properties we are interested in
            )
            print("Families: {}", len(families))
            # set the active design option and design set names
            self.revit_model._set_active_design_option_and_design_set(doc)
            print("update design set and option")

            # update the rooms data with placed family data
            room_data = self.revit_model._update_room_data_with_family_data(
                rooms_in_data_model, families
            )

            print("updated room data with placed families")

            # clear the old rooms
            self.revit_model.clear_rooms()
            print("cleared existing rooms from data model")

            # add the updated rooms to the model
            for room in room_data:
                self.revit_model.add_room(room)
            
            print("added updated rooms to the data model: {}".format(len(room_data)))

            # raise property changed event to update the UI
            #self.revit_model.RaisePropertyChanged(event_names.REVIT_MODEL_ROOMS_UPDATED)
        except Exception as e:
            print("Error in UpdateDataModelFromRevit: {error}".format(error=e))
            
