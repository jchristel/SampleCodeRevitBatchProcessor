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

import clr
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')
clr.AddReference('System.Data')

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase
from duHast.UI.Objects.WPF.Commands.RelayCommand import RelayCommand
from duHast.UI.Objects.WPF.ViewModels.FilterItem import FilterItem

from System.Collections.ObjectModel import ObservableCollection
from System.Windows.Data import CollectionViewSource, PropertyGroupDescription
from System.Data import DataTable

from PushIt.ViewModels.RoomViewModel import RoomViewModel
#from ViewModels.FilterItem import FilterItem
from PushIt.Commands.PushRoomDataCommand import PushRoomDataCommand

import os

class RoomsSelectionViewModel(ViewModelBase):
    
    # the name of the count column in the data table
    count_column_name = "Count"
    
    def __init__(self, revit_model, navigation_service):
        super(RoomsSelectionViewModel, self).__init__()
        
        # properties
        
        # the command used to sort when the user clicks on the column headers
        self._sort_command = RelayCommand(self.refresh_view)
        
        # the revit wpf model object containing the settings and families to be displayed
        self._revit_model = revit_model

        # create the data table which is used to store the room data
        self._data_table = self.create_rooms_data_table()
        
        # selected row content
        self._selected_row_content = ""
        # the selected item
        self._selected_index = -1

        # commands
        # the command used to push data into the revit model family instance
        self.push_data_command = PushRoomDataCommand(
            revit_model=revit_model,
            rooms_selection_view_model=self,
            rooms_selection_view_navigation_service=navigation_service,
            execute=self.close_window
        )
        
        # list containing the column names for the filter
        self._column_filter_items = []
        
        # create the column filter items
        self.create_column_filter_items()
        
        # set the default filter value
        self._selected_filter_item = self._column_filter_items[0]
        
        # set the default filter value
        self._selected_filter_value = ""
        
        # add room data to view model
        # needs to be happening after data table has been created
        # and after the column filter items have been created
        #self.update_rooms()
        # event handlers
        self.add_PropertyChanged(self.filter_families)
        
    
    @property
    def DataView(self):
        """
        The collection view of the data collection. to which the xaml view is bound to.
        """
        return self._data_table.DefaultView

    @property
    def ColumnFilterItems(self):
        """
        The column names to display in the filter options drop down list.
        """
        return self._column_filter_items
    
    @property
    def SelectedColumnFilterItem(self):
        """
        The selected column name to filter by.
        """
        
        return self._selected_filter_item
    
    @SelectedColumnFilterItem.setter
    def SelectedColumnFilterItem(self, value):
        """
        Sets the selected column name to filter by.
        """
        
        self._selected_filter_item = value
        # raise property change event
        self.RaisePropertyChanged("SelectedColumnFilterItem")
        
    
    @property
    def SelectedColumnFilterValue(self):
        """
        The value entered to filter a column by.
        """
        
        return self._selected_filter_value
    
    @SelectedColumnFilterValue.setter
    def SelectedColumnFilterValue(self, value):
        """
        Sets the value entered to filter a column by.
        """
        
        self._selected_filter_value = value
        # raise property change event
        self.RaisePropertyChanged("SelectedColumnFilterValue")
    
    
    @property
    def SelectedRowContent(self):
        """
        The content of the selected row.
        """
        
        return self._selected_row_content
    
    @property
    def SelectedIndex(self):
        """
        The selected row index of the data table view.
        """
        return self._selected_index
    
    
    @SelectedIndex.setter
    def SelectedIndex(self, value):
        # this returns the row index of the filtered default view not the actual data table.
        self._selected_index = value
        try:
            # get the row view from the data table view
            row_view = self._data_table.DefaultView[value]
            # get the original row from the data table
            row = row_view.Row
            # update the selected row content
            self._selected_row_content = ""
            for i in range(row.Table.Columns.Count):
                self._selected_row_content = self._selected_row_content + " Column:[{}] Value:[{}] ".format(row.Table.Columns[i].ColumnName, row[i])
            
            self.OnPropertyChanged("SelectedRowContent")
        except Exception as e:
            print("Error: ", e)


    @property
    def ReloadFamiliesCommand(self):
        """
        The command used to when the reload button in the view is clicked.
        
        Stores the selected family objects in the revit model object and triggers the close of the window.
        """
        return self.push_data_command 


    def create_column_filter_items(self):
        """
        Creates the column filter items.
        This is used to populate the column filter combo box in the view.
        
        Note:
        
        - Needs to be called after the data table has been created.
        """
        # get the columns from the data table
        columns = self._data_table.Columns
        
        # add the column names to the column filter items
        for column in columns:
            self._column_filter_items.append(column.ColumnName)
    
    def create_rooms_data_table(self):
        """
        Creates a data table with the rooms data.
        """
        # set up the data table
        data_table = DataTable()
        
        # add columns to the data table
        for room_model_instance in self._revit_model.get_all_rooms():
            # add a column per property
            for prop in room_model_instance.get_property_names():
                data_table.Columns.Add(prop)
            # get out of the loop
            break
        
        # add the count column
        data_table.Columns.Add("Count")
        
        # add the rows to the data table
        for room_model_instance in self._revit_model.get_all_rooms():
            # add a row per room
            row = data_table.NewRow()
            for prop in room_model_instance.get_property_names():
                row[prop] = room_model_instance.get_property_value(prop)
            row["Count"] = len(room_model_instance.get_revit_matches())
            data_table.Rows.Add(row)
        
        
        return data_table
    
    def update_rooms(self):
        """
        Updates the rooms view with the rooms from the data table.
        
        """

        # set up collection view based on the data table rows
        # this is what the xaml view is binding to
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        #self._rooms_view = CollectionViewSource.GetDefaultView(self._data_table.Rows)
        
        # group the families by match status (this will mean that the families will be sorted by match status first and than by any other sort criteria)
        # MatchStatus is a property of the FamilyViewModel
        #self._rooms_view.GroupDescriptions.Add(PropertyGroupDescription("MatchStatus"))
        
        # set up a filter for the collection view
        #self._rooms_view.Filter = self.filter_families
        #self.DataView.RowFilter = self.filter_families
        pass
        
    def filter_families(self, sender, property_changed_args):
        """
        Filters the families based on the selected filter item.
        
        :param item: The item to be filtered.
        :type item: object
        :return: True if the item should be displayed, False otherwise.
        :rtype: bool
        """
        
        # check if a library path is provided and if
        if property_changed_args.PropertyName == "SelectedColumnFilterValue" or property_changed_args.PropertyName == "SelectedColumnFilterItem":
            print("Filtering... {}".format(property_changed_args.PropertyName))
            
        
            # get the column index of the selected filter item
            column_index = self._data_table.Columns.IndexOf(self.SelectedColumnFilterItem)
            print("Column index: ", column_index)
            #self.DataView.RowFilter = "" #self.filter_families
    
    
    def refresh_view(self):
        """
        Refreshes the view by updating the families collection and the unique values for the column filters.
        """
        # refreshes the view in the UI
        self._rooms_view.Refresh()
    
    
    def close_window(self, window):
        """
        Closes the window that is passed in as an argument. 
        """
        
        if window:
            window.Close()