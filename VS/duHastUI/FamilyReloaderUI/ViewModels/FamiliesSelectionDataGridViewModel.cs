using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.FamilyReloaderUI.Models;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;

namespace duHastNet.UI.FamilyReloaderUI.ViewModels
{
    public class FamiliesSelectionDataGridViewModel : BaseDynamicGridViewModel<DynamicRowData>
    {

        //field storing the families data model
        private Models.FamiliesDataModel FamiliesDataModel { get; set; }

        /// <summary>
        /// Dictionary containing custom default values for specific product columns
        /// </summary>
        private Dictionary<string, Func<FamiliesSelectionDataGridViewModel, object>> _columnDefaults;

        /// <summary>
        /// Dictionary containing custom default values for specific product columns
        /// </summary>
        public Dictionary<string, Func<FamiliesSelectionDataGridViewModel, object>> ColumnDefaults
        {
            get => _columnDefaults;
        }

        private Dictionary<string, string> _columnIdToParameterNameLookUp;
        public Dictionary<string, string> ColumnIdToParameterNameLookUp
        {
            get => _columnIdToParameterNameLookUp;
        }

        public FamiliesSelectionDataGridViewModel(duHastNet.UI.FamilyReloaderUI.Models.FamiliesDataModel familiesDataModel)
        {
            // Base constructor will call InitializeAvailableColumns()
            // and set up all the commands

            this.FamiliesDataModel = familiesDataModel;

            // manually call this since it was skipped during base constructor
            InitializeAvailableColumns();

            // Initialize column defaults first
            InitializeColumnDefaults();

            // Populate the grid with data from the sheets model
            LoadDataFromFamiliesModel();

            // Set up automatic data synchronization
            SetupDataSynchronization();
        }

        /// <summary>
        /// Define what columns are available for the views grid
        /// </summary>
        protected override void InitializeAvailableColumns()
        {

            // Don't do anything if called from base constructor
            if (this.FamiliesDataModel == null) return;

            //initialise available columns with default sheet properties
            AvailableColumns = new ObservableCollection<AvailableColumnDefinition> { 
            
                // Basic sheet Info
                new AvailableColumnDefinition(Constants.ColumnHeaderReload.Replace(" ", ""), Constants.ColumnHeaderReload, typeof(bool)),
                new AvailableColumnDefinition(Constants.ColumnHeaderFamilyName.Replace(" ", ""), Constants.ColumnHeaderFamilyName, typeof(string)),
                new AvailableColumnDefinition(Constants.ColumnHeaderFamilyCategory.Replace(" ", ""), Constants.ColumnHeaderFamilyCategory, typeof(string)),
                new AvailableColumnDefinition(Constants.ColumnHeaderIsSharedFamily.Replace(" ", ""), Constants.ColumnHeaderIsSharedFamily, typeof(bool)),
            };

            // Pre-compute the parameter name to column id lookup dictionary
            _columnIdToParameterNameLookUp = Constants.ColumnInfo;

            // Set up initial columns that should be visible by default
            SetupDefaultColumns();
        }

        /// <summary>
        /// Create a new product row with default data
        /// </summary>
        protected override DynamicRowData CreateNewRow()
        {
            return new DynamicRowData
            {
                // You can pre-populate some default values here if needed
                // The base class will fill in defaults for all columns
            };
        }


        /// <summary>
        /// Load data from the SheetsDataModel into the grid
        /// </summary>
        private void LoadDataFromFamiliesModel()
        {
            Data.Clear();

            if (FamiliesDataModel?.RevitFamilies == null) return;

            foreach (var family in FamiliesDataModel.RevitFamilies)
            {
                try
                {
                    var rowData = CreateRowFromSheet(family);
                    Data.Add(rowData);
                }
                catch (Exception ex)
                {
                    // Log or handle individual sheet errors
                    System.Diagnostics.Debug.WriteLine($"Error loading family: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Convert a sheet object to a ViewDataViewModel for the grid
        /// </summary>
        private DynamicRowData CreateRowFromSheet(Models.RevitFamily family)
        {
            var rowData = new DynamicRowData();

            // Set the standard column values
            rowData[Constants.ColumnHeaderReload.Replace(" ", "")] = family.IsSelected; // Default to not exported
            rowData[Constants.ColumnHeaderFamilyName.Replace(" ", "")] = family.FamilyName ?? "";
            rowData[Constants.ColumnHeaderFamilyCategory.Replace(" ", "")] = family.FamilyCategory ?? "";
            rowData[Constants.ColumnHeaderIsSharedFamily.Replace(" ", "")] = family.IsShared;

            return rowData;
        }

        /// <summary>
        /// Refresh the grid data from the sheets model (call this if the underlying data changes)
        /// </summary>
        public void RefreshData()
        {
            LoadDataFromFamiliesModel();
        }

        #region Private Helper Methods

        private void InitializeColumnDefaults()
        {
            //initialise with default sheet properties and default values
            _columnDefaults = new Dictionary<string, Func<FamiliesSelectionDataGridViewModel, object>>
            {
                { Constants.ColumnHeaderReload.Replace(" ", ""), vm => false },
                { Constants.ColumnHeaderFamilyName.Replace(" ", ""), vm =>  ""},
                { Constants.ColumnHeaderFamilyCategory.Replace(" ", ""), vm => "" },
                { Constants.ColumnHeaderIsSharedFamily.Replace(" ", ""), vm => false },
            };
        }

        /// <summary>
        /// Override to restore actual sheet data instead of defaults when adding columns
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
                // For new columns, populate with actual sheet data instead of defaults
                RestoreActualFamilyData(propertyName, availableColumn);
            }
        }

        /// <summary>
        /// Populate column with actual data from families instead of defaults
        /// </summary>
        private void RestoreActualFamilyData(string propertyName, AvailableColumnDefinition availableColumn)
        {
            // For all rows, set the actual data from the corresponding sheet
            for (int i = 0; i < Data.Count && i < FamiliesDataModel.RevitFamilies.Count; i++)
            {
                var family = FamiliesDataModel.RevitFamilies[i];
                var rowData = Data[i];

                // Set the value based on the property name
                if (propertyName == Constants.ColumnHeaderReload.Replace(" ", ""))
                {
                    rowData[propertyName] = family.IsSelected;
                }
                else if (propertyName == Constants.ColumnHeaderFamilyName.Replace(" ", ""))
                {
                    rowData[propertyName] = family.FamilyName ?? "";
                }
                else if (propertyName == Constants.ColumnHeaderFamilyCategory.Replace(" ", ""))
                {
                    rowData[propertyName] = family.FamilyCategory ?? "";
                }
                else if (propertyName == Constants.ColumnHeaderIsSharedFamily.Replace(" ", ""))
                {
                    rowData[propertyName] = family.IsShared;
                }
            }
        }

        /// <summary>
        /// Get default value for a specific column in the sheets context
        /// </summary>
        protected override object GetDefaultValueForColumn(AvailableColumnDefinition columnDef)
        {

            // Check if we have a custom default for this column
            if (ColumnDefaults.TryGetValue(columnDef.PropertyName, out Func<FamiliesSelectionDataGridViewModel, object> defaultValueFunc))
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

            var defaultColumns = new List<string>();

            //check if any column id ( property name without space) is mentioned in the settings object
            //if there are columns stored in settings retrieved from file
            if (FamiliesDataModel.Settings.ColumnIds != null &&
                FamiliesDataModel.Settings.ColumnIds.Count > 0)
            {
                foreach (string columnId in FamiliesDataModel.Settings.ColumnIds)
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
                        var columnNameDefault = Constants.ColumnInfo.TryGetValue(columnId, out string displayName) ? displayName : null;
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
                foreach (KeyValuePair<string, string> entry in Constants.ColumnInfo)
                {
                    defaultColumns.Add(entry.Key);
                }
            }

            foreach (var columnName in defaultColumns)
            {
                AddSelectedColumn(columnName);
            }
        }

        /// <summary>
        /// Define which columns should be read-only by default ( just the export check box column!!! )
        /// </summary>
        protected override bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            if (propertyName == Constants.ColumnHeaderReload.Replace(" ", ""))
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
            // You can override this to provide custom widths
            // or just use the base implementation
            return base.GetDefaultWidthForType(dataType);
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
            if (FamiliesDataModel?.RevitFamilies == null || Data == null) return;

            var exportColumnId = Constants.ColumnHeaderReload.Replace(" ", "");

            for (int i = 0; i < Data.Count && i < FamiliesDataModel.RevitFamilies.Count; i++)
            {
                var gridRow = Data[i];
                var family = FamiliesDataModel.RevitFamilies[i];

                // Sync the export/selection status
                if (gridRow.Values.ContainsKey(exportColumnId))
                {
                    var gridValue = gridRow.Values[exportColumnId];
                    if (gridValue is bool isSelected)
                    {
                        family.IsSelected = isSelected;
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
                if (index >= 0 && index < FamiliesDataModel.RevitFamilies.Count)
                {
                    var sheet = FamiliesDataModel.RevitFamilies[index];

                    // Sync specific properties
                    var exportColumnId = Constants.ColumnHeaderReload.Replace(" ", "");
                    if (e.PropertyName == exportColumnId || e.PropertyName == "Values")
                    {
                        if (row.Values.ContainsKey(exportColumnId) && row.Values[exportColumnId] is bool isSelected)
                        {
                            sheet.IsSelected = isSelected;
                        }
                    }

                    // Add other property syncing as needed
                }
            }
        }
        #endregion
    }
}
