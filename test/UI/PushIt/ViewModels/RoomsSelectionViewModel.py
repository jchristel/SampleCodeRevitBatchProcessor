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
A view model class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


It displays the rooms data in a data grid view and allows the user to filter the data by column name and value.

Room data will need updating:

1 at start up: where the room data is read from the data file, the revit model is interrogated for already placed room place holders and the result is displayed in the data grid view.
2 when a single room is pushed to revit: the room data is updated in the revit model and the data grid view.
3 when all rooms are pushed to revit: the room data is updated in the revit model and the data grid view.
4 when the room data is refreshed from the revit model: the room data is updated in the data grid view.
5 when the room data path is changed to a new file: the room data is updated in the data grid view based on the new file and place holders in the revit model.

All of the above cases will need an external event triggered to get access to the current revit model.


Room data displayed will not need updating:

1 when the room data is wiped from stale rooms: the room data is updated in the data grid view.


"""

import clr

clr.AddReference("PresentationFramework")
clr.AddReference("WindowsBase")
clr.AddReference("System.Data")
from System.Data import DataTable, DataView

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase

from PushIt.Commands.PushRoomDataCommand import PushRoomDataCommand
from PushIt.Commands.RaiseRevitEventCommand import RaiseRevitEventCommand
from PushIt.Utilities import event_names

class RoomsSelectionViewModel(ViewModelBase):

    # the name of the count column in the data table
    count_column_name = "Count"

    def __init__(
        self, revit_model, revit_model_event_handler_manager, navigation_service
    ):
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

        # set the data path
        self._data_path = self._revit_model.settings.rooms_data_file_path

        # the selected room
        self._selected_room = None
        # the selected row index
        self._selected_index = -1

        # set up class properties with default values
        # these will be changed a little further down in the constructor
        # but I need to set them up here to avoid errors
        self._selected_column_to_filter = None
        self._selected_filter_value = ""

        # list containing the column names for the filter
        self._column_filter_items = []

        # set up a specific data view for the data table
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        self._data_view = None

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

        # subscribe to the rooms changed event
        self._revit_model.add_PropertyChanged(self.update_room_data)

        # raise event to populate room data in the view
        self._revit_model_event_handler_manager.setup_data()

        # event handlers
        # event handler to filter the room data upon filter selection or filter value entered/changed
        self.add_PropertyChanged(self.filter_room_data)

        # the code below will need to go into an event handler only executed when the data is ready
        # this is just a placeholder for now

        # create the data table which is used to store the room data
        # self._data_table = self.create_rooms_data_table()

        # set up a specific data view for the data table
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        # self._data_view = DataView(self._data_table)
        # self._data_view = None

        # # create the column filter items (list of column headers to filter by)
        # self.create_column_filter_items()

        # # event handlers
        # self.add_PropertyChanged(self.filter_room_data)

        # # set the default column to filter by
        # if self._revit_model.settings.last_column_filter in self._column_filter_items:
        #     self.SelectedColumnFilterItem = (
        #         self._revit_model.settings.last_column_filter
        #     )
        # else:
        #     self.SelectedColumnFilterItem = self._column_filter_items[0]

        # # set the default filter value
        # if (
        #     self._revit_model.settings.last_column_filter_value
        #     and self._revit_model.settings.last_column_filter_value != ""
        # ):
        #     self.SelectedColumnFilterValue = (
        #         self._revit_model.settings.last_column_filter_value
        #     )
        # else:
        #     self.SelectedColumnFilterValue = ""

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

        # raise property change event for safety off mode
        self.RaisePropertyChanged(event_names.VIEW_MODEL_SAFETY_OFF_MODE)

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

        # raise property change event to update the data table filters
        self.RaisePropertyChanged(event_names.VIEW_MODEL_SELECTED_FILTER_BY_COLUMN)
        
        # update the settings
        self._revit_model.settings.last_column_filter = value

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

        # raise property change event to update the data table filters
        self.RaisePropertyChanged(event_names.VIEW_MODEL_SELECTED_FILTER_BY_VALUE)

        # update the settings
        self._revit_model.settings.last_column_filter_value = value

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
            row_view = self._data_view[value]
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
            self.RaisePropertyChanged(event_names.VIEW_MODEL_SELECTED_ROW)
        except Exception as e:
            print("Error: ", e)

    @property
    def DataPath(self):
        """
        The path to the data file.
        """

        return self._data_path

    @DataPath.setter
    def DataPath(self, value):
        """
        Sets the path to the data file.
        """

        self._data_path = value
        # update the room data file
        self._revit_model.settings.rooms_data_file_path = value

        # raise property change event in the revit model to reload the data
        # from the new file path
        self._revit_model.RaisePropertyChanged(event_names.VIEW_MODEL_DATA_FILE_PATH)

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

    def update_room_data(self, sender, property_changed_args):
        """
        Updates the room data in the view.

        Builds a data table with the room data and sets up a specific data view for the data table.
        This is required to be able to sort, group and filter the collection view without affecting the observable collection.

        Applies filter column selection and filter value entered to the UI. Which in turn will trigger events to filter the data view.

        And finally triggers a property changed event to let the UI know that the data view has changed.

        :param sender: The sender of the event.
        :type sender: object
        :param property_changed_args: The property changed event arguments.
        :type property_changed_args: PropertyChangedEventArgs
        """

        # check if the rooms in the model have been updated and therefore the UI needs to be updated
        if property_changed_args.PropertyName != event_names.REVIT_MODEL_ROOMS_UPDATED:
            return
        
        print("Updating room data...")

        # create the data table which is used to store the room data
        data_table = self.create_rooms_data_table()

        # check if data_table was created if not get out of the function
        if data_table is None:
            return

        # set the data table
        self._data_table = data_table

        # set up a specific data view for the data table
        # this is required to be able to sort, group and filter the collection view without affecting the observable collection
        self._data_view = DataView(self._data_table)

        # create the column filter items (list of column headers to filter by)
        self.create_column_filter_items()

        # set the default column to filter by
        if self._revit_model.settings.last_column_filter in self._column_filter_items:
            self.SelectedColumnFilterItem = (
                self._revit_model.settings.last_column_filter
            )
        else:
            self.SelectedColumnFilterItem = self._column_filter_items[0]

        # set the default filter value
        if (
            self._revit_model.settings.last_column_filter_value
            and self._revit_model.settings.last_column_filter_value != ""
        ):
            self.SelectedColumnFilterValue = (
                self._revit_model.settings.last_column_filter_value
            )
        else:
            self.SelectedColumnFilterValue = ""

        # let the ui know that the data view has changed
        self.RaisePropertyChanged(event_names.VIEW_MODEL_DATA_VIEW_UPDATED)

    def create_column_filter_items(self):
        """
        Populates the column filter items (list of column headers to filter by).
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

        :return: The data table with the rooms data, or None if there are no rooms.
        :rtype: DataTable or None
        """

        # check if there are any rooms
        if len(self._revit_model.get_all_rooms()) == 0:
            return None

        # set up the data table
        data_table = DataTable()

        print(
            "Creating data table...of {} rooms.".format(
                len(self._revit_model.get_all_rooms())
            )
        )
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

        :param sender: The sender of the event.
        :type sender: object
        :param property_changed_args: The property changed event arguments.
        :type property_changed_args: PropertyChangedEventArgs
        """

        # check if either the selected column filter value or the selected column filter item has changed
        if (
            property_changed_args.PropertyName == event_names.VIEW_MODEL_SELECTED_FILTER_BY_COLUMN
            or property_changed_args.PropertyName == event_names.VIEW_MODEL_SELECTED_FILTER_BY_VALUE
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
                self.RaisePropertyChanged(event_names.VIEW_MODEL_DATA_VIEW_UPDATED)
            except Exception as e:
                print("Error: ", e)
