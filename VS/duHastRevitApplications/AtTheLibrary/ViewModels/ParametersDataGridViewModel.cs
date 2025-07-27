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

using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public class ParametersDataGridViewModel : BaseDynamicGridViewModel<DynamicRowData>
    {
        private Models.RevitFamiliesDataModel RevitDataModel { get; set; }


        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        private Dictionary<string, Func<ParametersDataGridViewModel, object>> _columnDefaults;

        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        public Dictionary<string, Func<ParametersDataGridViewModel, object>> ColumnDefaults
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

        #region selected parameter

        protected override void OnSelectionChanged()
        {
            base.OnSelectionChanged();
        }

        //field to store the selected room from the revit data model
        private Models.FamilyDataModel _selectedParameter;

        //property to get the selected room from the revit data model
        public Models.FamilyDataModel SelectedParameter
        {
            set
            {
                _selectedParameter = value;
                OnPropertyChanged(nameof(SelectedParameter));
            }

            get => _selectedParameter;
        }

        #endregion selected parameter

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
            AvailableColumns = new ObservableCollection<AvailableColumnDefinition> { 
            
                // Basic revit category Info
                new AvailableColumnDefinition(Models.Constants.ColumnHeaderParameterIsSelected.Replace(" ", "") , Models.Constants.ColumnHeaderParameterIsSelected, typeof(bool)),
                new AvailableColumnDefinition(Models.Constants.ColumnHeaderParameterName.Replace(" ", "") , Models.Constants.ColumnHeaderParameterName, typeof(string)),
                new AvailableColumnDefinition(Models.Constants.ColumnHeaderParameterOccurenceCount.Replace(" ",""), Models.Constants.ColumnHeaderParameterOccurenceCount, typeof(int)),

            };

            // Pre-compute the parameter name to column id lookup dictionary
            _columnIdToParameterNameLookUp = RevitDataModel.GetAllParameterProperties().ToDictionary(parameter => parameter.Name.Replace(" ", ""), name => name.Name);

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

            if (RevitDataModel?.GetAllParameterProperties() == null || RevitDataModel?.GetAllParameterProperties().Count == 0) return;

            foreach (var parameterEntry in RevitDataModel.GetAllParameterProperties())
            {
                try
                {
                    var rowData = CreateRowFromFamily(parameterEntry);
                    Data.Add(rowData);
                }
                catch (Exception ex)
                {
                    // Log or handle individual category errors
                    System.Diagnostics.Debug.WriteLine($"Error loading parameter data: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Convert a room data object to a dynamic row for the grid
        /// </summary>
        private DynamicRowData CreateRowFromFamily(Models.ParameterDataProperty parameterEntry)
        {
            var rowData = new DynamicRowData();

            // Set the standard column values
            rowData[Models.Constants.ColumnHeaderParameterIsSelected.Replace(" ", "")] = parameterEntry.EnabledInUI;
            rowData[Models.Constants.ColumnHeaderParameterName.Replace(" ", "")] = parameterEntry.Name;
            rowData[Models.Constants.ColumnHeaderParameterOccurenceCount.Replace(" ", "")] = parameterEntry.OccurenceCount;

            return rowData;
        }

        #endregion data loading

        #region event handlers

        /// <summary>
        /// Custom closing logic for ParameterSelectionViewModel
        /// Disposes all external events from the event manager
        /// </summary>
        public override void OnClosing()
        { 
            base.OnClosing();
        }

        #endregion event handlers

        #region Private Helper Methods
        private void InitializeColumnDefaults()
        {
            //initialise with default category properties and default values
            _columnDefaults = new Dictionary<string, Func<ParametersDataGridViewModel, object>>
            {
                {Models.Constants.ColumnHeaderParameterIsSelected.Replace(" ", ""), vm => false },
                {Models.Constants.ColumnHeaderParameterName.Replace(" ", ""), vm =>  ""},
                {Models.Constants.ColumnHeaderParameterOccurenceCount.Replace(" ",""), vm => 0},
            };
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
                RestoreActualFamilyData(propertyName, availableColumn);
            }
        }


        /// <summary>
        /// Populate column with actual data from rooms instead of defaults
        /// </summary>
        private void RestoreActualFamilyData(string propertyName, AvailableColumnDefinition availableColumn)
        {
            var parameters = RevitDataModel.GetAllParameterProperties();
            // For all rows, set the actual data from the corresponding room
            for (int i = 0; i < Data.Count && i < parameters.Count; i++)
            {
                var parameter = parameters[i];
                var rowData = Data[i];

                // Set the value based on the property name
                if (propertyName == Models.Constants.ColumnHeaderParameterIsSelected.Replace(" ", ""))
                {
                    rowData[propertyName] = parameter.EnabledInUI;
                }
                else if (propertyName == Models.Constants.ColumnHeaderParameterName.Replace(" ", ""))
                {
                    rowData[propertyName] = parameter.Name;
                }
                else if (propertyName == Models.Constants.ColumnHeaderParameterOccurenceCount.Replace(" ", ""))
                {
                    rowData[propertyName] = parameter.OccurenceCount;
                }
            }
        }


        /// <summary>
        /// Get default value for a specific column in the catgeories context
        /// </summary>
        protected override object GetDefaultValueForColumn(AvailableColumnDefinition columnDef)
        {

            // Check if we have a custom default for this column
            if (ColumnDefaults.TryGetValue(columnDef.PropertyName, out Func<ParametersDataGridViewModel, object> defaultValueFunc))
            {
                return defaultValueFunc(this);
            }

            // Fall back to base implementation for standard types
            return GetDefaultValue(columnDef.DataType);
        }


        /// <summary>
        /// Define which columns should be read-only by default (para is selected is only editable column )
        /// </summary>
        protected override bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            if (propertyName == Models.Constants.ColumnHeaderParameterIsSelected.Replace(" ", ""))
            {
                return false; // This should be the only column editable
            }
            else
            {
                return true; // Everything else is not editable
            }
        }

        /// <summary>
        /// Set up the default columns that should be visible when the grid loads
        /// </summary>
        private void SetupDefaultColumns()
        {
            var defaultColumns = new List<string>();

            //add all column names
            foreach (KeyValuePair<string, string> entry in Models.Constants.ColumnParametersInfo)
            {
                defaultColumns.Add(entry.Key);
            }

            foreach (var columnName in defaultColumns)
            {
                AddSelectedColumn(columnName);
            }
        }


        public string FindColumnNameById(string id)
        {
            return _columnIdToParameterNameLookUp.TryGetValue(id, out string displayName) ? displayName : null;
        }


        /// <summary>
        /// Synchronizes changes from the grid data back to the underlying SheetsDataModel
        /// Call this method after bulk operations or when you need to ensure data consistency
        /// </summary>
        public void SyncGridDataToUnderlyingModel()
        {
            if (RevitDataModel?.GetAllParameterProperties() == null || Data == null) return;

            var parameterDataProperties = RevitDataModel.GetAllParameterProperties();

            var enabledColumnId = Models.Constants.ColumnHeaderParameterIsSelected.Replace(" ", "");

            for (int i = 0; i < Data.Count && i < parameterDataProperties.Count; i++)
            {
                var gridRow = Data[i];
                var parameter = parameterDataProperties[i];

                // Sync the export/selection status
                if (gridRow.Values.ContainsKey(enabledColumnId))
                {
                    var gridValue = gridRow.Values[enabledColumnId];
                    if (gridValue is bool isSelected)
                    {
                        parameter.EnabledInUI = isSelected;
                    }
                }

                // Sync other editable properties if needed
                // Add more sync logic here for other properties that can be edited
            }
        }


        /// <summary>
        /// Sets up a property changed event handler to automatically sync data
        /// Call this from constructor after initializing the data
        /// </summary>
        private void SetupDataSynchronization()
        {
            // Monitor changes to the Data collection
            if (Data != null)
            {
                foreach (var row in Data)
                {
                    if (row is INotifyPropertyChanged notifyRow)
                    {
                        notifyRow.PropertyChanged += OnGridRowPropertyChanged;
                    }
                }

                // Also monitor when new rows are added
                Data.CollectionChanged += (s, e) =>
                {
                    if (e.NewItems != null)
                    {
                        foreach (var newItem in e.NewItems.OfType<INotifyPropertyChanged>())
                        {
                            newItem.PropertyChanged += OnGridRowPropertyChanged;
                        }
                    }

                    if (e.OldItems != null)
                    {
                        foreach (var oldItem in e.OldItems.OfType<INotifyPropertyChanged>())
                        {
                            oldItem.PropertyChanged -= OnGridRowPropertyChanged;
                        }
                    }
                };
            }
        }

        /// <summary>
        /// Handles property changes in grid rows and syncs to underlying model
        /// </summary>
        private void OnGridRowPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            if (sender is DynamicRowData row && e.PropertyName != null)
            {
                // Find the index of this row
                var index = Data.IndexOf(row);
                if (index >= 0 && index < RevitDataModel.GetAllParameterProperties().Count)
                {
                    var parameterDataProperty = RevitDataModel.GetAllParameterProperties()[index];

                    // Sync specific properties
                    var exportColumnId = Models.Constants.ColumnHeaderParameterIsSelected.Replace(" ", "");
                    if (e.PropertyName == exportColumnId || e.PropertyName == "Values")
                    {
                        if (row.Values.ContainsKey(exportColumnId) && row.Values[exportColumnId] is bool isSelected)
                        {
                            parameterDataProperty.EnabledInUI = isSelected;
                        }
                    }

                    // Add other property syncing as needed
                }
            }
        }

        #endregion event handlers


        public ParametersDataGridViewModel(Models.RevitFamiliesDataModel revitDataModel)
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

            // Set up automatic data synchronization
            SetupDataSynchronization();
        }
    }
}
