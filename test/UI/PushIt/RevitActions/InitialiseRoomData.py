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


from PushIt.RevitActions.RevitActionBase import RevitActionBase
from PushIt.Utilities.families_get import (
    get_families_in_model,
)
from PushIt.Utilities.shared_parameters import check_shared_parameters_are_in_document

from duHast.Utilities.files_io import file_exist
from PushIt.Utilities.rooms_load import load_rooms_from_file
from PushIt.Utilities import event_names


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
            # TODO: pop up a message box to inform the user
            return False

        return True

    def execute(self, doc):
        """
        Execute the action.
        """

        # load rooms from file if file path is set and an update is required
        if (
            self.revit_model._settings.rooms_data_file_path
            and self.revit_model._data_path_requires_update_of_rooms
        ):
            # check if the file exists
            if file_exist(self.revit_model._settings.rooms_data_file_path) is False:
                return

            # clear room data
            self.revit_model.clear_rooms()

            # load rooms from file
            rooms_result = load_rooms_from_file(
                self.revit_model._settings.rooms_data_file_path
            )
            if rooms_result.status is False:
                raise ValueError(
                    "Failed to load rooms from file: {}".format(rooms_result.message)
                )

            # check if property shared parameters exist in the document and are bound to the correct categories
            if self._check_shared_parameters(doc, room=rooms_result.result[0]) is False:
                raise ValueError(
                    "Shared parameters do not exist in the document or are not bound to the correct categories."
                )

            # get the elements from the document
            families = get_families_in_model(
                doc,
                self.revit_model._settings.push_it_revit_target_categories,  # the target categories
                rooms_result.result[
                    0
                ],  # a room object to get the properties we are interested in
            )

            # set the active design option and design set names
            self.revit_model._set_active_design_option_and_design_set(doc)

            # update the rooms data with placed family data
            room_data = self.revit_model._update_room_data_with_family_data(
                rooms_result.result, families
            )

            # add the rooms to the model
            for room in room_data:
                self.revit_model.add_room(room)

            # print("raising property changed event to update the UI..")
            # raise property changed event to update the UI
            self.revit_model.RaisePropertyChanged(event_names.REVIT_MODEL_ROOMS_UPDATED)

        else:
            print("No room data file path set, skipping room data loading.")
