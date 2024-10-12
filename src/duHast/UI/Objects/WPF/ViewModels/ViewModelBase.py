"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class for WPF view models.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on:

https://markheath.net/post/wpf-and-mvvm-in-ironpython

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

# from duHast.Utilities.Objects import base

from System.ComponentModel import INotifyPropertyChanged
from System.ComponentModel import PropertyChangedEventArgs


class ViewModelBase(INotifyPropertyChanged):
    def __init__(self):
        """
        A base class for WPF view models.
        """
        # ini super class to allow multi inheritance in children!
        super(ViewModelBase, self).__init__()
        self.property_changed_handlers = []

    def RaisePropertyChanged(self, propertyName):
        """
        Raises property changed event for handlers

        Args:
            propertyName (str): the name of the property which has changed
        """
        args = PropertyChangedEventArgs(propertyName)
        for handler in self.property_changed_handlers:
            handler(self, args)

    def add_PropertyChanged(self, handler):
        """
        Adds a handler to the property changed event.
        """
        self.property_changed_handlers.append(handler)

    def remove_PropertyChanged(self, handler):
        """
        Removes a handler from the property changed event.
        """
        self.property_changed_handlers.remove(handler)
