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
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;

namespace duHastNet.PushIt.ViewModels
{
    public class RoomsDataGridViewModel : BaseDynamicGridViewModel<DynamicRowData>
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
        /// Define what columns are available for the revit categories grid
        /// </summary>
        protected override void InitializeAvailableColumns()
        {

            // Don't do anything if called from base constructor
            if (this.RevitDataModel == null) return;

            //initialise available columns with default room properties
            AvailableColumns = new ObservableCollection<AvailableColumnDefinition> { 
            
                // Basic revit category Info
                new AvailableColumnDefinition(Models.Constants.ColumnHeaderRoomId.Replace(" ", "") , Models.Constants.ColumnHeaderRoomId, typeof(string)),
                new AvailableColumnDefinition(Models.Constants.ColumnHeaderRoomCount.Replace(" ", "") , Models.Constants.ColumnHeaderRoomCount, typeof(int)),
                new AvailableColumnDefinition(Models.Constants.ColumnHeaderRoomSplit.Replace(" ",""), Models.Constants.ColumnHeaderRoomSplit, typeof(int)),

            };

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
                rowData[property.Name]= property.Value;
            }

            return rowData;
        }

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
                case  duHastNet.PushIt.Utilities.PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED:
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
        /// Custom closing logic for RoomsSelectionViewModel
        /// Disposes all external events from the event manager
        /// </summary>
        //public override void OnClosing()
        //{
        //    // Custom closing logic for RoomsSelectionViewModel
        //    //_eventManager.DisposeEvents();

        //    //unbsubscribe from underlying model changes
        //    RevitDataModel.PropertyChanged -= Model_PropertyChanged;

            
        //    base.OnClosing();
        //}

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
        /// Set up the default columns that should be visible when the grid loads
        /// </summary>
        private void SetupDefaultColumns()
        {
            //there are only 2 columns to display and they are always visible
            foreach (KeyValuePair<string, string> columnName in Models.Constants.ColumnRoomsInfo)
            {
                AddSelectedColumn(columnName.Key);
            }
        }

        
        #endregion

        public RoomsDataGridViewModel(Models.RevitDataModel revitDataModel)
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
