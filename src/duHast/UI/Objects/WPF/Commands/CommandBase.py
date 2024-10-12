"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to handle wpf command bindings.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on:

https://markheath.net/post/wpf-and-mvvm-in-ironpython
https://www.youtube.com/channel/UC7X9mQ_XtTYWzr9Tf_NYcIg

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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
#

from duHast.Utilities.Objects import base
from System.Windows.Input import ICommand
from System import EventArgs


class CommandBase(ICommand):
    def __init__(self, execute):
        """
        A class to handle wpf command bindings.

        :param execute: The method to execute when the command is invoked.
        :type execute: callable
        :param can_execute: The method to determine if the command can be executed.
        :type can_execute: callable
        """
        # ini super class to allow multi inheritance in children!
        # super(Command, self).__init__()

        self.execute = execute
        self.can_execute_changed_handlers = []

    def Execute(self, parameter):
        self.execute()

    def on_can_execute_changed(self):
        """
        Raises the CanExecuteChanged event for subscribers.
        """
        if self.can_execute_changed_handlers:
            for handler in self.can_execute_changed_handlers:
                handler(self, EventArgs())

    def add_CanExecuteChanged(self, handler):
        """
        Adds a handler to the CanExecuteChanged event.
        """
        self.can_execute_changed_handlers.append(handler)

    def remove_CanExecuteChanged(self, handler):
        """
        Removes a handler from the CanExecuteChanged event.
        """
        if handler in self.can_execute_changed_handlers:
            self.can_execute_changed_handlers.remove(handler)

    def CanExecute(self, parameter):
        return True
