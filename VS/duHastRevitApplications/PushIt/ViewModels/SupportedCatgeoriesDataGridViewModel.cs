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
    public class SupportedCatgeoriesDataGridViewModel : duHastNet.Utils.WPF.ViewModels.BaseDynamicGridViewModel<DynamicRowData>
    {

        private Models.RevitDataModel RevitDataModel { get; set; }


        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        private Dictionary<string, Func<SupportedCatgeoriesDataGridViewModel, object>> _columnDefaults;

        /// <summary>
        /// Dictionary containing custom default values for specific columns
        /// </summary>
        public Dictionary<string, Func<SupportedCatgeoriesDataGridViewModel, object>> ColumnDefaults
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

            //initialise available columns with default category properties
            AvailableColumns = [ 
            
                // Basic revit category Info
                new(Models.Constants.ColumnHeaderCategoriesIsEnabled.Replace(" ", "") , Models.Constants.ColumnHeaderCategoriesIsEnabled, typeof(bool)),
                new(Models.Constants.ColumnHeaderCategoriesCategoryName.Replace(" ", "") , Models.Constants.ColumnHeaderCategoriesCategoryName, typeof(string))

            ];

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

            if (RevitDataModel?.GetAllCategories() == null || RevitDataModel?.GetAllCategories().Count == 0) return;

            foreach (var availableCategory in RevitDataModel.GetAllCategories())
            {
                try
                {
                    var rowData = CreateRowFromCategory(availableCategory);
                    Data.Add(rowData);
                }
                catch (Exception ex)
                {
                    // Log or handle individual category errors
                    System.Diagnostics.Debug.WriteLine($"Error loading category: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Convert a category object to a ViewDataViewModel for the grid
        /// </summary>
        private DynamicRowData CreateRowFromCategory(Models.CategoryDataModel availableCategory)
        {
            var rowData = new DynamicRowData();

            // Set the standard column values
            rowData[Models.Constants.ColumnHeaderCategoriesIsEnabled.Replace(" ", "")] = availableCategory.Enabled;
            rowData[Models.Constants.ColumnHeaderCategoriesCategoryName.Replace(" ", "")] = availableCategory.Name ?? "";

            return rowData;
        }

        #region Private Helper Methods

        private void InitializeColumnDefaults()
        {
            //initialise with default category properties and default values
            _columnDefaults = new Dictionary<string, Func<SupportedCatgeoriesDataGridViewModel, object>>
            {
                {Models.Constants.ColumnHeaderCategoriesIsEnabled.Replace(" ", ""), vm => false },
                { Models.Constants.ColumnHeaderCategoriesCategoryName.Replace(" ", ""), vm =>  "Revit Category Name"},
            };
        }


        /// <summary>
        /// Override to restore actual revit category data instead of defaults when adding columns ( should not be required. column management is disabled)
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
                // For new columns, populate with actual category data instead of defaults
                RestoreActualRevitCategoryData(propertyName);
            }
        }


        /// <summary>
        /// Populate column with actual data from categories instead of defaults
        /// </summary>
        private void RestoreActualRevitCategoryData(string propertyName)
        {
            var supportedCategories = RevitDataModel.GetAllCategories();

            // For all rows, set the actual data from the corresponding category
            for (int i = 0; i < Data.Count && i < supportedCategories.Count; i++)
            {
                var category = supportedCategories[i];
                var rowData = Data[i];

                // Set the value based on the property name
                if (propertyName == Models.Constants.ColumnHeaderCategoriesIsEnabled.Replace(" ", ""))
                {
                    rowData[propertyName] = category.Enabled;
                }
                else
                {
                    rowData[propertyName] = category.Name ?? "";
                }
            }
        }

        /// <summary>
        /// Get default value for a specific column in the catgeories context
        /// </summary>
        protected override object GetDefaultValueForColumn(AvailableColumnDefinition columnDef)
        {

            // Check if we have a custom default for this column
            if (ColumnDefaults.TryGetValue(columnDef.PropertyName, out Func<SupportedCatgeoriesDataGridViewModel, object> defaultValueFunc))
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
            foreach (KeyValuePair<string, string> columnName in Models.Constants.ColumnCategoriesInfo)
            {
                AddSelectedColumn(columnName.Key);
            }
        }


        /// <summary>
        /// Define which columns should be read-only by default ( just the is enabledcheck box column!!!   )
        /// </summary>
        protected override bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            if (propertyName == Models.Constants.ColumnHeaderCategoriesIsEnabled.Replace(" ", ""))
            {
                return false; // This should be the only column editable
            }
            else
            {
                return true; // Everything else is not editable
            }
        }

        /// <summary>
        /// Custom column widths for better display
        /// </summary>
        protected override double GetDefaultWidthForType(Type dataType)
        {
            // override this to provide custom widths
            // or just use the base implementation
            return base.GetDefaultWidthForType(dataType);
        }

        /// <summary>
        /// Synchronizes changes from the grid data back to the underlying RevitDataModel
        /// Call this method after bulk operations or when you need to ensure data consistency
        /// </summary>
        public void SyncGridDataToUnderlyingModel()
        {

            if (RevitDataModel?.GetAllCategories() == null || RevitDataModel?.GetAllCategories().Count == 0 || Data == null) return;

            var supportedCategories = RevitDataModel.GetAllCategories();
            var enabledColumnId = Models.Constants.ColumnHeaderCategoriesIsEnabled.Replace(" ", "");

            for (int i = 0; i < Data.Count && i < supportedCategories.Count; i++)
            {
                var gridRow = Data[i];
                var supportedCategory = supportedCategories[i];

                // Sync the export/selection status
                if (gridRow.Values.TryGetValue(enabledColumnId, out object gridValue))
                {
                    if (gridValue is bool isSelected)
                    {
                        supportedCategory.Enabled = isSelected;
                    }
                }
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
                if (index >= 0 && index < RevitDataModel.GetAllCategories().Count)
                {
                    var supportedCategory = RevitDataModel.GetAllCategories()[index];

                    // Sync specific properties
                    var enabledColumnId = Models.Constants.ColumnHeaderCategoriesIsEnabled.Replace(" ", "");
                    if (e.PropertyName == enabledColumnId || e.PropertyName == "Values")
                    {
                        if (row.Values.TryGetValue(enabledColumnId, out object value) && value is bool isSelected)
                        {
                            supportedCategory.Enabled = isSelected;
                        }
                    }
                }
            }
        }

        #endregion

        public SupportedCatgeoriesDataGridViewModel(Models.RevitDataModel revitDataModel)
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
