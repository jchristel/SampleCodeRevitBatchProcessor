"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class for WPF view model error validation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on:

https://github.com/SingletonSean/wpf-tutorials/blob/master/ValidationMVVM/ViewModels/ErrorsViewModel.cs

"""

#
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
#


from System.ComponentModel import INotifyDataErrorInfo,  PropertyChangedEventArgs



class ErrorsViewModel(INotifyDataErrorInfo):
    def __init__(self):
        """
        A base class for error validation in WPF view models.
        """
        # ini super class to allow multi inheritance in children!
        super(ErrorsViewModel, self).__init__()
        
        self._errors = {}
        self.propertyChangedHandlers = []
    

    def GetErrors(self, propertyName):
        """
        Returns the errors for the specified property.
        Implementation of INotifyDataErrorInfo.GetErrors.
        """
        
        if propertyName in self._errors:
            return self._errors[propertyName]
        return None

    def HasErrors(self):
        """
        Returns True if there are any errors in the view model.
        Implementation of INotifyDataErrorInfo.HasErrors.
        """
        return len(self._errors) > 0

    def add_ErrorsChanged(self, handler):
        """
        Adds a handler to the ErrorsChanged event.
        """
        self.propertyChangedHandlers.append(handler)

    def remove_ErrorsChanged(self, handler):
        """
        Removes a handler from the ErrorsChanged event.
        """
        self.propertyChangedHandlers.remove(handler)

    def RaiseErrorsChanged(self, propertyName):
        """
        Raises the ErrorsChanged event for the specified property.
        
        :param propertyName: The name of the property that has changed.
        :type propertyName: str
        """
        
        args = PropertyChangedEventArgs(propertyName)
        for handler in self.propertyChangedHandlers:
            handler(self, args)
        
    
    def ClearErrors(self, property_name):
        """
        Clears the errors for the specified property.
        
        :param property_name: The name of the property to clear the errors for.
        :type property_name: str
        """
        
        if property_name in self._errors:
            del self._errors[property_name]
            self.RaiseErrorsChanged(property_name)
    
    def ClearAllErrors(self):
        """
        Clears all errors.
        """
        
        self._errors.clear()
        self.RaiseErrorsChanged(None)
    
    def AddError(self, property_name, error_message):
        """
        Adds an error to the specified property.
        
        :param property_name: The name of the property to add the error to.
        :type property_name: str
        :param error_message: The error message.
        :type error_message: str
        """
        
        if property_name not in self._errors:
            self._errors[property_name] = []
        self._errors[property_name].append(error_message)
        self.RaiseErrorsChanged(property_name)