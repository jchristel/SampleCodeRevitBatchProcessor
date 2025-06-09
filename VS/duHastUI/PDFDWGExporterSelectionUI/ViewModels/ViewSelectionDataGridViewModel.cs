using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.PDFDWGExporterSelectionUI.Models;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public class ViewSelectionDataGridViewModel : BaseDynamicGridViewModel<DynamicRowData>
    {

        //field storing the sheets data model
        private Models.SheetsDataModel SheetsDataModel { get; set; }

        /// <summary>
        /// Dictionary containing custom default values for specific product columns
        /// </summary>
        private Dictionary<string, Func<ViewSelectionDataGridViewModel, object>> _columnDefaults;

        /// <summary>
        /// Dictionary containing custom default values for specific product columns
        /// </summary>
        public Dictionary<string, Func<ViewSelectionDataGridViewModel, object>> ColumnDefaults
        {
            get => _columnDefaults;
        }


        private Dictionary<string, string> _columnIdToParameterNameLookUp;
        public Dictionary<string, string> ColumnIdToParameterNameLookUp
        {
            get => _columnIdToParameterNameLookUp;
        }

        public ViewSelectionDataGridViewModel(duHastNet.UI.PDFDWGExporterSelectionUI.Models.SheetsDataModel sheetDataModel)
        {
            // Base constructor will call InitializeAvailableColumns()
            // and set up all the commands

            this.SheetsDataModel = sheetDataModel;

            // NOW manually call this since it was skipped during base constructor
            InitializeAvailableColumns();

            // Initialize column defaults first
            InitializeColumnDefaults();

            // Populate the grid with data from the sheets model
            LoadDataFromSheetsModel();
        }

        /// <summary>
        /// Define what columns are available for the views grid
        /// </summary>
        protected override void InitializeAvailableColumns()
        {

            // Don't do anything if called from base constructor
            if (this.SheetsDataModel == null) return;

            //initialise available columns with default sheet properties
            AvailableColumns = new ObservableCollection<AvailableColumnDefinition> { 
            
                // Basic sheet Info
                new AvailableColumnDefinition(Constants.ColumnHeaderExport.Replace(" ", ""), Constants.ColumnHeaderExport, typeof(bool)),
                new AvailableColumnDefinition(Constants.ColumnHeaderPDFPreviewName.Replace(" ", ""), Constants.ColumnHeaderPDFPreviewName, typeof(string)),
                new AvailableColumnDefinition(Constants.ColumnHeaderDWGPreviewName.Replace(" ", ""), Constants.ColumnHeaderDWGPreviewName, typeof(string)),
                new AvailableColumnDefinition(Constants.ColumnHeaderSheetNumber.Replace(" ", ""), Constants.ColumnHeaderSheetNumber, typeof(string)),
                new AvailableColumnDefinition(Constants.ColumnHeaderSheetName.Replace(" ", ""), Constants.ColumnHeaderSheetName, typeof(string)),

            };

            //add any other custom properties
            var sampleSheet = SheetsDataModel.RevitSheets.First();

            foreach (var sheetProperty in sampleSheet.Properties)
            {
                AvailableColumns.Add(
                    new AvailableColumnDefinition(sheetProperty.Name.Replace(" ", ""), sheetProperty.Name, typeof(string), "Properties")
                    );
            }

            // Pre-compute the parameter name to column id lookup dictionary
            _columnIdToParameterNameLookUp = SheetsDataModel.ParameterNames.ToDictionary(name => name.Replace(" ", ""), name => name);

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
        private void LoadDataFromSheetsModel()
        {
            Data.Clear();

            if (SheetsDataModel?.RevitSheets == null) return;

            foreach (var sheet in SheetsDataModel.RevitSheets)
            {
                try
                {
                    var rowData = CreateRowFromSheet(sheet);
                    Data.Add(rowData);
                }
                catch (Exception ex)
                {
                    // Log or handle individual sheet errors
                    System.Diagnostics.Debug.WriteLine($"Error loading sheet: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Convert a sheet object to a ViewDataViewModel for the grid
        /// </summary>
        private DynamicRowData CreateRowFromSheet(Models.RevitSheet sheet)
        {
            var rowData = new DynamicRowData();

            // Set the standard column values
            rowData[Constants.ColumnHeaderExport.Replace(" ", "")] = sheet.IsSelected; // Default to not exported
            rowData[Constants.ColumnHeaderPDFPreviewName.Replace(" ", "")] = sheet.PDFPreviewName ?? "";
            rowData[Constants.ColumnHeaderDWGPreviewName.Replace(" ", "")] = sheet.DWGPreviewName ?? "";
            rowData[Constants.ColumnHeaderSheetNumber.Replace(" ", "")] = sheet.SheetNumber.Value ?? "";
            rowData[Constants.ColumnHeaderSheetName.Replace(" ", "")] = sheet.SheetName.Value ?? "";

            // Set the custom properties from the sheet
            foreach (var property in sheet.Properties)
            {
                var columnId = property.Name.Replace(" ", "");
                rowData[columnId] = property.Value ?? "";
            }

            return rowData;
        }

        /// <summary>
        /// Refresh the grid data from the sheets model (call this if the underlying data changes)
        /// </summary>
        public void RefreshData()
        {
            LoadDataFromSheetsModel();
        }

        /// <summary>
        /// method updating sheet selection check box depending on print set
        /// </summary>
        /// <param name="printSetName"></param>
        public void UpdateSheetSelectionByPrintSet(string printSetName)
        {
            if (string.IsNullOrEmpty(printSetName) || Data == null) return;

            var exportColumnId = Constants.ColumnHeaderExport.Replace(" ", "");

            // Check if <None> was selected
            if (printSetName == Models.Constants.DefaultPrintSetName)
            {
                // Set all sheets to not selected in BOTH the grid and underlying data
                for (int i = 0; i < Data.Count && i < SheetsDataModel.RevitSheets.Count; i++)
                {
                    // Update grid
                    Data[i][exportColumnId] = false;

                    // Update underlying sheet data (if your sheet has an IsSelected property)
                    SheetsDataModel.RevitSheets[i].IsSelected = false; // Adjust property name as needed
                }
            }
            else
            {
                // Get the print set by name
                var printSet = SheetsDataModel.PrintSets.Find(x => x.Name == printSetName);

                if (printSet != null)
                {
                    // Check if sheet is in set
                    for (int i = 0; i < Data.Count && i < SheetsDataModel.RevitSheets.Count; i++)
                    {
                        var sheet = SheetsDataModel.RevitSheets[i];
                        bool shouldBeSelected = printSet.RevitSheets.Contains(sheet);

                        // Update both grid and underlying data
                        Data[i][exportColumnId] = shouldBeSelected;
                        sheet.IsSelected = shouldBeSelected; // Adjust property name as needed
                    }
                }
            }
            
            RefreshData();
        }

        #region Private Helper Methods


        private void InitializeColumnDefaults()
        {
            //initialise with default sheet properties and default values
            _columnDefaults = new Dictionary<string, Func<ViewSelectionDataGridViewModel, object>>
            {
                { Constants.ColumnHeaderExport.Replace(" ", ""), vm => false },
                { Constants.ColumnHeaderPDFPreviewName.Replace(" ", ""), vm =>  ""},
                { Constants.ColumnHeaderDWGPreviewName.Replace(" ", ""), vm => "" },
                { Constants.ColumnHeaderSheetNumber.Replace(" ", ""), vm => Constants.ColumnHeaderSheetNumber },
                { Constants.ColumnHeaderSheetName.Replace(" ", ""), vm => Constants.ColumnHeaderSheetName },
            };

            //add any other custom properties
            var sampleSheet = SheetsDataModel.RevitSheets.First();
            for (int i = 0; i < sampleSheet.Properties.Count; i++)
            {
                var item = sampleSheet.Properties[i];
                _columnDefaults[item.Name.Replace(" ", "")] = vm => item.Value;
            }
        }

        /// <summary>
        /// Get default value for a specific column in the sheets context
        /// </summary>
        protected override object GetDefaultValueForColumn(AvailableColumnDefinition columnDef)
        {

            // Check if we have a custom default for this column
            if (ColumnDefaults.TryGetValue(columnDef.PropertyName, out Func<ViewSelectionDataGridViewModel, object> defaultValueFunc))
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
            if (SheetsDataModel.Settings.ColumnIds != null &&
                SheetsDataModel.Settings.ColumnIds.Count > 0)
            {
                foreach (string columnId in SheetsDataModel.Settings.ColumnIds)
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

                ////use the extra parameter, if any, from the rename pdf settings
                //foreach (var settings in SheetsDataModel.PDFSettings)
                //{

                //    defaultColumns.Add(settings.PropertyName);

                //}
                ////use the extra parameter, if any, from the rename dwg settings
                //foreach (var setting in SheetsDataModel.DWGSettings)
                //{
                //    // make sure not to double up property names
                //    if (!defaultColumns.Contains(setting.PropertyName))
                //    {
                //        defaultColumns.Add(setting.PropertyName);
                //    }
                //}
            }

            foreach (var columnName in defaultColumns)
            {
                AddSelectedColumn(columnName);
            }
        }

        /// <summary>
        /// Define which columns should be read-only by default ( just the expor5t check box column!!! )
        /// </summary>
        protected override bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            if (propertyName == Constants.ColumnHeaderExport.Replace(" ", ""))
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

        #endregion
    }
}
