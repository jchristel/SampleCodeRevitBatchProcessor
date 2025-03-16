//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//


using duHast.PushIt.Utilities;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Data;
using System.Linq;
using System.Windows.Data;
using System.Windows.Input;

namespace duHast.PushIt.ViewModels
{
    public class RoomsSelectionViewModel : Utils.WPF.ViewModels.ViewModelBase, INotifyDataErrorInfo
    {
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly RevitExternalEventHandlerManager _eventManager;
        private readonly Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        // data table containing push it data
        private DataTable _dt;
        // default view of the data table
        private DataView _dv;

        //flag to indicate if safety off mode is enabled
        private bool _safetyOffMode = false;
        //default button text for safety off mode
        private string _safetyOffButtonText = "Safety on";

        private string _activeDesignSetName = duHast.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME;
        private string _activeDesignOptionName = duHast.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME;

        //observable collection of supported categories in Revit to push data into
        private readonly ObservableCollection<SupportedCategoryViewModel> _supportedCategories;
        //default view of the supported categories collection
        private ICollectionView _supportedCategoriesView;

        //command to raise an event to refresh the gui
        private readonly Commands.RaiseRevitEventCommand _raiseRefreshGUICommand;
        //command to push a single room to revit
        private readonly Commands.PushSingleRoomDataToRevitCommand _raisePushSingleRoomCommand;
        //command to raise an event to reload data from file path
        private readonly Commands.ReloadDataCommand _raiseReloadDataCommand;
        //command to highlight a room in Revit
        private readonly Commands.HighlightRoomsInRevitCommand _highLightRoomCommand;
        //command to wipe stale rooms data
        private readonly Commands.RaiseRevitEventCommand _wipeStaleRoomsDataCommand;
        //command to update from changed categories
        private readonly Commands.UpdateFromChangedCategoriesCommand _updateFromChangedCategoriesCommand;
        //command to update all rooms in revit from data model
        private readonly Commands.RaiseRevitEventCommand _updateAllRoomsCommand;

        //property to check if there are any errors
        public bool HasErrors => _errorsViewModel.HasErrors;
        // event handler for errors changed
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;

        // flag indicating whether the view model is waiting for a Revit command to finish
        private bool _isWaitingForRevitCommandToFinish;
        public bool IsWaitingForRevitCommandToFinish
        {
            get => _isWaitingForRevitCommandToFinish;
            set
            {
                _isWaitingForRevitCommandToFinish = value;
                OnPropertyChanged(nameof(IsWaitingForRevitCommandToFinish));
            }
        }

        #region settings

        private string _dataFilePath;
        public string DataFilePath
        {
            get => _dataFilePath;
            set
            {
                _dataFilePath = value;
                
                _errorsViewModel.ClearErrors(nameof(DataFilePath));

                // check if the file path is valid, if not add an error
                if (string.IsNullOrEmpty(value))
                {
                    // set the data path to invalid
                    _dataFilePathValid = false;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.AddError(nameof(DataFilePath), "Data file path cannot be empty");
                }
                else if (!System.IO.File.Exists(value))
                {
                    // set the data path to invalid
                    _dataFilePathValid = false;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.AddError(nameof(DataFilePath), "Data file path does not exist");
                }
                else
                {
                    // set the data path to valid
                    _dataFilePathValid = true;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.ClearErrors(nameof(DataFilePath));
                    
                    // update the data path in the settings
                    _revitDataModel.Settings.DataPath = value;
                }

                // call ui update
                OnPropertyChanged(nameof(DataFilePath));
                
            }
        }

        private bool _dataFilePathValid;
        public bool DataFilePathValid
        {
            get => _dataFilePathValid;
        }

        //is UI in safety off mode ? (rooms can be pushed multiple times)
        public bool SafetyOffMode
        {
            get => _safetyOffMode;
            set
            {
                _safetyOffMode = value;

                // set the button text
                _safetyOffButtonText = value ? "Safety off" : "Safety on";

                //debug
                //IsWaitingForRevitCommandToFinish = value;

                // notify ui of changes
                OnPropertyChanged(nameof(SafetyOffButtonText));
                OnPropertyChanged(nameof(SafetyOffMode));
            }
        }

        //button text for safety off mode
        public string SafetyOffButtonText
        {
            get => _safetyOffButtonText;
        }

        // the currently active design set name
        public string ActiveDesignSetName
        {
            get => _activeDesignSetName;
            set
            {
                _activeDesignSetName = value;
                OnPropertyChanged(nameof(ActiveDesignSetName));
            }
        }

        // the currently active design option name
        public string ActiveDesignOptionName
        {
            get => _activeDesignOptionName;
            set
            {
                _activeDesignOptionName = value;
                OnPropertyChanged(nameof(ActiveDesignOptionName));
            }
        }

        #endregion settings

        #region Column Filtering

        // Field to return a default list of column names
        private readonly List<string> _columnNameDefaultList = new List<string>
        {
            "Id",
            "Count"
        };

        // Property to expose the default list of column names
        public List<string> ColumnNameDefaultList => _columnNameDefaultList;

        // field to store the selected column filter item
        private string _selectedColumnFilterItem;
        public string SelectedColumnFilterItem
        {
            get => _selectedColumnFilterItem;
            set
            {
                _selectedColumnFilterItem = value;
                OnPropertyChanged(nameof(SelectedColumnFilterItem));
                
                //update is filter applied property
                OnPropertyChanged(nameof(IsFilterApplied));
            }
        }

        // field to store the filter value
        private string _filterValue;
        public string FilterValue
        {
            get => _filterValue;
            set
            {
                _filterValue = value;
                OnPropertyChanged(nameof(FilterValue));

                //update is filter applied property
                OnPropertyChanged(nameof(IsFilterApplied));

            }
        }

        // Property to indicate if a filter is applied
        public bool IsFilterApplied => !string.IsNullOrEmpty(SelectedColumnFilterItem) && !string.IsNullOrEmpty(FilterValue);

        #endregion Column Filtering

        #region user selection

        //binding in xaml property to the default view of the rooms collection
        public DataView DataView { 
            get => _dv;
            private set 
            {
                _dv = value;
                OnPropertyChanged(nameof(DataView));
            }

        }
        
        //binding in xaml property to the default view of the supported categories collection
        public ICollectionView SupportedCategories => _supportedCategoriesView;

        //binding to show selected index
        private int _selectedIndex;

        public int SelectedIndex
        {
            get => _selectedIndex;
            set
            {
                if (_selectedIndex != value)
                {
                    _selectedIndex = value;
                    OnPropertyChanged(nameof(SelectedIndex));
                    OnPropertyChanged(nameof(SelectedRoom));
                    OnPropertyChanged(nameof(IsMatchingRevitRoomsEmpty));
                }
            }
        }

        //property to get the selected room from the revit data model
        public Models.RoomDataModel SelectedRoom
        {
            get
            {
                // check if a default view exists
                if (_dv == null)
                {
                    return null;
                }
                // check if the selected index is within the bounds of the rooms collection
                // check if the selected index is within the bounds of the rooms collection
                if (_selectedIndex >= 0 && _selectedIndex < _dv.Count)
                {
                    var selectedRow = _dv[_selectedIndex].Row;
                    var roomId = selectedRow["Id"].ToString();
                    return _revitDataModel.GetAllRooms().FirstOrDefault(r => r.Id.Value == roomId);
                }
                // return null if the selected index is out of bounds
                return null;
            }
        }

        //property to check if the selected room has any matching Revit rooms
        //used to determine if the button to push the selected room to Revit should be enabled
        public bool IsMatchingRevitRoomsEmpty
        {
            get
            {
                var selectedRoom = SelectedRoom;
                if (selectedRoom != null && SelectedIndex >=0 )
                {
                    return selectedRoom.MatchingRevitRooms.Count == 0;
                }
                // if no room is selected, return false to avoid pushing null or stale data
                else if (SelectedIndex < 0)
                {
                    return false;
                }
                return true;
            }
        }

        #endregion user selection

        #region Commands

        //commands
        public ICommand RefreshGUICommand { get { return _raiseRefreshGUICommand; } }
        public ICommand PushSingleRoomCommand { get { return _raisePushSingleRoomCommand; } }
        public ICommand ReloadDataCommand { get { return _raiseReloadDataCommand; } }
        public ICommand HighLightRoomCommand { get { return _highLightRoomCommand; } }
        public ICommand WipeStaleRoomsDataCommand { get { return _wipeStaleRoomsDataCommand; } }
        public ICommand UpdateFromChangedCategoriesCommand { get { return _updateFromChangedCategoriesCommand; } }
        public ICommand UpdateAllRoomsCommand { get { return _updateAllRoomsCommand; } }

        #endregion Commands

        /// <summary>
        /// Update the rooms in the view model by creating a data table from the rooms in the data model, 
        /// updating the default view of the data table, and updating the column filter list.
        /// </summary>
        private void UpdateRooms()
        {
            //create a data table from the rooms in the data model
            DataTable dt = CreateRoomsDataTable();
            if (dt == null)
            {
                return;
            }

            //store the data table
            _dt = dt;

            // create a data view from the data table
            // this will trigger an onproperty chaanged event
            DataView = new DataView(dt);

            // update the column filter list
            bool resetFilterValue = CreateColumnFilterItems();

            // reset the column filter value?
            if (resetFilterValue) { FilterValue = ""; }
            else
            {
                //reapply the filter
                OnPropertyChanged(nameof(FilterValue));
            }
        }


        /// <summary>
        /// Creates the data table displayed in the ui
        /// </summary>
        /// <returns></returns>
        public DataTable CreateRoomsDataTable()
        {
            // Check if there are any rooms
            if (_revitDataModel.GetAllRooms().Count == 0)
            {
                return null;
            }

            // Set up the data table
            DataTable dataTable = new DataTable();

            //add the default id column
            dataTable.Columns.Add("Id");

            // Add columns to the data table
            foreach (var roomModelInstance in _revitDataModel.GetAllRooms())
            {
                // Add a column per property
                foreach (var prop in roomModelInstance.Properties)
                {
                    // check if the column is meant to be displayed in the ui
                    if (prop.ShowInUI) { dataTable.Columns.Add(prop.Name); }
                }
                // Get out of the loop
                break;
            }

            // Add the count column
            dataTable.Columns.Add("Count");

            // Add the rows to the data table
            foreach (var roomModelInstance in _revitDataModel.GetAllRooms())
            {
                // Add a row per room
                DataRow row = dataTable.NewRow();

                // add the id value
                row["Id"] = roomModelInstance.Id.Value;

                // add the property values
                foreach (var prop in roomModelInstance.Properties)
                {
                    // check if the column is meant to be displayed in the ui
                    if (prop.ShowInUI) { row[prop.Name] = !string.IsNullOrEmpty(prop.Value) ? prop.Value : ""; }
                }
                row["Count"] = roomModelInstance.MatchingRevitRooms.Count;
                dataTable.Rows.Add(row);
            }

            return dataTable;
        }


        /// <summary>
        /// populates the column filter items list the user can chpoose to filter by in the UI
        /// </summary>
        /// <returns>true if column filter list changed, otherwise false.</returns>
        public bool CreateColumnFilterItems()
        {
            // Check if the data table is null
            if (_dt == null)
            {
                return false;
            }

            // Get the columns from the data table
            var columns = _dt.Columns;

            bool filterListNeedsUpdating = false;

            if (_columnNameDefaultList.Count == columns.Count)
            {
                //identical length ... make sure its the same values in both lists
                //only update the filter list if new list is different to existing values
                foreach (DataColumn column in columns)
                {
                    if (!_columnNameDefaultList.Contains(column.ColumnName))
                    {
                        filterListNeedsUpdating = true;
                        break;
                    }
                }
            }
            else
            {
                // got different length...needs updating
                filterListNeedsUpdating = true;
            }

            // if the list does not need updating get out
            if (!filterListNeedsUpdating)
            {
                return false;
            }

            // Clear the old entries
            _columnNameDefaultList.Clear();

            // Add the column names to the column filter items
            foreach (DataColumn column in columns)
            {
                _columnNameDefaultList.Add(column.ColumnName);
            }

            // Notify UI of changes
            OnPropertyChanged(nameof(ColumnNameDefaultList));

            return true;
        }


        /// <summary>
        /// Update available and supported categories collection in UI from revit data model.
        /// </summary>
        public void UpdateCategories()
        {
            //loop over categories supported as per data model and categories used in settings and add to the supported categories collection
            _supportedCategories.Clear();
            foreach (Models.CategoryDataModel category in _revitDataModel.GetAllCategories())
            {
                {
                    bool isUsed = _revitDataModel.Settings.SupportedCategories.Contains(category.Name);
                    ViewModels.SupportedCategoryViewModel categoryViewModel = new SupportedCategoryViewModel(category, isUsed);
                    _supportedCategories.Add(categoryViewModel);
                }
            }
            _supportedCategoriesView.Refresh();
            OnPropertyChanged(nameof(SupportedCategories));
        }

        /// <summary>
        /// The row filter applied to the data table default view
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="propertyChangedArgs"></param>
        private void FilterRoomData(object sender, PropertyChangedEventArgs propertyChangedArgs)
        {
            try
            {
                // Check if either the selected column filter value or the selected column filter item has changed
                if (propertyChangedArgs.PropertyName == nameof(SelectedColumnFilterItem) ||
                    propertyChangedArgs.PropertyName == nameof(FilterValue))
                {
                    // Check if the data view is null, if so get out of the function since there is nothing to filter
                    if (DataView == null)
                    {
                        return;
                    }

                    // Check if the filter value is empty
                    if (string.IsNullOrEmpty(SelectedColumnFilterItem))
                    {
                        // Clear the filter on the data view
                        DataView.RowFilter = string.Empty;
                        return;
                    }

                    // Check if the column name contains a space, if so add square brackets to the column name
                    string columnName = SelectedColumnFilterItem;
                    if (SelectedColumnFilterItem.Contains(" "))
                    {
                        columnName = $"[{SelectedColumnFilterItem}]";
                    }

                    // Create the filter value for the data view
                    // Check if the column value contains the filter value
                    string filterValue = $"{columnName} LIKE '%{FilterValue}%'";

                    // Filter the data view
                    try
                    {
                        // Set the filter on the data view
                        DataView.RowFilter = filterValue;
                        // Let the UI know that the data view has changed to force a refresh
                        OnPropertyChanged(nameof(DataView));
                    }
                    catch (Exception e)
                    {
                        AddMessage($"Failed to apply filter to data: {e.Message}", Utils.WPF.Stores.MessageTypes.Error);
                    }
                }
            }
            catch (Exception ex)
            {
                AddMessage($"Failed to filter data: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }
            return;
        }


        /// <summary>
        /// used to catch property changed events from the underlying model in order to update the ui
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Model_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check which property changed in the underlying model
            switch (e.PropertyName)
            {
                case PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED:
                    //update rooms in the view model
                    UpdateRooms();
                    break;

                // Add more cases for other properties as needed

                default:
                    // Handle changes for properties not explicitly handled
                    break;
            }
        }


        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {
            
            _messageStore.SetCurrentMessage(message, messageType);
        }


        // not sure whether this is actually required or not
        // when on closing, dispose of the event manager
        // and remove the event handler
        public override void Dispose()
        {
            base.Dispose();
        }


        /// <summary>
        /// Custom closing logic for RoomsSelectionViewModel
        /// Disposes all external events from the event manager
        /// </summary>
        public override void OnClosing()
        {
            // Custom closing logic for RoomsSelectionViewModel
            _eventManager.DisposeEvents();

            //unbsubscribe from underlying model changes
            _revitDataModel.PropertyChanged -= Model_PropertyChanged;

            //unsubscribe from errors changed event
            _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;
            GlobalMessageViewModel.Dispose();

            base.OnClosing();
        }


        /// <summary>
        /// Data validation for text input fields
        /// </summary>
        /// <param name="propertyName">The name of the property of which to get any errors, if they exist, for.</param>
        /// <returns></returns>
        /// <exception cref="NotImplementedException"></exception>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }


        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            ErrorsChanged?.Invoke(this, e);
            // update the data file path valid property
            OnPropertyChanged(nameof(DataFilePathValid));
        }

        /// <summary>
        /// The rooms selection view model class constructor.
        /// </summary>
        /// <param name="revitDataModel">The underlying revit data model</param>
        /// <param name="navigationStore">A navigation store for the UI</param>
        /// <param name="messageStore">A message store used to display messages to the user</param>
        /// <param name="eventManager"></param>
        /// <param name="globalMessageViewModel">A message view model, the message store uses to display messages to the user.</param>
        public RoomsSelectionViewModel(
            Models.RevitDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.MessageStore messageStore,
            RevitExternalEventHandlerManager eventManager,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel)
        {
            //store services
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;
            _eventManager = eventManager;

            //initialize the errors view model
            _errorsViewModel = new Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;

            // supported categories collection
            _supportedCategories = new ObservableCollection<SupportedCategoryViewModel>();
            _supportedCategoriesView = CollectionViewSource.GetDefaultView(_supportedCategories);

            //set the data file path
            _dataFilePath = _revitDataModel.Settings.DataPath;

            //update supported categories from settings
            UpdateCategories();

            //subscribe to underlying model changes
            _revitDataModel.PropertyChanged += Model_PropertyChanged;

            // add the view model to the event manager
            _eventManager.RoomsSelectionViewModel = this;
            //update rooms data with data from revit through an external event
            _eventManager.RefreshUIDataEventRaise();

            //subscribe to property changed event to allow update of the data table filters
            this.PropertyChanged += FilterRoomData;

            // set up commands
            // refresh gui with data from model
            _raiseRefreshGUICommand = new Commands.RaiseRevitEventCommand(this, _revitDataModel, _messageStore, () => { _eventManager.RefreshUIDataEventRaise(); });
            // push single room to revit
            _raisePushSingleRoomCommand = new Commands.PushSingleRoomDataToRevitCommand(this, _revitDataModel, _messageStore, () => { _eventManager.PushItSingleEventRaise(); });
            //load data from file path
            _raiseReloadDataCommand = new Commands.ReloadDataCommand(this, _revitDataModel, _messageStore, () => { _eventManager.ReloadDataEventRaise(); });
            //highlight room in Revit
            _highLightRoomCommand = new Commands.HighlightRoomsInRevitCommand(this, _revitDataModel, _messageStore, () => { _eventManager.HighlightSelectedRoomEventRaise(); });
            //wipe stale rooms data
            _wipeStaleRoomsDataCommand = new Commands.RaiseRevitEventCommand(this, _revitDataModel, _messageStore, () => { _eventManager.WipeStaleRoomDataEventRaise(); });
            //update from changed categories
            _updateFromChangedCategoriesCommand = new Commands.UpdateFromChangedCategoriesCommand(this, _revitDataModel, _messageStore, () => { _eventManager.UpdateAfterSupportedCategoryChangeEventRaise(); });
            //update all rooms in revit from data model
            _updateAllRoomsCommand = new Commands.RaiseRevitEventCommand(this, _revitDataModel, _messageStore, () => { _eventManager.UpdateAllRoomsInRevitEventRaise(); });
        }
    }
}
