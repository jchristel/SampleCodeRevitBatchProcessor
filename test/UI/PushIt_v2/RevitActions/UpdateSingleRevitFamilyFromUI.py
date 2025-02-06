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

from PushIt_v2.RevitActions.RevitActionBase import RevitActionBase
from PushIt_v2.Utilities.shared_parameters import (
    get_shared_parameter_data,
)
from PushIt_v2.Utilities.families_get import (
    extract_single_family_data,
)
from PushIt_v2.Utilities.families_update import update_single_family
from PushIt_v2.Utilities import event_names


class UpdateSingleRevitFamilyFromUI(RevitActionBase):

    def __init__(self, revit_model):
        """
        Constructor for the Revit Action class.
        """

        super(UpdateSingleRevitFamilyFromUI, self).__init__(revit_model=revit_model)

    def execute(self, doc, selected_element_id):
        """
        Execute the action.

        Pushes single room data into selected element in Revit only.

        :param doc: The Revit document.
        :type doc: Autodesk.Revit.DB.Document
        :param selected_element_id: The selected element id.
        :type selected_element_id: ElementId
        """

        # check if the room of interest is set
        if self.revit_model._room_of_interest is None:
            print("Room of interest is not set.")
            return

        # get the selected elements from the revit ui:
        selected_element = doc.GetElement(selected_element_id)

        # check if the selected element is of the correct category(s)
        if (
            selected_element.Category.Name
            not in self.revit_model._settings.push_it_revit_target_categories
        ):
            print(
                "Selected element cat: {} is not supported.".format(
                    selected_element.Category.Name
                )
            )
            print(
                "Supported categories: {}".format(
                    self.revit_model._settings.push_it_revit_target_categories
                )
            )

        # get the shared parameter data
        shared_parameter_data = get_shared_parameter_data(
            doc=doc, room=self.revit_model._room_of_interest
        )

        # get the room related properties from the element so matching room in data model can be updated
        # the element can be removed from the room
        # and the new element can be added to the room
        revit_family_instance_old = extract_single_family_data(
            doc=doc,
            family_instance=selected_element,
            shared_parameter_data=shared_parameter_data,
        )
        # print("revit_family_instance_old: {}".format(revit_family_instance_old))

        # update the element in Revit with the new room properties
        update_single_family_result = update_single_family(
            doc=doc,
            family_instance=selected_element,
            room=self.revit_model._room_of_interest,
            shared_parameter_data=shared_parameter_data,
            safety_off=self.revit_model.safety_off,
        )
        # print("update_single_family_result: {}".format(update_single_family_result))

        # add the revit element to the room
        if update_single_family_result.status is True:
            self.revit_model._room_of_interest.add_placed_family(
                update_single_family_result.result[0]
            )

        # remove previously pushed element from the room in data model
        self.revit_model.remove_placed_family_from_room(revit_family_instance_old)

        # raise property changed event to update the UI
        self.revit_model.RaisePropertyChanged(event_names.REVIT_MODEL_ROOMS_UPDATED)
