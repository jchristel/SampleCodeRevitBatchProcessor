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

clr.AddReference("PresentationFramework")
clr.AddReference("WindowsBase")
clr.AddReference("System.Data")

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase

from System.Collections.ObjectModel import ObservableCollection
from System.Windows.Data import CollectionViewSource, PropertyGroupDescription
from System.Data import DataTable, DataView

# from ViewModels.FilterItem import FilterItem
from PushIt.Commands.PushRoomDataCommand import PushRoomDataCommand
from PushIt.Commands.RaiseRevitEventCommand import RaiseRevitEventCommand



class RoomsSelectionViewModel(ViewModelBase):

    # the name of the count column in the data table
    count_column_name = "Count"

    def __init__(self, revit_model, revit_model_event_handler_manager, navigation_service):
        super(RoomsSelectionViewModel, self).__init__()

        # properties
        # the revit model event handler manager
        self._revit_model_event_handler_manager = revit_model_event_handler_manager

        # can a room be pushed to revit, default is false
        # will be re-evaluated when a row is selected
        self._can_push_room_data = False

        # is safety off mode enabled (default is false)
        # safety off mode is used to allow pushing of rooms more than once to revit
        self._safety_off_mode = False

        # the revit wpf model object containing the settings and families to be displayed
        self._revit_model = revit_model

        # create the data table which is used to store the room data
        self._data_table = self.create_rooms_data_table()

        # set up a specific data view for the data table
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        self._data_view = DataView(self._data_table)

        # the selected room
        self._selected_room = None
        # the selected row index
        self._selected_index = -1

        # commands
        # the command used to raise the revit external event which in turn calls a function pushing data into the revit model family instance
        self._push_data_command = PushRoomDataCommand(
            rooms_selection_view_model=self,
            execute=self._revit_model_event_handler_manager.push_single_room_data,
        )

        # the command used to raise the revit external event which in turn calls a function refreshing the rooms in the revit model
        self._refresh_room_data_from_model_command = RaiseRevitEventCommand(
            execute=self._revit_model_event_handler_manager.pull_data_from_revit
        )

        # the command used to raise the revit external event which in turn calls a function updating the rooms in the revit model from the room data
        self._update_rooms_in_revit_from_room_data_command = RaiseRevitEventCommand(
            execute=self._revit_model_event_handler_manager.update_all_revit_rooms
        )

        # the command used to raise the revit external event which in turn calls a function wiping stale room data
        self._wipe_stale_room_data_command = RaiseRevitEventCommand(
            execute=self._revit_model_event_handler_manager.wipe_stale_data
        )

        # list containing the column names for the filter
        self._column_filter_items = []

        # create the column filter items (list of column headers to filter by)
        self.create_column_filter_items()

        # set the default column to filter by
        self._selected_column_to_filter = self._column_filter_items[0]

        # set the default filter value
        self._selected_filter_value = ""

        # event handlers
        self.add_PropertyChanged(self.filter_room_data)

    @property
    def DataView(self):
        """
        The collection view of the data collection. to which the xaml view is bound to.
        """

        return self._data_view

    @property
    def SafetyOffMode(self):
        """
        A boolean value indicating if the safety off mode is enabled.
        """

        return self._safety_off_mode

    @SafetyOffMode.setter
    def SafetyOffMode(self, value):
        """
        Sets the safety off mode.
        """

        self._safety_off_mode = value
        # raise property change event
        self.RaisePropertyChanged("SafetyOffMode")

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

        return self._selected_column_to_filter

    @SelectedColumnFilterItem.setter
    def SelectedColumnFilterItem(self, value):
        """
        Sets the selected column name to filter by.
        """

        self._selected_column_to_filter = value
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
    def CanPushRoomData(self):
        """
        A boolean value indicating if the room data can be pushed to the revit model.
        """

        return self._can_push_room_data

    @property
    def SelectedRoom(self):
        """
        The selected room.
        """

        return self._selected_room

    @property
    def SelectedIndex(self):
        """
        The selected row index of the data table view.
        """

        return self._selected_index

    @SelectedIndex.setter
    def SelectedIndex(self, value):
        """
        Sets the selected row index of the data table view. 
        
        This is used to: 
        
        - get the selected room.
        - set the flag as to whether a room can be pushed to the revit model.

        
        :param value: The selected row index.
        :type value: int
        """

        # this returns the row index of the filtered default view not the actual data table.
        self._selected_index = value
        try:
            # get the row view from the data table view
            row_view = self._data_table.DefaultView[value]
            # get the original row from the data table
            row = row_view.Row

            # update the selected room
            self._selected_room = None
            # get the selected room based on the id
            self._selected_room = self._revit_model.get_room_by_id(row[0])
            # set the selected room in the revit model to make it available for pushing
            self._revit_model.room_of_interest = self._selected_room

            # set the flag as to whether a room can be pushed to the revit model
            self._can_push_room_data = row[row.Table.Columns.Count - 1] == "0"

            # raise property change event for the selected row content
            # this will trigger a re-evaluation of push it command availability
            self.RaisePropertyChanged("SelectedIndexChanged")
        except Exception as e:
            print("Error: ", e)

    @property
    def PushItCommand(self):
        """
        The command used to when the reload button in the view is clicked.

        Stores the selected family objects in the revit model object and triggers the close of the window.
        """
        
        return self._push_data_command

    @property
    def RefreshRoomDataFromModelCommand(self):
        """
        The command used to refresh the room data from the revit model.

        This is used when the user wants to refresh the room data in the view.
        """

        return self._refresh_room_data_from_model_command

    @property
    def UpdateRoomsInRevitFromRoomDataCommand(self):
        """
        The command used to update the rooms in the revit model from the room data.

        This is used when the user wants to update the rooms in the revit model from the room data.
        """

        # scaffold the command
        return self._update_rooms_in_revit_from_room_data_command

    @property
    def WipeStaleRoomDataCommand(self):
        """
        The command used to wipe stale room data.

        This is used when the user wants to wipe stale room data.
        """

        # scaffold the command
        return self._wipe_stale_room_data_command

    def create_column_filter_items(self):
        """
        Creates the column filter items (list of column headers to filter by).
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

    def filter_room_data(self, sender, property_changed_args):
        """
        Filters the room data based on the selected filter column and filter value entered.

        """

        # check if either the selected column filter value or the selected column filter item has changed
        if (
            property_changed_args.PropertyName == "SelectedColumnFilterValue"
            or property_changed_args.PropertyName == "SelectedColumnFilterItem"
        ):

            # check if the filter value is empty
            if self.SelectedColumnFilterValue == "":
                self.DataView.RowFilter = ""
                return

            # check if the column name contains a space
            # if so add square brackets to the column name
            column_name = self.SelectedColumnFilterItem
            if " " in self.SelectedColumnFilterItem:
                column_name = "[{}]".format(self.SelectedColumnFilterItem)

            # create the filter value for the data view
            # check if the column value contains the filter value
            filter_value = "{} LIKE '%{}%'".format(
                column_name, self.SelectedColumnFilterValue
            )

            # filter the data view
            try:
                self.DataView.RowFilter = filter_value
                # let the ui know that the data view has changed
                self.RaisePropertyChanged("DataView")
            except Exception as e:
                print("Error: ", e)

    def close_window(self, window):
        """
        Closes the window that is passed in as an argument.
        """

        if window:
            window.Close()
