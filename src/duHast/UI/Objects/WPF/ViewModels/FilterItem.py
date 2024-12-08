"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to provide filtering of views of observable collections..
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IsChecked property should be bound similar to this sample code:
<GridViewColumn.HeaderContainerStyle>
    <Style TargetType="GridViewColumnHeader">
        <Setter Property="ContextMenu">
            <Setter.Value>
                <ContextMenu>
                    <ItemsControl ItemsSource="{Binding UniqueFamilyNames}">
                        <ItemsControl.ItemTemplate>
                            <DataTemplate>
                                <CheckBox 
                                    Content="{Binding Value}" 
                                    IsChecked="{Binding IsChecked, Mode=TwoWay}"   <<<--- here
                                    Command="{Binding CheckCommand}"/>
                            </DataTemplate>
                        </ItemsControl.ItemTemplate>
                    </ItemsControl>
                </ContextMenu>
            </Setter.Value>
        </Setter>
    </Style>
    </GridViewColumn.HeaderContainerStyle>

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

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase

class FilterItem(ViewModelBase):
    def __init__(self, value, refresh_view_method):
        """
        A filter item for a view model view. 
        
        Is used in column context menu filters to filter the view based on the value of the item.
        
        :param value: the value of the item
        :param refresh_view_method: the method to call to refresh the view
        """
        
        super(FilterItem, self).__init__()
        self._value = value
        self.refresh_view_method = refresh_view_method
        
        # default to checked
        self._is_checked = True

    @property
    def Value(self):
        """
        Gets the value of the item displayed in the context menu.
        """
        
        return self._value
    
    @property
    def IsChecked(self):
        """
        Gets the is checked value of the item.
        """
        
        return self._is_checked

    @IsChecked.setter
    def IsChecked(self, value):
        """
        Sets the is checked value of the item.
        """
        
        if  self._is_checked != value:
            self._is_checked = value
            self.RaisePropertyChanged("IsChecked")
            
            # refresh the view to show the changes
            if self.refresh_view_method:
                self.refresh_view_method()

        

