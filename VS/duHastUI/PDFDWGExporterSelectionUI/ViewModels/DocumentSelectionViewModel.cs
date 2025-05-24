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


using duHastNet.Utils.WPF.Commands;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Data;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public class DocumentSelectionViewModel : ViewModelBase
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
        /// default view of the data table
        /// </summary>
        private DataView _dvAvailableParameters;

        /// <summary>
        /// Contains the settings data tables for the different document types
        /// </summary>
        private Dictionary<string, DataTable> _documentSettingsTables;

        /// <summary>
        ///  default view of the data table containing document settings
        /// </summary>
        private DataView _dvDocumentSettings;

        /// <summary>
        /// Dictionary containing the document naming settings per document type
        /// </summary>
        private Dictionary<string, ObservableCollection<Utils.DocumentSetting>> _documentSettingsDictionary;

        /// <summary>
        /// Command to add a parameter to the document name table
        /// </summary>
        private readonly duHastNet.Utils.WPF.Commands.RelayCommand _moveParameterToDocumentNameTableCommand;
        public ICommand MoveParameterToDocumentNameTableCommand { get { return _moveParameterToDocumentNameTableCommand; } }

        /// <summary>
        /// Command to remove a parameter from the document name table
        /// </summary>
        private readonly duHastNet.Utils.WPF.Commands.RelayCommand _removeParameterFromDocumentNameTableCommand;
        public ICommand RemoveParameterFromDocumentNameTableCommand { get { return _removeParameterFromDocumentNameTableCommand; } }

        /// <summary>
        /// command move selected parameter up in the document name table
        /// </summary>
        private readonly duHastNet.Utils.WPF.Commands.RelayCommand _moveUpCommand;
        public ICommand MoveUpCommand { get { return _moveUpCommand; } }

        /// <summary>
        /// command move selected parameter down in the document name table
        /// </summary>
        private readonly duHastNet.Utils.WPF.Commands.RelayCommand _moveDownCommand;
        public ICommand MoveDownCommand { get { return _moveDownCommand; } }

        /// <summary>
        /// command to save the settings and close the window
        /// </summary>
        private readonly duHastNet.Utils.WPF.Commands.RelayCommand _saveAndCloseCommand;
        public ICommand SaveAndCloseCommand { get { return _saveAndCloseCommand; } }


        #region column names

        /// <summary>
        /// single column name for available property table
        /// </summary>
        private string _columnNameAvailableProperties = "Sheet properties";

        /// <summary>
        /// column names for document naming table
        /// </summary>
        private string _columnNameRulePrefix = "Prefix";
        private string _columnNameRuleSuffix = "Suffix";
        private string _columnNameRuleParameter = "Sheet property";
        private string _columnNameRuleSeparator = "Separator";

        #endregion column names

        #region event handlers

        /// <summary>
        /// On window closing, unsubscribe from the event to prevent memory leaks
        /// </summary>
        public override void OnClosing()
        {

            if (GlobalMessageViewModel != null)
            {
                // Unsubscribe from the event to prevent memory leaks
                GlobalMessageViewModel.Dispose();
            }

            base.OnClosing();
        }

        #endregion event handlers

        #region document type filter

        /// <summary>
        /// available document types
        /// </summary>
        private string _documentTypePDFName = "PDF";
        private string _documentTypeDWGName = "DWG";

        // Field to return a default list of document type names
        private readonly List<string> _documentTypeNameDefaultList = new List<string>();

        // Property to expose the default list of document type names
        public List<string> DocumentTypeNameDefaultList => _documentTypeNameDefaultList;

        // field to store the selected document type
        private string _selectedDocumentType;
        public string SelectedDocumentType
        {
            get => _selectedDocumentType;
            set
            {
                _selectedDocumentType = value;

                //set the data view to the pdf settings table
                //this will also clear the selection in the document name table
                DataViewDocumentTypeSettings = new DataView(_documentSettingsTables[_selectedDocumentType]);

                // hide or show the dwg export option scheme names
                IsDWGExportSchemeVisible = _selectedDocumentType == _documentTypeDWGName;

                //update UI
                OnPropertyChanged(nameof(SelectedDocumentType));
            }
        }

        #endregion document type filter

        #region dwg export scheme name

        /// json Field to return the selected export scheme name
        private string _dwgExportSchemeNameProperty = "DWGExportSchemeName";

        // Field to return a list of dwg export scheme names
        private readonly List<string> _dwgExportSchemeNameList = new List<string>();

        // Property to expose the list of dwg export scheme names
        public List<string> DWGExportSchemeNameList => _dwgExportSchemeNameList;

        //field to store the selected export scheme name
        private string _selectedDWGExportSchemeName;
        public string SelectedDWGExportSchemeName
        {
            get => _selectedDWGExportSchemeName;
            set
            {
                _selectedDWGExportSchemeName = value;
                OnPropertyChanged(nameof(SelectedDWGExportSchemeName));
            }
        }

        // stores whether the dweg export scheme name is visible or not
        // this is used to show or hide the export scheme name in the UI
        private bool _isDWGExportSchemeVisible;

        public bool IsDWGExportSchemeVisible
        {
            get => _isDWGExportSchemeVisible;
            set
            {
                _isDWGExportSchemeVisible = value;
                OnPropertyChanged(nameof(IsDWGExportSchemeVisible));
            }
        }


        /// <summary>
        /// populates the list of dwg export scheme names
        /// </summary>
        /// <param name="dwgExportSchemes"></param>
        public void populateDWGExportSchemeNameList(List<string> dwgExportSchemes)
        {
            //populate the list of dwg export scheme names
            //check if the current settings contain a dwg export scheme name
            //and set up the data tables accordingly
            //clear the list
            _dwgExportSchemeNameList.Clear();
            //add the values
            foreach (var scheme in dwgExportSchemes)
            {
                _dwgExportSchemeNameList.Add(scheme);
            }
            //trigger property changed event
            OnPropertyChanged(nameof(DWGExportSchemeNameList));
        }

        #endregion dwg export scheme name

        #region user selection

        /// <summary>
        /// binding to show selected index of available parameters
        /// </summary>
        private int _selectedIndexAvailableParameters;

        public int SelectedIndexAvailableParameters
        {
            get => _selectedIndexAvailableParameters;
            set
            {
                if (_selectedIndexAvailableParameters != value)
                {
                    _selectedIndexAvailableParameters = value;
                    OnPropertyChanged(nameof(SelectedIndexAvailableParameters));
                    OnPropertyChanged(nameof(SelectedParameter));
                }
            }
        }


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
                // check if the selected index is within the bounds of the rooms collection
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
        private int _selectedIndexDocumentNameSetting;

        public int SelectedIndexDocumentNameSetting
        {
            get => _selectedIndexDocumentNameSetting;
            set
            {
                if (_selectedIndexDocumentNameSetting != value)
                {
                    _selectedIndexDocumentNameSetting = value;
                    OnPropertyChanged(nameof(SelectedIndexDocumentNameSetting));

                    if (_selectedIndexDocumentNameSetting >= 0 && _selectedIndexDocumentNameSetting <= _documentSettingsDictionary[SelectedDocumentType].Count)
                        //change the selected item as well... that will trigger the command can execute state updates for move up and down buttons
                        SelectedItemDocumentNameSetting = _documentSettingsDictionary[SelectedDocumentType][_selectedIndexDocumentNameSetting];
                    else if (_selectedIndexDocumentNameSetting == -1)
                    {
                        //reset the selected item in the naming table
                        SelectedItemDocumentNameSetting = null;
                    }
                }
            }
        }


        /// <summary>
        /// The selected document name setting
        /// </summary>
        private Utils.DocumentSetting _selectedItemDocumentNameSetting;

        public Utils.DocumentSetting SelectedItemDocumentNameSetting
        {
            get => _selectedItemDocumentNameSetting;
            set
            {

                //sync data table with the document settings dictionary before doc change
                synchronizeDocumentNameTable();

                _selectedItemDocumentNameSetting = value;
                OnPropertyChanged(nameof(SelectedItemDocumentNameSetting));

                // update the command can execute state
                if (MoveUpCommand != null)
                {
                    //update the command can execute state
                    ((RelayCommand)MoveUpCommand).RaiseCanExecuteChanged();
                }

                // update the command can execute state
                if (MoveDownCommand != null)
                {
                    ((RelayCommand)MoveDownCommand).RaiseCanExecuteChanged();
                }
            }
        }

        #endregion user selection

        #region data views

        /// <summary>
        /// binding in xaml property to the default view of the available parameters collection
        /// </summary>
        public DataView DataViewAvailableParameters
        {
            get => _dvAvailableParameters;
            private set
            {
                _dvAvailableParameters = value;
                OnPropertyChanged(nameof(DataViewAvailableParameters));
            }

        }

        /// <summary>
        /// binding in xaml property to the default view of the document type settings collection
        /// </summary>
        public DataView DataViewDocumentTypeSettings
        {
            get => _dvDocumentSettings;
            private set
            {
                _dvDocumentSettings = value;
                OnPropertyChanged(nameof(DataViewDocumentTypeSettings));

                //clear selection when changing doc type
                if (SelectedIndexDocumentNameSetting != -1 || SelectedItemDocumentNameSetting != null) { ClearSelection(); }

                // update the command can execute state
                if (MoveParameterToDocumentNameTableCommand != null)
                {
                    //update the command can execute state
                    ((RelayCommand)MoveParameterToDocumentNameTableCommand).RaiseCanExecuteChanged();
                }
                // update the command can execute state
                if (RemoveParameterFromDocumentNameTableCommand != null)
                {
                    //update the command can execute state
                    ((RelayCommand)RemoveParameterFromDocumentNameTableCommand).RaiseCanExecuteChanged();
                }
                // update the command can execute state
                if (MoveUpCommand != null)
                {
                    //update the command can execute state
                    ((RelayCommand)MoveUpCommand).RaiseCanExecuteChanged();
                }
                // update the command can execute state
                if (MoveDownCommand != null)
                {
                    ((RelayCommand)MoveDownCommand).RaiseCanExecuteChanged();
                }
            }
        }

        #endregion data views

        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType)
        {

            _messageStore.SetCurrentMessage(message, messageType);
        }


        #region data tables

        /// <summary>
        /// Populate the data table containing the available parameters (sheet properties)
        /// </summary>
        private void populateParameterDataTable()
        {
            //populate the data table containing the available parameters
            //check if the current settings contain a dwg or pdf settings string
            //and set up the data tables accordingly

            // check if any parameter names are present
            if (_exportDataModel.ParameterNames == null || _exportDataModel.ParameterNames.Count == 0)
            {
                //pop message to user
                AddMessage("No parameter names available.", MessageTypes.Error);
                return;
            }

            // Set up the data table
            DataTable dataTable = new DataTable();
            //add the default column
            dataTable.Columns.Add(_columnNameAvailableProperties);

            //add the values
            foreach (var propname in _exportDataModel.ParameterNames)
            {
                // Add a row per room
                DataRow row = dataTable.NewRow();
                row[_columnNameAvailableProperties] = propname;

                // Add the row to the data table
                dataTable.Rows.Add(row);
            }

            //store the table in global
            _dtAvailableParameters = dataTable;

            //setup a new data view based on the table created
            //this will also trigger an on property changed event
            DataViewAvailableParameters = new DataView(dataTable);
        }

        /// <summary>
        /// Create an empty data table with the default columns for the document settings
        /// </summary>
        /// <returns>An empty data table.</returns>
        private DataTable CreateEmptySettingsDataTable()
        {
            //create an empty data table
            DataTable dataTable = new DataTable();
            //add the default columns
            dataTable.Columns.Add(_columnNameRulePrefix);
            dataTable.Columns.Add(_columnNameRuleParameter);
            dataTable.Columns.Add(_columnNameRuleSuffix);
            dataTable.Columns.Add(_columnNameRuleSeparator);
            return dataTable;
        }

        /// <summary>
        /// populate the data table containing the pdf name settings
        /// </summary>
        private void populatePDFSettingsDataTable()
        {
            //populate the data table containing the pdf settings
            //check if the current settings contain a pdf settings string
            //and set up the data tables accordingly

            //set up an empty table
            DataTable dataTable = CreateEmptySettingsDataTable();

            //check if the current settings contain a pdf settings string
            if (_exportDataModel.Settings.PDFRenameString == null || _exportDataModel.Settings.PDFRenameString == "")
            {
                //store the table in global
                _documentSettingsTables.Add(_documentTypePDFName, dataTable);
                //setup a new data view based on the table created
                //this will also trigger an on property changed event
                DataViewDocumentTypeSettings = new DataView(dataTable);

                // get out of the function
                return;
            }

            //parse the settings string and add the values
            ObservableCollection<Utils.DocumentSetting> pdfDocumentSettings = Utils.SettingsStringParser.ParsePdfSettingsString(
                _exportDataModel.Settings.PDFRenameString,
                _exportDataModel.ParameterNames
            );

            //update the global dictionary with the parsed values
            _documentSettingsDictionary[_documentTypePDFName] = pdfDocumentSettings;

            //update the data table with the parsed values
            foreach (var pdfDocumentSetting in pdfDocumentSettings)
            {
                // Add a row per room
                DataRow row = dataTable.NewRow();
                row[_columnNameRulePrefix] = pdfDocumentSetting.Prefix;
                row[_columnNameRuleParameter] = pdfDocumentSetting.PropertyName;
                row[_columnNameRuleSuffix] = pdfDocumentSetting.Suffix;
                row[_columnNameRuleSeparator] = pdfDocumentSetting.Separator;
                // Add the row to the data table
                dataTable.Rows.Add(row);
            }

            //store the table in global
            _documentSettingsTables.Add(_documentTypePDFName, dataTable);

            //refresh the data view
            DataViewDocumentTypeSettings = new DataView(dataTable);

            return;
        }

        /// <summary>
        /// populate the data table containing the dwg name settings
        /// </summary>
        private void popualateDWGSettingsDataTable()
        {
            //populate the data table containing the dwg settings
            //check if the current settings contain a  dwg settings string
            //and set up the data tables accordingly

            //set up an empty table
            DataTable dataTable = CreateEmptySettingsDataTable();

            //check if the current settings contain a dwg settings string
            if (_exportDataModel.Settings.DWGRenameString == null || _exportDataModel.Settings.DWGRenameString == "")
            {
                //store the table in global
                _documentSettingsTables.Add(_documentTypeDWGName, dataTable);
                // do not set the data view here, as this will be done in the populateAvailableFilters function
                //and the default view will be set to the pdf settings table
                // get out of the function
                return;
            }

            //parse the settings string and add the values
            ObservableCollection<Utils.DocumentSetting> dwgDocumentSettings = Utils.SettingsStringParser.ParseDwgSettingsString(
                _exportDataModel.Settings.DWGRenameString,
                _exportDataModel.ParameterNames
            );

            //update the global dictionary with the parsed values
            _documentSettingsDictionary[_documentTypeDWGName] = dwgDocumentSettings;

            //update the data table with the parsed values
            foreach (var dwgDocumentSetting in dwgDocumentSettings)
            {
                // Add a row per room
                DataRow row = dataTable.NewRow();
                row[_columnNameRulePrefix] = dwgDocumentSetting.Prefix;
                row[_columnNameRuleParameter] = dwgDocumentSetting.PropertyName;
                row[_columnNameRuleSuffix] = dwgDocumentSetting.Suffix;
                row[_columnNameRuleSeparator] = dwgDocumentSetting.Separator;
                // Add the row to the data table
                dataTable.Rows.Add(row);
            }

            //store the table in global
            _documentSettingsTables.Add(_documentTypeDWGName, dataTable);

            // do not set the data view here, as this will be done in the populateAvailableFilters function
            //and the default view will be set to the pdf settings table
            // get out of the function
            return;

        }

        #endregion data tables

        private void populateAvailableFilters()
        {
            //populate the available filters list ( PDF and DWG)
            //set the filter to display pdf settings by default
            //this will be trigger a view change to show the selected data table

            _documentTypeNameDefaultList.Add(_documentTypePDFName);
            _documentTypeNameDefaultList.Add(_documentTypeDWGName);

            //also populat global dictionary of document settings
            foreach (var documentType in _documentTypeNameDefaultList)
            {
                //create an empty list of document settings
                ObservableCollection<Utils.DocumentSetting> documentSettings = new ObservableCollection<Utils.DocumentSetting>();
                //add the empty list to the dictionary
                _documentSettingsDictionary.Add(documentType, documentSettings);
            }

            // trigger the property changed event
            OnPropertyChanged(nameof(DocumentTypeNameDefaultList));
        }

        private void setFilterToPDFSettings()
        {
            //set the filter to display pdf settings by default
            //this will be trigger a view change to show the selected data table
            SelectedDocumentType = _documentTypePDFName;
        }

        /// <summary>
        /// Set the selected export scheme name to the one in the settings if it exists
        /// </summary>
        private void setSelectedDWGExportScheme()
        {
            // set the dwg export scheme name to the first one in the list if none in settings
            if (_exportDataModel.Settings.DWGExportScheme == null || _exportDataModel.Settings.DWGExportScheme == "")
            {
                //set the selected export scheme name to the first one in the list
                if (_dwgExportSchemeNameList.Count > 0)
                {
                    SelectedDWGExportSchemeName = _dwgExportSchemeNameList[0];
                }
            }
            else
            {
                //set the selected export scheme name to the one in the settings if it exists
                //check if the selected export scheme name is in the list
                if (_dwgExportSchemeNameList.Contains(_exportDataModel.Settings.DWGExportScheme))
                {
                    SelectedDWGExportSchemeName = _exportDataModel.Settings.DWGExportScheme;
                }
                else
                {
                    //add message to user
                    AddMessage("Retrieved DWG export scheme name not in list.", MessageTypes.Error);
                    //set the selected export scheme name to the first one in the list
                    if (_dwgExportSchemeNameList.Count > 0)
                    {
                        SelectedDWGExportSchemeName = _dwgExportSchemeNameList[0];
                    }
                }
            }
        }


        #region button underlying functions

        /// <summary>
        /// checks if there are any parameters available to move to the document name table
        /// and if not all parameteers are already in the document settings table
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        private bool CanMoveToTableDocumentSettings(object parameter) => _dvAvailableParameters.Count > 0 && _dvAvailableParameters.Count > _dvDocumentSettings.Count;

        /// <summary>
        /// Checks if there are any parameters available to move to the property namer table
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        private bool CanMoveToTableParameterNames(object parameter) => _dvDocumentSettings.Count > 0;

        /// <summary>
        /// Move the selected parameter to the document name table
        /// </summary>
        /// <param name="parameter"></param>
        private void MoveParameterToDocumentNameTable(object parameter)
        {

            //sync the document name table with the document settings dictionary
            synchronizeDocumentNameTable();

            // get the parameter from the selected row and check if already in the document settings table
            //if not, add it to the document settings table

            foreach (Utils.DocumentSetting documentSetting in _documentSettingsDictionary[SelectedDocumentType])
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
            Utils.DocumentSetting newDocumentSetting = new Utils.DocumentSetting(SelectedParameter);
            //add the new document setting to the document settings table add the end
            _documentSettingsDictionary[SelectedDocumentType].Add(newDocumentSetting);

            //update the UI!!
            RefreshDocumentNameTable();
        }

        /// <summary>
        /// Removes the selected parameter from the document name table
        /// </summary>
        private void RemoveParameterFromDocumentNameTable(object parameter)
        {
            //sync the document name table with the document settings dictionary
            synchronizeDocumentNameTable();

            // remove the selected parameter from the document name table
            // check if the selected index is within the bounds of the rooms collection
            if (_selectedIndexDocumentNameSetting >= 0 && _selectedIndexDocumentNameSetting < _dvDocumentSettings.Count)
            {
                var selectedRow = _dvDocumentSettings[_selectedIndexDocumentNameSetting].Row;
                var parameterName = selectedRow[_columnNameRuleParameter].ToString();
                //remove the parameter from the document settings table
                foreach (Utils.DocumentSetting documentSetting in _documentSettingsDictionary[SelectedDocumentType])
                {
                    if (documentSetting.PropertyName == parameterName)
                    {
                        _documentSettingsDictionary[SelectedDocumentType].Remove(documentSetting);
                        break;
                    }
                }
            }

            //update the UI!!
            RefreshDocumentNameTable();
        }

        /// <summary>
        /// Refreshes the document name table after moving a parameter up or down or adding a new parameter or removing a parameter
        /// </summary>
        private void RefreshDocumentNameTable()
        {
            DataTable dt = CreateEmptySettingsDataTable();
            //update the data table with the parsed values
            foreach (var documentSetting in _documentSettingsDictionary[SelectedDocumentType])
            {
                // Add a row per room
                DataRow row = dt.NewRow();
                row[_columnNameRulePrefix] = documentSetting.Prefix;
                row[_columnNameRuleParameter] = documentSetting.PropertyName;
                row[_columnNameRuleSuffix] = documentSetting.Suffix;
                row[_columnNameRuleSeparator] = documentSetting.Separator;
                // Add the row to the data table
                dt.Rows.Add(row);
            }

            _documentSettingsTables[SelectedDocumentType].Clear();
            _documentSettingsTables[SelectedDocumentType] = dt;

            //update the UI!!
            DataViewDocumentTypeSettings = new DataView(dt);
        }

        /// <summary>
        /// Synchronizes the document settings with data entered in the document name table
        /// </summary>
        private void synchronizeDocumentNameTable()
        {

            //check if sync is required ( data table is empty )
            if (SelectedDocumentType == null || _documentSettingsTables[SelectedDocumentType].Rows.Count == 0)
            {
                //if the data table is empty, return
                return;
            }

            //update the objects in the document settings table with the values in the data table
            //loop over data table and update the objects in the document dictionary
            foreach (DataRow row in _documentSettingsTables[SelectedDocumentType].Rows)
            {
                //get the values from the data table
                string prefix = row[_columnNameRulePrefix].ToString();
                string suffix = row[_columnNameRuleSuffix].ToString();
                string separator = row[_columnNameRuleSeparator].ToString();
                string propertyName = row[_columnNameRuleParameter].ToString();

                //loop over the document settings dictionary and update the objects
                foreach (Utils.DocumentSetting documentSetting in _documentSettingsDictionary[SelectedDocumentType])
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
        /// Checks if the selected item in the document name table can be moved up
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        private bool CanMoveUp(object parameter) => SelectedItemDocumentNameSetting != null &&
            SelectedIndexDocumentNameSetting > 0;

        /// <summary>
        /// Checks if the selected item in the document name table can be moved down
        /// </summary>
        private bool CanMoveDown(object parameter) => SelectedItemDocumentNameSetting != null &&
            SelectedIndexDocumentNameSetting < _documentSettingsDictionary[SelectedDocumentType].Count - 1;

        /// <summary>
        /// Moves a selected item in the document name settings data table up
        /// </summary>
        private void MoveUp(object parameter)
        {
            //sync the document name table with the document settings dictionary
            synchronizeDocumentNameTable();

            // get the current index of the selected item
            int index = _documentSettingsDictionary[SelectedDocumentType].IndexOf(SelectedItemDocumentNameSetting);
            if (index > 0)
            {
                var item = _documentSettingsDictionary[SelectedDocumentType][index];
                _documentSettingsDictionary[SelectedDocumentType].RemoveAt(index);
                _documentSettingsDictionary[SelectedDocumentType].Insert(index - 1, item);
                RefreshDocumentNameTable();
                //SelectedItemDocumentNameSetting = item; // Ensure selection follows move
            }

            // keep the row selected
            var dataGrid = parameter as DataGrid;  // Get the actual DataGrid instance
            if (dataGrid != null)
            {
                // Select the row by index
                SelectRowByIndex(dataGrid, index - 1);
            }
        }

        /// <summary>
        /// Moves a selected item in the document name settings data table down
        /// </summary>
        private void MoveDown(object parameter)
        {
            //sync the document name table with the document settings dictionary
            synchronizeDocumentNameTable();
            // get the current index of the selected item
            int index = _documentSettingsDictionary[SelectedDocumentType].IndexOf(SelectedItemDocumentNameSetting);
            if (index < _documentSettingsDictionary[SelectedDocumentType].Count - 1)
            {
                var item = _documentSettingsDictionary[SelectedDocumentType][index];
                _documentSettingsDictionary[SelectedDocumentType].RemoveAt(index);
                _documentSettingsDictionary[SelectedDocumentType].Insert(index + 1, item);
                RefreshDocumentNameTable();
                //SelectedItemDocumentNameSetting = item;
            }

            // keep the row selected
            var dataGrid = parameter as DataGrid;  // Get the actual DataGrid instance
            if (dataGrid != null)
            {
                // Select the row by index
                SelectRowByIndex(dataGrid, index + 1);
            }
        }


        /// <summary>
        /// The file path for the export settings file
        /// </summary>
        private string _selectedExportFilePath;

        /// <summary>
        /// property handling file path changes
        /// </summary>
        public string ExportSettingsFilePath
        {
            get => _selectedExportFilePath;
            set
            {
                if (_selectedExportFilePath != value)
                {
                    _selectedExportFilePath = value;

                    //build a dictioanry to be written to file
                    Dictionary<string, object> settingsDictionary = new Dictionary<string, object>()
                    {
                        { _documentTypePDFName, _documentSettingsDictionary[_documentTypePDFName] },
                        { _documentTypeDWGName, _documentSettingsDictionary[_documentTypeDWGName] },
                        {_dwgExportSchemeNameProperty, SelectedDWGExportSchemeName }
                    };

                    //export settings to given file path
                    duHastNet.UI.PDFDWGExporterUI.Utils.SettingsExport.ExportSettingsToJson(
                        filePath: _selectedExportFilePath,
                        settings: settingsDictionary,
                        AddMessage: AddMessage);

                    OnPropertyChanged(nameof(ExportSettingsFilePath));
                }
            }
        }

        /// <summary>
        /// The file path for the import settings file
        /// </summary>
        private string _selectedImportFilePath;

        /// <summary>
        /// property handling import file path changes
        /// </summary>
        public string ImportSettingsFilePath
        {
            get => _selectedImportFilePath;
            set
            {
                if (_selectedImportFilePath != value)
                {
                    _selectedImportFilePath = value;

                    //import settings from given file path
                    Dictionary<string, string> settingsDictionary = Utils.SettingsImport.ImportSettingsFromJson(
                        filePath: _selectedImportFilePath,
                        AddMessage: AddMessage
                    );

                    //check if the settings dictionary is not null
                    if (settingsDictionary != null)
                    {
                        //check if required keys are present
                        if (!settingsDictionary.ContainsKey(_documentTypePDFName) || 
                            !settingsDictionary.ContainsKey(_documentTypeDWGName )||
                            !settingsDictionary.ContainsKey(_dwgExportSchemeNameProperty))
                        {
                            //add message to user
                            AddMessage("Settings file does not contain required keys.", MessageTypes.Error);
                            return;
                        }

                        //clear the overalll settings tables dictionary so it can be repopulated
                        _documentSettingsTables.Clear();

                        //store settings strings in settings
                        _exportDataModel.Settings.PDFRenameString = settingsDictionary[_documentTypePDFName];
                        _exportDataModel.Settings.DWGRenameString = settingsDictionary[_documentTypeDWGName];
                        _exportDataModel.Settings.DWGExportScheme = settingsDictionary[_dwgExportSchemeNameProperty];

                        //populate data tables with the settings strings
                        populatePDFSettingsDataTable();
                        popualateDWGSettingsDataTable();

                        //set the selected export scheme name
                        setSelectedDWGExportScheme();

                        // reset the current document type to the pdf settings
                        //this will be trigger a view change to show the selected data table
                        setFilterToPDFSettings();
                    }

                    OnPropertyChanged(nameof(ImportSettingsFilePath));
                }
            }
        }

        /// <summary>
        /// updates the settings in the export data model and closes the window
        /// </summary>
        /// <param name="window"></param>
        private void SaveSettingsAndClose(object window)
        {

            //sync the document name table with the document settings dictionary
            synchronizeDocumentNameTable();

            // save the settings to the export data model
            _exportDataModel.Settings.PDFRenameString = Utils.SettingsStringParser.ConvertSettingsToPDFString(_documentSettingsDictionary[_documentTypePDFName]);
            _exportDataModel.Settings.DWGRenameString = Utils.SettingsStringParser.ConvertSettingsToDwgString(_documentSettingsDictionary[_documentTypeDWGName]);
            _exportDataModel.Settings.DWGExportScheme = SelectedDWGExportSchemeName;

            if (window is Window w)
            {
                w.Close(); // Closes the window
            }
        }

        /// <summary>
        /// Method to clear selection in document naming table
        /// Used when the document type is changed
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
            if (row != null)
            {
                row.Focus(); // Force focus on the row to ensure it visually matches the mouse selection
            }
        }

        #endregion button underlying functions

        /// <summary>
        /// Constructor for the SettingsViewModel class.
        /// </summary>
        /// <param name="globalMessageViewModel"></param>
        /// <param name="messageStore"></param>
        public DocumentSelectionViewModel(
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

            _documentSettingsTables = new Dictionary<string, DataTable>();
            _documentSettingsDictionary = new Dictionary<string, ObservableCollection<Utils.DocumentSetting>>();

            //populate the data table containing the available parameters
            populateParameterDataTable();

            //populate the available filters list ( PDF and DWG)
            populateAvailableFilters();

            //populate available dwg export scheme names
            populateDWGExportSchemeNameList(_exportDataModel.DWGExportSchemeNames);

            //check if the current settings contain a dwg or pdf settings string
            //and set up the data tables accordingly
            populatePDFSettingsDataTable();
            popualateDWGSettingsDataTable();

            //set up all commands:
            //push in
            _moveParameterToDocumentNameTableCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
                MoveParameterToDocumentNameTable,
                CanMoveToTableDocumentSettings
            );

            //push out
            _removeParameterFromDocumentNameTableCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
                RemoveParameterFromDocumentNameTable,
                CanMoveToTableParameterNames
            );

            //push up
            _moveUpCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
                MoveUp,
                CanMoveUp
            );

            //push down
            _moveDownCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
                MoveDown,
                CanMoveDown
            );

            //save and exit
            _saveAndCloseCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
                SaveSettingsAndClose,
                (object parameter) => true //always enabled
            );

            //set the selected dwg export scheme
            setSelectedDWGExportScheme();

            //set the filter to display pdf settings by default
            //this will be trigger a view change to show the selected data table, hence last thing in the constructor
            setFilterToPDFSettings();
        }
    }
}
