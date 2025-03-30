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


using duHast.Utils.WPF.Commands;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Linq;

using System.Windows.Input;

namespace duHast.AtTheLibrary.ViewModels
{
    public class FamiliesSelectionViewModel : Utils.WPF.ViewModels.ViewModelBase, INotifyDataErrorInfo
    {
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Models.RevitFamiliesDataModel _revitDataModel;
        private readonly Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        // data table containing push it data
        private DataTable _dt;
        // default view of the data table
        private DataView _dv;

        //command to raise an event to refresh the gui
        private readonly Commands.RefreshUIFromRevitModelAsyncCommand _raiseRefreshGUICommand;
        //command to push a single room to revit
        //private readonly Commands.PushSingleRoomInRevitAsyncCommand _raisePushSingleRoomCommand;
        
        //command to update the view model if the column order changes
        public RelayCommand ColumnOrderChangedCommand { get; private set; }

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
                    DataFilePathValid = false;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.AddError(nameof(DataFilePath), "Data file path cannot be empty");
                }
                else if (!System.IO.File.Exists(value))
                {
                    // set the data path to invalid
                    DataFilePathValid = false;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.AddError(nameof(DataFilePath), "Data file path does not exist");
                }
                else
                {
                    // set the data path to valid
                    DataFilePathValid = true;
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
            set
            { 
                _dataFilePathValid = value;
                // call ui update
                OnPropertyChanged(nameof(DataFilePathValid));
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

        //binding in xaml property to the default view of the families collection
        public DataView DataView { 
            get => _dv;
            private set 
            {
                _dv = value;
                OnPropertyChanged(nameof(DataView));
            }

        }

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
                    OnPropertyChanged(nameof(SelectedFamily));
                    OnPropertyChanged(nameof(IsMatchingRevitFamiliesEmpty));
                }
            }
        }

        //property to get the selected room from the revit data model
        public Models.FamilyDataModel SelectedFamily
        {
            get
            {
                // check if a default view exists
                if (_dv == null)
                {
                    return null;
                }
                // check if the selected index is within the bounds of the rooms collection
                if (_selectedIndex >= 0 && _selectedIndex < _dv.Count)
                {
                    var selectedRow = _dv[_selectedIndex].Row;
                    var roomId = selectedRow["Id"].ToString();
                    return _revitDataModel.GetAllFamilies().FirstOrDefault(r => r.Id.Name == roomId);
                }
                // return null if the selected index is out of bounds
                return null;
            }
        }

        //property to check if the selected family has any matches in the project file
        //used to determine if the button to TODO should be enabled
        public bool IsMatchingRevitFamiliesEmpty
        {
            get
            {
                var selectedRoom = SelectedFamily;
                if (selectedRoom != null && SelectedIndex >=0 )
                {
                    return selectedRoom.MatchingRevitFamilies.Count == 0;
                }
                // if no family is selected, return false to avoid  TODO
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
        //public ICommand PushSingleRoomCommand { get { return _raisePushSingleRoomCommand; } }
       

        #endregion Commands

        #region column order

        //property to store the column order
        private IEnumerable<string> _columnOrder;

        //property to expose the column order
        public IEnumerable<string> ColumnOrder
        {
            get => _columnOrder;
            set
            {
                _columnOrder = value;
            }
        }

        /// <summary>
        /// Relay command target for column order changed event
        /// </summary>
        private void OnColumnOrderChanged(object parameter)
        {
            if (parameter is Tuple<IEnumerable<string>, DataView> data && data.Item2 is DataView dataView)
            {
                // update the column order
                ColumnOrder = data.Item1;
            }
        }

        #endregion column order

        /// <summary>
        /// Update the rooms in the view model by creating a data table from the rooms in the data model, 
        /// updating the default view of the data table, and updating the column filter list.
        /// </summary>
        private void UpdateFamilies()
        {
            //create a data table from the rooms in the data model
            DataTable dt = CreateFamiliesDataTable();
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
        public DataTable CreateFamiliesDataTable()
        {
            // Check if there are any rooms
            if (_revitDataModel.GetAllFamilies().Count == 0)
            {
                return null;
            }

            // Set up the data table
            DataTable dataTable = new DataTable();

            // Check if the column order is not null and has any elements
            // if so add columns to the data table in the order specified by the column order
            if (ColumnOrder != null && ColumnOrder.Any())
            {
                // Add columns to the data table in the order specified by the column order
                foreach (var column in ColumnOrder)
                {
                    //check for default columns
                    if (column == "Count")
                    {
                        dataTable.Columns.Add("Count");
                        continue;
                    }
                    else if (column == "Id")
                    {
                        dataTable.Columns.Add("Id");
                        continue;
                    }
                    else if (column == "Family Name")
                    {
                        dataTable.Columns.Add("Family Name");
                        continue;
                    }
                    else if (column == "Family Category")
                    {
                        dataTable.Columns.Add("Family Category");
                        continue;
                    }
                    else if (column == "Family Type Name")
                    {
                        dataTable.Columns.Add("Family Type Name");
                        continue;
                    }
                    else
                    {
                        // Add a column per property
                        foreach (var roomModelInstance in _revitDataModel.GetAllFamilies())
                        {
                            // Add a column per property
                            foreach (var prop in roomModelInstance.Properties)
                            {
                                // check if the column is meant to be displayed in the ui
                                if (prop.ShowInUI && prop.Name == column) { 
                                    dataTable.Columns.Add(prop.Name);
                                    break;
                                }
                            }
                            // Get out of the loop
                            break;
                        }
                    }
                }
            }
            else
            {
                //othrwise add columns in default order
                //add the default id column
                dataTable.Columns.Add("Id");
                // add default family name
                dataTable.Columns.Add("Family Name");
                // add default family category
                dataTable.Columns.Add("Family Category");
                // add default family type name
                dataTable.Columns.Add("Family Type Name");

                // Add columns to the data table
                foreach (var roomModelInstance in _revitDataModel.GetAllFamilies())
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
            }

            

            // Add the rows to the data table
            foreach (var familyModelInstance in _revitDataModel.GetAllFamilies())
            {
                // Add a row per room
                DataRow row = dataTable.NewRow();

                //add properties to the row in order specified by the column order
                if (ColumnOrder != null && ColumnOrder.Any())
                {
                    // Add columns to the data table in the order specified by the column order
                    foreach (var column in ColumnOrder)
                    {
                        if (column == "Count")
                        {
                            row["Count"] = familyModelInstance.MatchingRevitFamilies.Count;
                            continue;
                        }
                        else if (column == "Id")
                        {
                            row["Id"] = familyModelInstance.Id.Value;
                            continue;
                        }
                        else if(column == "Family Name")
                        {
                            row["Family Name"] = familyModelInstance.FamilyName.Value;
                            continue;
                        }
                        else if (column == "Family Category")
                        {
                            row["Family Category"] = familyModelInstance.FamilyCategory.Value;
                            continue;
                        }
                        else if (column == "Family Type Name")
                        {
                            row["Family Type Name"] = familyModelInstance.FamilyTypeName.Value;
                            continue;
                        }
                        else
                        {
                            // Add the property values
                            foreach (var prop in familyModelInstance.Properties)
                            {
                                // check if the column is meant to be displayed in the ui
                                if (prop.ShowInUI && prop.Name == column) { 
                                    row[prop.Name] = !string.IsNullOrEmpty(prop.Value) ? prop.Value : "";
                                    break;
                                }
                            }
                        }
                    }
                    // Add the row to the data table
                    dataTable.Rows.Add(row);
                }
                else
                {
                    //add data to the row in default order
                    // add the id value
                    row["Id"] = familyModelInstance.Id.Value;
                    // add the family name
                    row["Family Name"] = familyModelInstance.FamilyName.Value;
                    // add the family category
                    row["Family Category"] = familyModelInstance.FamilyCategory.Value;
                    // add the family type name
                    row["Family Type Name"] = familyModelInstance.FamilyTypeName.Value;


                    // add the property values
                    foreach (var prop in familyModelInstance.Properties)
                    {
                        // check if the column is meant to be displayed in the ui
                        if (prop.ShowInUI) { row[prop.Name] = !string.IsNullOrEmpty(prop.Value) ? prop.Value : ""; }
                    }
                    row["Count"] = familyModelInstance.MatchingRevitFamilies.Count;
                    // Add the row to the data table
                    dataTable.Rows.Add(row);
                }
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
                case Utilities.PropertyChangedEventNames.DATA_MODEL_FAMILIES_UPDATED:
                    //update rooms in the view model
                    UpdateFamilies();
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
            //_eventManager.DisposeEvents();

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
        /// <param name="globalMessageViewModel">A message view model, the message store uses to display messages to the user.</param>
        public FamiliesSelectionViewModel(
            Models.RevitFamiliesDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.MessageStore messageStore,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel)
        {
            //store services
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;

            //initialize the errors view model
            _errorsViewModel = new Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;

            //initialize column order
            _columnOrder = new List<string>();

            //set the data file path
            DataFilePath = _revitDataModel.Settings.DataPath;

            //subscribe to underlying model changes
            _revitDataModel.PropertyChanged += Model_PropertyChanged;

            //subscribe to property changed event to allow update of the data table filters
            this.PropertyChanged += FilterRoomData;

            // set up commands
            // refresh gui with data from model
            _raiseRefreshGUICommand = new Commands.RefreshUIFromRevitModelAsyncCommand(
               familiesSelectionViewModel: this,
               revitFamiliesDataModel: _revitDataModel);

            // push single room to revit
            //_raisePushSingleRoomCommand = new Commands.PushSingleRoomInRevitAsyncCommand(
             //   roomsSelectionViewModel: this,
             //   revitDataModel: _revitDataModel
             //);
            

            //update rooms data with data from revit through an external event
            RefreshGUICommand.Execute(null);
        }
    }
}
