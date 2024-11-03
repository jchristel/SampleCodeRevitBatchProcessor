"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An implementation of a custom wpf window base class which can be shown in the Revit context.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
clr.AddReference("PresentationFramework")

from System.Windows import Window, VerticalAlignment, HorizontalAlignment
from duHast.UI.Objects.WPF.Xaml.XamlLoader import XamlLoader
from duHast.UI.Objects.WPF.Exceptions.MissingXAMLException import MissingXAMLException

class WPFWindowBase(Window):
    def __init__(self, xaml_path, main_view_model, xaml_by_view_model, resources_xaml_path):
    
        # make sure to initialize the base class
        super(WPFWindowBase, self).__init__()
        
        # load start up xaml data (main window)
        xaml_loader = XamlLoader(xaml_path)
        
        # get the xaml root
        xaml_window = xaml_loader.Root
        
        # get the main grid control from main window
        # this control will host all other views and associated view models
        self.main_grid = xaml_loader.MainGrid
        
        # Ensure xaml_window is of type Window and use it
        if isinstance(xaml_window, Window):
            self.Content = xaml_window.Content
            self.Title = xaml_window.Title
            self.Width = xaml_window.Width
            self.SizeToContent = xaml_window.SizeToContent
        else:
            self.Content = xaml_window

        # set up any static styling resources
        # in c# land these would be added in App.xaml
        if( resources_xaml_path):
            resources_loader = XamlLoader(resources_xaml_path)
            self.Resources.MergedDictionaries.Add(resources_loader.Root)
        
        # store xaml views by view model
        self.xaml_path_by_view_model = xaml_by_view_model
        
        # Store the passed-in MainViewModel
        self.main_view_model = main_view_model
        
        # Set the DataContext of the window to MainViewModel
        self.DataContext = self.main_view_model
        
        # Bind the CurrentViewModel to the ContentControl
        self.update_content_view(self.main_view_model.CurrentViewModel)
        
        # Subscribe to changes in CurrentViewModel
        self.main_view_model._navigation_store.add_ViewModelChanged (self.on_current_view_model_changed)
        
        # Wire up the Closed event
        self.Closed += self.on_closed
    
    
    def on_current_view_model_changed(self):
        # Update the view when CurrentViewModel changes
        self.update_content_view(self.main_view_model.CurrentViewModel)


    def update_content_view(self, view_model):
        """
        Dynamically set the content of the main grid control based on the current view model

        Args:
            view_model (_type_): The new view model to be applied
        """
        
        # get the xaml path depending on the view model
        xaml_path_current_view = self.xaml_path_by_view_model.get(type(view_model),None)

        # Load the XAML file if it exists
        if xaml_path_current_view :
            # load xaml data matching view model
            xaml_loader_current_view = XamlLoader(xaml_path_current_view)
            
            # set the data context to the new view model
            xaml_loader_current_view.Root.DataContext = view_model
            
            # Clear the existing children in the main grid
            self.main_grid.Children.Clear()

            # Set alignment for full stretching (not sure whether this is doing anything??)
            xaml_loader_current_view.VerticalAlignment = VerticalAlignment.Stretch
            xaml_loader_current_view.HorizontalAlignment = HorizontalAlignment.Stretch

            # Add the new view to the main grid
            self.main_grid.Children.Add(xaml_loader_current_view.Root)
        else:
            raise MissingXAMLException(message="XAML file not provided for view model.", view_model=view_model)
            
        
    def on_closed(self, sender, event):
        # Handle cleanup here
        pass