"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to handle stores.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on:

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


import clr
clr.AddReference('System')
from System import EventArgs

class NavigationStore:
    
    def __init__(self):
        
        # Private member _currentViewModel
        self._currentViewModel = None
        
        # Event for CurrentViewModelChanged
        self.CurrentViewModelChanged = []
    
    # Property for CurrentViewModel
    @property
    def CurrentViewModel(self):
        return self._currentViewModel

    @CurrentViewModel.setter
    def CurrentViewModel(self, value):
        self._currentViewModel = value
        # raise event that notifies subscribers that the view model has changed
        self.OnCurrentViewModelChanged()
    
    # Method to trigger CurrentViewModelChanged event
    def OnCurrentViewModelChanged(self):
        for handler in self.CurrentViewModelChanged:
            handler()#self)#, EventArgs()) # Invoke the event if there are any listeners
        
    def add_ViewModelChanged(self, handler):
        """
        Adds a handler to the ViewModelChanged event.
        """
        self.CurrentViewModelChanged.append(handler)