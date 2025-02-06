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

from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase

from PushIt_old.Utilities.event_names import VIEW_MODEL_SELECTED_ROW


class PushRoomDataCommand(CommandBase):

    def __init__(
        self,
        rooms_selection_view_model,
        execute=None,
    ):
        """
        Constructor for the PushRoomDataCommand class.

        :param revit_model: The Revit model
        :type revit_model: RevitModel
        :param rooms_selection_view_model: The rooms selection view model
        :type rooms_selection_view_model: RoomsSelectionViewModel
        :param rooms_selection_view_navigation_service: The rooms selection view navigation service
        :type rooms_selection_view_navigation_service: NavigateCommand
        :param execute: The execute method
        :type execute: func, optional
        """

        super(PushRoomDataCommand, self).__init__(execute=None)

        self.rooms_selection_view_model = rooms_selection_view_model
        self._execute = execute

        # sub scribe to property change event to enable or disable submit button
        self.rooms_selection_view_model.add_PropertyChanged(
            self.OnViewModelPropertyChanged
        )

    def CanExecute(self, parameter):
        """
        This method returns True if the row selected room has a count of 0 only or if the safety off mode is enabled.

        :param parameter: The parameter
        :type parameter: object
        """

        # check if push it is in safety off mode
        if self.rooms_selection_view_model.SafetyOffMode:
            return True

        # check if the selected rooms have a placement count of 0
        if self.rooms_selection_view_model.CanPushRoomData:
            return True
        else:
            return False

    def Execute(self, parameter):
        """
        This method raises the external event for the push room data command.

        :param parameter: The parameter
        :type parameter: object
        """

        if self._execute:
            self._execute(parameter)

    def OnViewModelPropertyChanged(self, sender, property_changed_args):
        """
        Forces to re-evaluate the reload button availability.

        Number of arg to this function is not optional!!

        Args:
            sender (_type_): _description_
            property_changed_args (_type_): _description_

        """

        # check if the selected row index has changed
        if property_changed_args.PropertyName == VIEW_MODEL_SELECTED_ROW:
            self.on_can_execute_changed()
