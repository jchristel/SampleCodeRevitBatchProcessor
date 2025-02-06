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
A  generic class used to raise Revit events.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No Can execute method is required for this command.

"""

from duHast.UI.Objects.WPF.Commands.CommandBase import CommandBase


class RaiseRevitEventCommand(CommandBase):

    def __init__(
        self,
        execute=None,
    ):
        """
        Constructor for the PushRoomDataCommand class.

        :param revit_model: The Revit model
        :type revit_model: RevitModel
        :param execute: The execute method
        :type execute: func, optional
        """

        super(RaiseRevitEventCommand, self).__init__(execute=None)
        self._execute = execute

    def CanExecute(self, parameter):
        """
        This method always returns True

        :param parameter: The parameter
        :type parameter: object
        """

        return True

    def Execute(self, parameter):
        """
        This method raises the Revit event.

        :param parameter: The parameter
        :type parameter: object
        """

        if self._execute:
            try:
                self._execute(parameter)
            except Exception as e:
                print("Error in execute push UPDATE room data command: {}".format(e))

    def OnViewModelPropertyChanged(self, sender, property_changed_args):
        """
        Not required for this command.

        Args:
            sender (_type_): _description_
            property_changed_args (_type_): _description_

        """

        pass
