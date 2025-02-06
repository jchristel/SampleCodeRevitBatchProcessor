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
A class populating the data model with data from file and placed revit family instances representing rooms.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


from PushIt_v2.RevitActions.RevitActionBase import RevitActionBase
from PushIt_v2.Utilities.families_get import (
    get_families_in_model,
)
from PushIt_v2.Utilities.shared_parameters import check_shared_parameters_are_in_document

from duHast.Utilities.files_io import file_exist
from PushIt_v2.Utilities.rooms_load import load_rooms_from_file
from PushIt_v2.Utilities import event_names


class InitialiseRoomData(RevitActionBase):

    def __init__(self, revit_model):
        """
        Constructor for the Revit Action class.
        """

        super(InitialiseRoomData, self).__init__(revit_model=revit_model)

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
            self.revit_model._settings.push_it_revit_target_categories,
        )

        if check_shared_parameters_result.status is False:
            print("Shared parameters do not exist in the document or are not bound to the correct categories.")
            print(check_shared_parameters_result)
            return False

        return True

    def execute(self, doc):
        """
        Execute the action.
        """

        try:
            
            # load rooms from file if file path is set and an update is required
            if (
                self.revit_model._settings.rooms_data_file_path
            ):
                if( self.revit_model._data_path_requires_update_of_rooms):
                    if (len(self.revit_model.get_all_rooms()) > 0):
                

                        # check if property shared parameters exist in the document and are bound to the correct categories
                        if self._check_shared_parameters(doc, room=self.revit_model.get_all_rooms()[0]) is False:
                            raise ValueError(
                                "Shared parameters do not exist in the document or are not bound to the correct categories."
                            )

                        # get the elements from the document
                        families = get_families_in_model(
                            doc,
                            self.revit_model._settings.push_it_revit_target_categories,  # the target categories
                            self.revit_model.get_all_rooms()[0],  # a room object to get the properties we are interested in
                        )
                        print("Families in model: {}".format(len(families)))

                        # set the active design option and design set names
                        self.revit_model._set_active_design_option_and_design_set(doc)
                        print("Active design option and design set names set.: {}::{}".format(self.revit_model.active_design_set_name, self.revit_model.active_design_option_name))
                        # update the rooms data with placed family data
                        room_data = self.revit_model._update_room_data_with_family_data(
                            self.revit_model.get_all_rooms(), families
                        )
                        print("Room data updated with family data: {}".format(len(room_data)))
                        
                        print("Model has rooms: {}".format(self.revit_model.has_rooms()))
                        
                        # add the rooms to the model
                        #for room in room_data:
                        #    self.revit_model.add_room(room)
                        
                        print("Rooms added to the model: {}".format(len(self.revit_model.get_all_rooms())))
                    else:
                        print("No rooms in model, skipping room data loading.")
                else:
                    print("Room data file path set, but no update required.")

            else:
                print("No room data file path set, skipping room data loading.")
        except Exception as e:
            print("Failed to initialise room data: {}".format(e))
    