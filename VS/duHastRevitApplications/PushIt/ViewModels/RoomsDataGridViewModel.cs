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

using duHastNet.PushIt.Models;
using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;

namespace duHastNet.PushIt.ViewModels
{
    public class RoomsDataGridViewModel : duHastNet.Utils.WPF.ViewModels.BaseDynamicGridViewModel<DynamicRowData>
    {

        private Models.RevitDataModel RevitDataModel { get; set; }


        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        private Dictionary<string, Func<RoomsDataGridViewModel, object>> _columnDefaults;

        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        public Dictionary<string, Func<RoomsDataGridViewModel, object>> ColumnDefaults
        {
            get => _columnDefaults;
        }

        /// <summary>
        /// maps column ids to display names
        /// </summary>
        private Dictionary<string, string> _columnIdToParameterNameLookUp;
        public Dictionary<string, string> ColumnIdToParameterNameLookUp
        {
            get => _columnIdToParameterNameLookUp;
        }

        #region user interaction


        #region selected room

        protected override void OnSelectionChanged()
        {
            base.OnSelectionChanged();

            if (HasSelection)
            {
                //get the selected row item
                var selectedRow = SelectedItem;
                var roomId = selectedRow[Models.Constants.ColumnHeaderRoomId.Replace(" ", "")].ToString();
                SelectedRoom = RevitDataModel.GetAllRooms().FirstOrDefault(r => r.Id.Value == roomId);

                //check matching revit rooms
                if (SelectedRoom != null)
                {
                    IsMatchingRevitRoomsEmpty = SelectedRoom.MatchingRevitRooms.Count == 0;
                    IsMatchingSplitRoomsEmpty = SelectedRoom.MatchingSplitRevitRooms.Count == 0;
                }
                else
                {
                    IsMatchingRevitRoomsEmpty = true;
                    IsMatchingSplitRoomsEmpty = true;
                }
            }
            else
            {
                SelectedRoom = null;
                IsMatchingRevitRoomsEmpty = true;
                IsMatchingSplitRoomsEmpty = true;
            }
        }

        //field to store the selected room from the revit data model
        private Models.RoomDataModel _selectedRoom;

        //property to get the selected room from the revit data model
        public Models.RoomDataModel SelectedRoom
        {
            set
            {
                _selectedRoom = value;
                OnPropertyChanged(nameof(SelectedRoom));
            }

            get => _selectedRoom;
        }

        //field to store if the selected room has any matching Revit rooms
        bool _isMatchingRevitRoomsEmpty;

        //property to check if the selected room has any matching Revit rooms
        //used to determine if the button to push the selected room to Revit should be enabled
        public bool IsMatchingRevitRoomsEmpty
        {
            set
            {
                _isMatchingRevitRoomsEmpty = value;
                OnPropertyChanged(nameof(IsMatchingRevitRoomsEmpty));
            }
            get => _isMatchingRevitRoomsEmpty;

        }

        //field to store if the selected room has no matching split rooms
        bool _isMatchingSplitRoomsEmpty;

        /// <summary>
        /// property returning true if either no room is selected or the selected room has no matching split rooms
        /// </summary>
        public bool IsMatchingSplitRoomsEmpty
        {
            set
            {
                _isMatchingSplitRoomsEmpty = value;
                OnPropertyChanged(nameof(IsMatchingSplitRoomsEmpty));
            }

            get => _isMatchingSplitRoomsEmpty;

        }

        #endregion selected room

        #endregion user interaction

        #region data loading

        /// <summary>
        /// Define what columns are available for the revit categories grid
        /// </summary>
        protected override void InitializeAvailableColumns()
        {

            // Don't do anything if called from base constructor
            if (this.RevitDataModel == null) return;

            //initialise available columns with default room properties
            AvailableColumns = [ 
            
                // Basic revit category Info
                new(Models.Constants.ColumnHeaderRoomId.Replace(" ", "") , Models.Constants.ColumnHeaderRoomId, typeof(string)),
                new(Models.Constants.ColumnHeaderRoomCount.Replace(" ", "") , Models.Constants.ColumnHeaderRoomCount, typeof(int)),
                new(Models.Constants.ColumnHeaderRoomSplit.Replace(" ",""), Models.Constants.ColumnHeaderRoomSplit, typeof(int)),

            ];

            // add any other properties
            foreach (var property in RevitDataModel.GetAllParameters())
            {
                // skip the unique id property
                if (property.IsUniqueId)
                {
                    continue;
                }

                AvailableColumns.Add(
                    new AvailableColumnDefinition(property.Name.Replace(" ", ""), property.Name, typeof(string))
                    );
            }

            // Pre-compute the parameter name to column id lookup dictionary
            _columnIdToParameterNameLookUp = RevitDataModel._parameterDataContainer.GetAllParameters().ToDictionary(name => name.Name.Replace(" ", ""), name => name.Name);

            // Set up initial columns that should be visible by default
            SetupDefaultColumns();
        }


        /// <summary>
        /// Create a new revit category row with default data
        /// </summary>
        protected override DynamicRowData CreateNewRow()
        {
            return new DynamicRowData
            {
                // pre-populate some default values here if needed
                // The base class will fill in defaults for all columns
            };
        }


        /// <summary>
        /// Load data from the RevitDataModel into the grid
        /// </summary>
        private void LoadDataFromRevitDataModel()
        {
            Data.Clear();

            if (RevitDataModel?.GetAllRooms() == null || RevitDataModel?.GetAllRooms().Count == 0) return;

            foreach (var roomEntry in RevitDataModel.GetAllRooms())
            {
                try
                {
                    var rowData = CreateRowFromRoom(roomEntry);
                    Data.Add(rowData);
                }
                catch (Exception ex)
                {
                    // Log or handle individual category errors
                    System.Diagnostics.Debug.WriteLine($"Error loading room data: {ex.Message}");
                }
            }
        }


        /// <summary>
        /// Convert a room data object to a dynamic row for the grid
        /// </summary>
        private DynamicRowData CreateRowFromRoom(Models.RoomDataModel roomEntry)
        {
            var rowData = new DynamicRowData();

            // Set the standard column values
            rowData[Models.Constants.ColumnHeaderRoomId.Replace(" ", "")] = roomEntry.Id.Value;
            rowData[Models.Constants.ColumnHeaderRoomCount.Replace(" ", "")] = roomEntry.MatchingRevitRooms.Count;
            rowData[Models.Constants.ColumnHeaderRoomSplit.Replace(" ", "")] = roomEntry.MatchingSplitRevitRooms.Count;


            foreach (var property in roomEntry.Properties)
            {
                // add all other property values
                rowData[property.Name.Replace(" ", "")] = property.Value;
            }

            return rowData;
        }

        #endregion data loading

        #region event handlers

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
                case duHastNet.PushIt.Utilities.PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED:
                    //update rooms in the view model
                    LoadDataFromRevitDataModel();
                    break;

                // Add more cases for other properties as needed

                default:
                    // Handle changes for properties not explicitly handled
                    break;
            }
        }


        /// <summary>
        /// Step 7: Override DisposeManaged to unsubscribe from external event subscriptions.
        /// This is the correct place for cleanup per the migration guide — it ensures
        /// unsubscription happens regardless of how disposal is triggered.
        /// </summary>
        protected override void DisposeManaged()
        {
            // Unsubscribe from underlying model property changes
            if (RevitDataModel != null)
            {
                RevitDataModel.PropertyChanged -= Model_PropertyChanged;
            }

            base.DisposeManaged();
        }

        #endregion event handlers

        #region Private Helper Methods

        private void InitializeColumnDefaults()
        {
            //initialise with default category properties and default values
            _columnDefaults = new Dictionary<string, Func<RoomsDataGridViewModel, object>>
            {
                {Models.Constants.ColumnHeaderRoomId.Replace(" ", ""), vm => "NEW" },
                {Models.Constants.ColumnHeaderRoomCount.Replace(" ", ""), vm =>  0},
                {Models.Constants.ColumnHeaderRoomSplit.Replace(" ",""), vm => 0},
            };

            //add other properties
            // add any other properties
            foreach (var property in RevitDataModel.GetAllParameters())
            {
                // skip the unique id property
                if (property.IsUniqueId)
                {
                    continue;
                }

                // add empty string for now...
                _columnDefaults[property.Name.Replace(" ", "")] = vm => "";
            }
        }

        /// <summary>
        /// Override to restore actual room data instead of defaults when adding columns
        /// </summary>
        protected override void RestoreOrSetDefaultColumnData(string propertyName, AvailableColumnDefinition availableColumn)
        {
            if (_removedColumnData.ContainsKey(propertyName))
            {
                // Use the base implementation for restored data
                base.RestoreOrSetDefaultColumnData(propertyName, availableColumn);
            }
            else
            {
                // For new columns, populate with actual room data instead of defaults
                RestoreActualRoomData(propertyName, availableColumn);
            }
        }

        /// <summary>
        /// Populate column with actual data from rooms instead of defaults
        /// </summary>
        private void RestoreActualRoomData(string propertyName, AvailableColumnDefinition availableColumn)
        {
            var rooms = RevitDataModel.GetAllRooms();
            // For all rows, set the actual data from the corresponding room
            for (int i = 0; i < Data.Count && i < rooms.Count; i++)
            {
                var room = rooms[i];
                var rowData = Data[i];

                // Set the value based on the property name
                if (propertyName == Constants.ColumnHeaderRoomId.Replace(" ", ""))
                {
                    rowData[propertyName] = room.Id.Value;
                }
                else if (propertyName == Constants.ColumnHeaderRoomCount.Replace(" ", ""))
                {
                    rowData[propertyName] = room.MatchingRevitRooms.Count;
                }
                else if (propertyName == Constants.ColumnHeaderRoomSplit.Replace(" ", ""))
                {
                    rowData[propertyName] = room.MatchingSplitRevitRooms.Count;
                }
                else
                {
                    // Handle custom properties
                    var property = room.Properties.FirstOrDefault(p => p.Name.Replace(" ", "") == propertyName);
                    if (property != null)
                    {
                        rowData[propertyName] = property.Value ?? "";
                    }
                    else
                    {
                        // Fallback to default value
                        rowData[propertyName] = GetDefaultValueForColumn(availableColumn);
                    }
                }
            }
        }

        /// <summary>
        /// Get default value for a specific column in the catgeories context
        /// </summary>
        protected override object GetDefaultValueForColumn(AvailableColumnDefinition columnDef)
        {

            // Check if we have a custom default for this column
            if (ColumnDefaults.TryGetValue(columnDef.PropertyName, out Func<RoomsDataGridViewModel, object> defaultValueFunc))
            {
                return defaultValueFunc(this);
            }

            // Fall back to base implementation for standard types
            return GetDefaultValue(columnDef.DataType);
        }

        /// <summary>
        /// Define which columns should be read-only by default ( all of them! )
        /// </summary>
        protected override bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            return true; // Everything is locked
        }

        /// <summary>
        /// Set up the default columns that should be visible when the grid loads
        /// </summary>
        private void SetupDefaultColumns()
        {

            var defaultColumns = new List<string>();

            //check if any column id ( property name without space) is mentioned in the settings object
            //if there are columns stored in settings retrieved from file
            if (RevitDataModel.Settings.ColumnIds != null &&
                RevitDataModel.Settings.ColumnIds.Count > 0)
            {
                foreach (string columnId in RevitDataModel.Settings.ColumnIds)
                {
                    var columNameByParameter = FindColumnNameById(columnId);
                    //check if column id has a match in parameters available
                    if (columNameByParameter != null)
                    {
                        // add the id not the display value!
                        defaultColumns.Add(columnId);
                    }
                    else
                    {
                        var columnNameDefault = Constants.ColumnRoomsInfo.TryGetValue(columnId, out string displayName) ? displayName : null;
                        if (columnNameDefault != null)
                        {
                            // add the id not the display value!
                            defaultColumns.Add(columnId);
                        }
                    }
                }
            }
            else
            {
                //add reserved names first
                foreach (KeyValuePair<string, string> entry in Constants.ColumnRoomsInfo)
                {
                    defaultColumns.Add(entry.Key);
                }
            }

            foreach (var columnName in defaultColumns)
            {
                // Step 8: Use the generated command instead of calling the internal method directly.
                // AddSelectedColumn() is marked internal in the base class assembly and is not
                // accessible from this assembly. AddSelectedColumnCommand is public.
                AddSelectedColumnCommand.Execute(columnName);
            }

        }

        public string FindColumnNameById(string id)
        {
            return _columnIdToParameterNameLookUp.TryGetValue(id, out string displayName) ? displayName : null;
        }
        #endregion

        public override void AssociateWithDataGrid(DynamicDataGrid dataGrid)
        {
            System.Diagnostics.Debug.WriteLine($"AssociateWithDataGrid called. Grid is: {(dataGrid == null ? "null" : "not null")}");
            System.Diagnostics.Debug.WriteLine($"Pending state to apply: {(_pendingStateToApply == null ? "null" : "exists")}");

            base.AssociateWithDataGrid(dataGrid);
        }

        public RoomsDataGridViewModel(
            Models.RevitDataModel revitDataModel,
            StateStore stateStore)
            : base(stateStore)  // Pass StateStore to base to allow state saving)
        {
            // Base constructor will call InitializeAvailableColumns()
            // and set up all the commands

            this.RevitDataModel = revitDataModel;

            // manually call this since it was skipped during base constructor
            InitializeAvailableColumns();

            // Initialize column defaults first
            InitializeColumnDefaults();

            // Populate the grid with data from the sheets model
            LoadDataFromRevitDataModel();

            //subscribe to underlying model changes
            RevitDataModel.PropertyChanged += Model_PropertyChanged;

        }
    }
}