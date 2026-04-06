

//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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


using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.UI.DocManagerSettingsUI.Models;
using duHastNet.Utils.WPF.Stores;
using System.Collections.ObjectModel;
using System.Data;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.DocManagerSettingsUI.ViewModels
{
    public partial class SettingsViewModel : AppViewModelBase
    {
        /// <summary>
        /// Global message view model for displaying messages to the user
        /// </summary>
        public duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// message store for storing messages
        /// </summary>
        private readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;

        /// <summary>
        /// The data model for the export settings
        /// </summary>
        private readonly Models.ExportDataModel _exportDataModel;

        /// <summary>
        /// Settings build in UI and to be returned to caller
        /// </summary>
        public Utils.Settings Settings
        {
            get { return _exportDataModel.Settings; }
        }

        /// <summary>
        /// data table containing the available parameters
        /// </summary>
        private DataTable _dtAvailableParameters;

        /// <summary>
        /// Data table containing document settings
        /// </summary>
        private DataTable _documentSettingsTable;

        /// <summary>
        /// Observable collection containing the document naming settings
        /// </summary>
        private ObservableCollection<Utils.DocumentSetting> _documentSettings;

        /// <summary>
        /// contains the file path for the database file
        /// </summary>
        [ObservableProperty]
        private string _databaseFilePath;

        #region column names

        /// <summary>
        /// single column name for available property table
        /// </summary>
        private string _columnNameAvailableProperties = "Sheet properties";

        /// <summary>
        /// column names for document naming table
        /// </summary>
        private readonly string _columnNameRulePrefix = "Prefix";
        private readonly string _columnNameRuleSuffix = "Suffix";
        private readonly string _columnNameRuleParameter = "Sheet property";
        private readonly string _columnNameRuleSeparator = "Separator";

        #endregion column names

        #region user selection

        /// <summary>
        /// binding to show selected index of available parameters
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(SelectedParameter))]
        private int _selectedIndexAvailableParameters;

        /// <summary>
        /// property to get the selected parameter from the UI
        /// </summary>
        public string SelectedParameter
        {
            get
            {
                // check if a default view exists
                if (_dvAvailableParameters == null)
                {
                    return null;
                }
                // check if the selected index is within the bounds of the collection
                if (_selectedIndexAvailableParameters >= 0 && _selectedIndexAvailableParameters < _dvAvailableParameters.Count)
                {
                    var selectedRow = _dvAvailableParameters[_selectedIndexAvailableParameters].Row;
                    var parameterName = selectedRow[_columnNameAvailableProperties].ToString();
                    return parameterName;
                }
                // return null if the selected index is out of bounds
                return null;
            }
        }

        /// <summary>
        /// binding to show selected index of document name settings
        /// </summary>
        [ObservableProperty]
        private int _selectedIndexDocumentNameSetting;

        partial void OnSelectedIndexDocumentNameSettingChanged(int value)
        {
            if (_selectedIndexDocumentNameSetting >= 0 && _selectedIndexDocumentNameSetting <= _documentSettings.Count)
            {
                //change the selected item as well... that will trigger the command can execute state updates for move up and down buttons
                SelectedItemDocumentNameSetting = _documentSettings[_selectedIndexDocumentNameSetting];
            }
            else if (_selectedIndexDocumentNameSetting == -1)
            {
                //reset the selected item in the naming table
                SelectedItemDocumentNameSetting = null;
            }
        }

        /// <summary>
        /// The selected document name setting
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(MoveUpCommand))]
        [NotifyCanExecuteChangedFor(nameof(MoveDownCommand))]
        private Utils.DocumentSetting _selectedItemDocumentNameSetting;

        partial void OnSelectedItemDocumentNameSettingChanging(Utils.DocumentSetting value)
        {
            //sync data table with the document settings before change
            SynchronizeDocumentNameTable();
        }

        #endregion user selection

        #region data views

        /// <summary>
        /// default view of the data table
        /// </summary>
        [ObservableProperty]
        private DataView _dvAvailableParameters;

        /// <summary>
        /// default view of the data table containing document settings
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(MoveParameterToDocumentNameTableCommand))]
        [NotifyCanExecuteChangedFor(nameof(RemoveParameterFromDocumentNameTableCommand))]
        [NotifyCanExecuteChangedFor(nameof(MoveUpCommand))]
        [NotifyCanExecuteChangedFor(nameof(MoveDownCommand))]
        private DataView _dvDocumentSettings;

        partial void OnDvDocumentSettingsChanged(DataView value)
        {
            //clear selection when changing view
            if (SelectedIndexDocumentNameSetting != -1 || SelectedItemDocumentNameSetting != null)
            {
                ClearSelection();
            }
        }

        #endregion data views

        #region import/export file paths

        /// <summary>
        /// The file path for the export settings file
        /// </summary>
        [ObservableProperty]
        private string _exportSettingsFilePath;

        partial void OnExportSettingsFilePathChanged(string value)
        {
            if (!string.IsNullOrEmpty(value))
            {
                //export settings to given file path
                Utils.SettingsExport.ExportSettingsToJson(
                    filePath: value,
                    settings: _documentSettings,
                    AddMessage: AddMessage);
            }
        }

        /// <summary>
        /// The file path for the import settings file
        /// </summary>
        [ObservableProperty]
        private string _importSettingsFilePath;

        partial void OnImportSettingsFilePathChanged(string value)
        {
            if (!string.IsNullOrEmpty(value))
            {
                //import settings from given file path
                Dictionary<string, string> settingsString = Utils.SettingsImport.ImportSettingsFromJson(
                    filePath: value,
                    AddMessage: AddMessage
                );

                //check if the settings string is not null
                if (settingsString != null)
                {
                    // Update the settings in the export data model
                    _exportDataModel.Settings.DocumentNumberString = settingsString[nameof(Settings.DocumentNumberString)];

                    // Clear the settings table so it can be repopulated
                    _documentSettingsTable.Clear();

                    //populate data table with the settings string
                    PopulateDocumentSettingsDataTable();
                }
            }
        }

        #endregion import/export file paths

        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType)
        {
           if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Error)
            {
                //let user dismiss the message themselves for error messages, since they might want to copy the message text for further use, and errors are more important to see for a longer time
                _messageStore.EnqueueMessage(message, messageType);
            }
            else if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Information)
            {
                //just flash message to user for information messages, since they are less important and user might not need to copy the message text, and it is better to dismiss them after a short time to avoid too many messages building up in the UI
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds:2);
            }
            else
            {
                //default to short display time for other message types
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds:5);
            }
        }

        #region data tables

        /// <summary>
        /// Populate the data table containing the available parameters (sheet properties)
        /// </summary>
        private void PopulateParameterDataTable()
        {
            // check if any parameter names are present
            if (_exportDataModel.ParameterNames == null || _exportDataModel.ParameterNames.Count == 0)
            {
                //pop message to user
                AddMessage("No parameter names available.", MessageTypes.Error);
                return;
            }

            // Set up the data table
            DataTable dataTable = new();
            //add the default column
            dataTable.Columns.Add(_columnNameAvailableProperties);

            //add the values
            foreach (var propname in _exportDataModel.ParameterNames)
            {
                // Add a row per parameter
                DataRow row = dataTable.NewRow();
                row[_columnNameAvailableProperties] = propname;

                // Add the row to the data table
                dataTable.Rows.Add(row);
            }

            //store the table in global
            _dtAvailableParameters = dataTable;

            //setup a new data view based on the table created
            DvAvailableParameters = new DataView(dataTable);
        }

        /// <summary>
        /// Create an empty data table with the default columns for the document settings
        /// </summary>
        /// <returns>An empty data table.</returns>
        private DataTable CreateEmptySettingsDataTable()
        {
            //create an empty data table
            DataTable dataTable = new();
            //add the default columns
            dataTable.Columns.Add(_columnNameRulePrefix);
            dataTable.Columns.Add(_columnNameRuleParameter);
            dataTable.Columns.Add(_columnNameRuleSuffix);
            dataTable.Columns.Add(_columnNameRuleSeparator);
            return dataTable;
        }

        /// <summary>
        /// populate the data table containing the document name settings
        /// </summary>
        private void PopulateDocumentSettingsDataTable()
        {
            //set up an empty table
            DataTable dataTable = CreateEmptySettingsDataTable();

            //check if the current settings contain a settings string
            if (_exportDataModel.Settings.DocumentNumberString == null || _exportDataModel.Settings.DocumentNumberString == "")
            {
                //store the table in global
                _documentSettingsTable = dataTable;
                //setup a new data view based on the table created
                DvDocumentSettings = new DataView(dataTable);

                // get out of the function
                return;
            }

            //parse the settings string and add the values
            ObservableCollection<Utils.DocumentSetting> documentSettings = Utils.SettingsStringParser.ParseRevitSheetNumberSettingsString(
                _exportDataModel.Settings.DocumentNumberString,
                _exportDataModel.ParameterNames
            );

            //update the global collection with the parsed values
            _documentSettings = documentSettings;

            //update the data table with the parsed values
            foreach (var documentSetting in documentSettings)
            {
                // Add a row per setting
                DataRow row = dataTable.NewRow();
                row[_columnNameRulePrefix] = documentSetting.Prefix;
                row[_columnNameRuleParameter] = documentSetting.PropertyName;
                row[_columnNameRuleSuffix] = documentSetting.Suffix;
                row[_columnNameRuleSeparator] = documentSetting.Separator;
                // Add the row to the data table
                dataTable.Rows.Add(row);
            }

            //store the table in global
            _documentSettingsTable = dataTable;

            //refresh the data view
            DvDocumentSettings = new DataView(dataTable);
        }

        #endregion data tables

        #region commands

        /// <summary>
        /// Move the selected parameter to the document name table
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanMoveParameterToDocumentNameTable))]
        private void MoveParameterToDocumentNameTable()
        {
            //sync the document name table with the document settings
            SynchronizeDocumentNameTable();

            // get the parameter from the selected row and check if already in the document settings table
            //if not, add it to the document settings table

            foreach (Utils.DocumentSetting documentSetting in _documentSettings)
            {
                //check if the parameter is already in the document settings table
                if (documentSetting.PropertyName == SelectedParameter)
                {
                    //add message to user
                    AddMessage("Parameter already in document settings table.", MessageTypes.Error);
                    return;
                }
            }

            //create a new document setting object
            Utils.DocumentSetting newDocumentSetting = new(SelectedParameter);
            //add the new document setting to the document settings table at the end
            _documentSettings.Add(newDocumentSetting);

            //update the UI!!
            RefreshDocumentNameTable();
        }

        /// <summary>
        /// checks if there are any parameters available to move to the document name table
        /// and if not all parameters are already in the document settings table
        /// </summary>
        /// <returns></returns>
        private bool CanMoveParameterToDocumentNameTable() =>
            _dvAvailableParameters != null &&
            _dvDocumentSettings != null &&
            _dvAvailableParameters.Count > 0 &&
            _dvAvailableParameters.Count > _dvDocumentSettings.Count;

        /// <summary>
        /// Removes the selected parameter from the document name table
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanRemoveParameterFromDocumentNameTable))]
        private void RemoveParameterFromDocumentNameTable()
        {
            //sync the document name table with the document settings
            SynchronizeDocumentNameTable();

            // remove the selected parameter from the document name table
            // check if the selected index is within the bounds of the collection
            if (_selectedIndexDocumentNameSetting >= 0 && _selectedIndexDocumentNameSetting < _dvDocumentSettings.Count)
            {
                var selectedRow = _dvDocumentSettings[_selectedIndexDocumentNameSetting].Row;
                var parameterName = selectedRow[_columnNameRuleParameter].ToString();
                //remove the parameter from the document settings table
                foreach (Utils.DocumentSetting documentSetting in _documentSettings)
                {
                    if (documentSetting.PropertyName == parameterName)
                    {
                        _documentSettings.Remove(documentSetting);
                        break;
                    }
                }
            }

            //update the UI!!
            RefreshDocumentNameTable();
        }

        /// <summary>
        /// Checks if there are any parameters in the document settings table to remove
        /// </summary>
        /// <returns></returns>
        private bool CanRemoveParameterFromDocumentNameTable() =>
            _dvDocumentSettings != null && _dvDocumentSettings.Count > 0;

        /// <summary>
        /// Moves a selected item in the document name settings data table up
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanMoveUp))]
        private void MoveUp(DataGrid dataGrid)
        {
            //sync the document name table with the document settings
            SynchronizeDocumentNameTable();

            // get the current index of the selected item
            int index = _documentSettings.IndexOf(SelectedItemDocumentNameSetting);
            if (index > 0)
            {
                var item = _documentSettings[index];
                _documentSettings.RemoveAt(index);
                _documentSettings.Insert(index - 1, item);
                RefreshDocumentNameTable();
            }

            // keep the row selected
            if (dataGrid != null)
            {
                // Select the row by index
                SelectRowByIndex(dataGrid, index - 1);
            }
        }

        /// <summary>
        /// Checks if the selected item in the document name table can be moved up
        /// </summary>
        /// <returns></returns>
        private bool CanMoveUp() =>
            SelectedItemDocumentNameSetting != null &&
            SelectedIndexDocumentNameSetting > 0;

        /// <summary>
        /// Moves a selected item in the document name settings data table down
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanMoveDown))]
        private void MoveDown(DataGrid dataGrid)
        {
            //sync the document name table with the document settings
            SynchronizeDocumentNameTable();
            // get the current index of the selected item
            int index = _documentSettings.IndexOf(SelectedItemDocumentNameSetting);
            if (index < _documentSettings.Count - 1)
            {
                var item = _documentSettings[index];
                _documentSettings.RemoveAt(index);
                _documentSettings.Insert(index + 1, item);
                RefreshDocumentNameTable();
            }

            // keep the row selected
            if (dataGrid != null)
            {
                // Select the row by index
                SelectRowByIndex(dataGrid, index + 1);
            }
        }

        /// <summary>
        /// Checks if the selected item in the document name table can be moved down
        /// </summary>
        private bool CanMoveDown() =>
            SelectedItemDocumentNameSetting != null &&
            _documentSettings != null &&
            SelectedIndexDocumentNameSetting < _documentSettings.Count - 1;

        /// <summary>
        /// updates the settings in the export data model and closes the window
        /// </summary>
        [RelayCommand]
        private void SaveAndClose(Window window)
        {
            //sync the document name table with the document settings
            SynchronizeDocumentNameTable();

            // save the settings to the export data model
            _exportDataModel.Settings.DocumentNumberString = Utils.SettingsStringParser.ConvertSettingsToDocumentNumberString(_documentSettings);
            _exportDataModel.Settings.DatabasePath = DatabaseFilePath;
            
            if (window != null)
            {
                window.Close(); // Closes the window
            }
        }

        #endregion commands

        #region helper methods

        /// <summary>
        /// Refreshes the document name table after moving a parameter up or down or adding a new parameter or removing a parameter
        /// </summary>
        private void RefreshDocumentNameTable()
        {
            DataTable dt = CreateEmptySettingsDataTable();
            //update the data table with the values
            foreach (var documentSetting in _documentSettings)
            {
                // Add a row per setting
                DataRow row = dt.NewRow();
                row[_columnNameRulePrefix] = documentSetting.Prefix;
                row[_columnNameRuleParameter] = documentSetting.PropertyName;
                row[_columnNameRuleSuffix] = documentSetting.Suffix;
                row[_columnNameRuleSeparator] = documentSetting.Separator;
                // Add the row to the data table
                dt.Rows.Add(row);
            }

            _documentSettingsTable.Clear();
            _documentSettingsTable = dt;

            //update the UI!!
            DvDocumentSettings = new DataView(dt);
        }

        /// <summary>
        /// Synchronizes the document settings with data entered in the document name table
        /// </summary>
        private void SynchronizeDocumentNameTable()
        {
            //check if sync is required ( data table is empty )
            if (_documentSettingsTable == null || _documentSettingsTable.Rows.Count == 0)
            {
                //if the data table is empty, return
                return;
            }

            //update the objects in the document settings with the values in the data table
            //loop over data table and update the objects in the document collection
            foreach (DataRow row in _documentSettingsTable.Rows)
            {
                //get the values from the data table
                string prefix = row[_columnNameRulePrefix].ToString();
                string suffix = row[_columnNameRuleSuffix].ToString();
                string separator = row[_columnNameRuleSeparator].ToString();
                string propertyName = row[_columnNameRuleParameter].ToString();

                //loop over the document settings and update the objects
                foreach (Utils.DocumentSetting documentSetting in _documentSettings)
                {
                    if (documentSetting.PropertyName == propertyName)
                    {
                        documentSetting.Prefix = prefix;
                        documentSetting.Suffix = suffix;
                        documentSetting.Separator = separator;
                    }
                }
            }
        }

        /// <summary>
        /// Method to clear selection in document naming table
        /// Used when the data view is changed
        /// </summary>
        public void ClearSelection()
        {
            SelectedItemDocumentNameSetting = null;
            SelectedIndexDocumentNameSetting = -1;
        }

        /// <summary>
        /// Select the current row in the data grid by index.
        /// This is also meant to highlight the row selected..but only works partly ( row is grey rather than blue )
        /// </summary>
        public static void SelectRowByIndex(DataGrid dataGrid, int rowIndex)
        {
            if (rowIndex < 0 || rowIndex >= dataGrid.Items.Count) return;

            // Retrieve the row data
            DataRowView rowView = dataGrid.Items[rowIndex] as DataRowView;

            if (rowView != null)
            {
                dataGrid.SelectedItem = rowView;
                dataGrid.ScrollIntoView(rowView);
                dataGrid.UpdateLayout(); // Ensures the visual state is refreshed
            }

            // Ensure focus is set on the row itself
            DataGridRow row = (DataGridRow)dataGrid.ItemContainerGenerator.ContainerFromItem(rowView);
            row?.Focus(); // Force focus on the row to ensure it visually matches the mouse selection
        }

        /// <summary>
        /// On window closing, unsubscribe from the event to prevent memory leaks
        /// </summary>
        public override void OnClosing()
        {
            // Unsubscribe from the event to prevent memory leaks
            GlobalMessageViewModel?.Dispose();
        }

        /// <summary>
        /// Dispose of resources
        /// </summary>
        public override void Dispose()
        {
            // Additional cleanup if needed
            base.Dispose();
        }

        #endregion helper methods

        /// <summary>
        /// Constructor for the SettingsViewModel class.
        /// </summary>
        /// <param name="exportDataModel">The data model containing export settings and parameter names</param>
        /// <param name="globalMessageViewModel">View model for displaying global messages</param>
        /// <param name="messageStore">Store for managing messages</param>
        public SettingsViewModel(
            Models.ExportDataModel exportDataModel,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {
            //store the export data model
            _exportDataModel = exportDataModel;
            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;
            //store the message store
            _messageStore = messageStore;

            //initialize the document settings collection
            _documentSettings = new ObservableCollection<Utils.DocumentSetting>();

            //populate the data table containing the available parameters
            PopulateParameterDataTable();

            //populate the document settings data table
            PopulateDocumentSettingsDataTable();

            //populate the database file path
            _databaseFilePath = exportDataModel.Settings.DatabasePath;
        }
    }
}