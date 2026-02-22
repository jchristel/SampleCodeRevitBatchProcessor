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


using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.UI.PDFDWGExporterUI.Models;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Data;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace duHastNet.UI.PDFDWGExporterUI.ViewModels
{
    public partial class SettingsViewModel : AppViewModelBase
    {
        /// <summary>
        /// Global message view model for displaying messages to the user.
        /// </summary>
        public GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// Message store for storing messages.
        /// </summary>
        private readonly MessageStore _messageStore;

        /// <summary>
        /// The data model for the export settings.
        /// </summary>
        private readonly Models.ExportDataModel _exportDataModel;

        /// <summary>
        /// Settings built in UI and to be returned to caller.
        /// </summary>
        public Utils.Settings Settings => _exportDataModel.Settings;

        /// <summary>
        /// Data table containing the available parameters.
        /// </summary>
        private DataTable _dtAvailableParameters;

        /// <summary>
        /// Default view of the available parameters data table.
        /// </summary>
        private DataView _dvAvailableParameters;

        /// <summary>
        /// Contains the settings data tables for the different document types.
        /// </summary>
        private Dictionary<string, DataTable> _documentSettingsTables;

        /// <summary>
        /// Default view of the document type settings data table.
        /// </summary>
        private DataView _dvDocumentSettings;

        /// <summary>
        /// Dictionary containing the document naming settings per document type.
        /// </summary>
        private Dictionary<string, ObservableCollection<Utils.DocumentSetting>> _documentSettingsDictionary;

        #region commands

        /// <summary>
        /// Command to add a parameter to the document name table.
        /// </summary>
        private RelayCommand? _moveParameterToDocumentNameTableCommand;
        public ICommand? MoveParameterToDocumentNameTableCommand => _moveParameterToDocumentNameTableCommand;

        /// <summary>
        /// Command to remove a parameter from the document name table.
        /// </summary>
        private RelayCommand? _removeParameterFromDocumentNameTableCommand;
        public ICommand? RemoveParameterFromDocumentNameTableCommand => _removeParameterFromDocumentNameTableCommand;

        /// <summary>
        /// Command to move selected parameter up in the document name table.
        /// </summary>
        private RelayCommand<object>? _moveUpCommand;
        public ICommand? MoveUpCommand => _moveUpCommand;

        /// <summary>
        /// Command to move selected parameter down in the document name table.
        /// </summary>
        private RelayCommand<object>? _moveDownCommand;
        public ICommand? MoveDownCommand => _moveDownCommand;

        /// <summary>
        /// Command to save the settings and close the window.
        /// </summary>
        private RelayCommand<object>? _saveAndCloseCommand;
        public ICommand? SaveAndCloseCommand => _saveAndCloseCommand;

        #endregion commands

        #region column names

        private string _columnNameAvailableProperties = "Sheet properties";
        private readonly string _columnNameRulePrefix = "Prefix";
        private readonly string _columnNameRuleSuffix = "Suffix";
        private readonly string _columnNameRuleParameter = "Sheet property";
        private readonly string _columnNameRuleSeparator = "Separator";

        #endregion column names

        #region event handlers

        public override void OnClosing()
        {
            System.Diagnostics.Debug.WriteLine("SettingsViewModel.OnClosing() called");
            base.OnClosing();
        }

        public override void Dispose()
        {
            System.Diagnostics.Debug.WriteLine("SettingsViewModel.Dispose() called");
            base.Dispose();
        }

        #endregion event handlers

        #region document type filter

        private readonly string _documentTypePDFName = "PDF";
        private readonly string _documentTypeDWGName = "DWG";

        // Get-only: backing list is mutated in place by PopulateAvailableFilters()
        private List<string> _documentTypeNameDefaultList = [];
        public List<string> DocumentTypeNameDefaultList => _documentTypeNameDefaultList;

        /// <summary>
        /// The selected document type (PDF or DWG).
        /// Side effects: updates DataViewDocumentTypeSettings and IsDWGExportSchemeVisible.
        /// </summary>
        [ObservableProperty]
        private string _selectedDocumentType;

        partial void OnSelectedDocumentTypeChanged(string value)
        {
            // update the data view to the selected document type settings table
            // (this also clears the selection in the document name table via DataViewDocumentTypeSettings setter)
            DataViewDocumentTypeSettings = new DataView(_documentSettingsTables[value]);

            // show or hide the DWG export scheme selector
            IsDWGExportSchemeVisible = value == _documentTypeDWGName;
        }

        #endregion document type filter

        #region dwg export scheme name

        private string _dwgExportSchemeNameProperty = "DWGExportSchemeName";

        // Get-only: backing list is mutated in place by PopulateDWGExportSchemeNameList()
        private readonly List<string> _dwgExportSchemeNameList = [];
        public List<string> DWGExportSchemeNameList => _dwgExportSchemeNameList;

        /// <summary>
        /// The selected DWG export scheme name.
        /// </summary>
        [ObservableProperty]
        private string _selectedDWGExportSchemeName;

        /// <summary>
        /// Controls visibility of the DWG export scheme selector in the UI.
        /// </summary>
        [ObservableProperty]
        private bool _isDWGExportSchemeVisible;

        /// <summary>
        /// Populates the list of DWG export scheme names.
        /// </summary>
        public void PopulateDWGExportSchemeNameList(List<string> dwgExportSchemes)
        {
            _dwgExportSchemeNameList.Clear();
            foreach (var scheme in dwgExportSchemes)
            {
                _dwgExportSchemeNameList.Add(scheme);
            }
            // Notify UI since the list is mutated in place, not replaced
            OnPropertyChanged(nameof(DWGExportSchemeNameList));
        }

        #endregion dwg export scheme name

        #region user selection

        /// <summary>
        /// The selected index in the available parameters list.
        /// Side effect: also notifies SelectedParameter (computed from this index).
        /// Equality guard handled automatically by [ObservableProperty].
        /// </summary>
        [ObservableProperty]
        private int _selectedIndexAvailableParameters;

        partial void OnSelectedIndexAvailableParametersChanged(int value)
        {
            // SelectedParameter is a computed get-only property that reads from this index,
            // so we must manually notify when the index changes.
            OnPropertyChanged(nameof(SelectedParameter));
        }

        /// <summary>
        /// The selected parameter name. Computed from the current index and data view — get-only.
        /// </summary>
        public string SelectedParameter
        {
            get
            {
                if (_dvAvailableParameters == null) return null;
                if (_selectedIndexAvailableParameters >= 0 && _selectedIndexAvailableParameters < _dvAvailableParameters.Count)
                {
                    var selectedRow = _dvAvailableParameters[_selectedIndexAvailableParameters].Row;
                    return selectedRow[_columnNameAvailableProperties].ToString();
                }
                return null;
            }
        }

        /// <summary>
        /// The selected index in the document name settings table.
        /// Side effect: updates SelectedItemDocumentNameSetting to keep them in sync.
        /// Equality guard handled automatically by [ObservableProperty].
        /// </summary>
        [ObservableProperty]
        private int _selectedIndexDocumentNameSetting;

        partial void OnSelectedIndexDocumentNameSettingChanged(int value)
        {
            if (value >= 0 && value <= _documentSettingsDictionary[SelectedDocumentType].Count)
            {
                SelectedItemDocumentNameSetting = _documentSettingsDictionary[SelectedDocumentType][value];
            }
            else if (value == -1)
            {
                SelectedItemDocumentNameSetting = null;
            }
        }

        /// <summary>
        /// The selected document name setting item.
        /// Side effects: syncs the document name table and notifies move commands.
        /// </summary>
        [ObservableProperty]
        private Utils.DocumentSetting _selectedItemDocumentNameSetting;

        partial void OnSelectedItemDocumentNameSettingChanged(Utils.DocumentSetting value)
        {
            SynchronizeDocumentNameTable();
            _moveUpCommand?.NotifyCanExecuteChanged();
            _moveDownCommand?.NotifyCanExecuteChanged();
        }

        #endregion user selection

        #region data views

        /// <summary>
        /// Binding to the default view of the available parameters collection.
        /// Uses SetProperty with a private setter — [ObservableProperty] only generates public setters.
        /// </summary>
        private DataView _dataViewAvailableParameters;
        public DataView DataViewAvailableParameters
        {
            get => _dataViewAvailableParameters;
            private set => SetProperty(ref _dataViewAvailableParameters, value);
        }

        /// <summary>
        /// Binding to the default view of the document type settings collection.
        /// Uses a manual property with SetProperty — private setter with side effects
        /// (clears selection and notifies commands) that cannot be expressed via [ObservableProperty].
        /// </summary>
        private DataView _dataViewDocumentTypeSettings;
        public DataView DataViewDocumentTypeSettings
        {
            get => _dataViewDocumentTypeSettings;
            private set
            {
                if (SetProperty(ref _dataViewDocumentTypeSettings, value))
                {
                    // Keep the internal _dvDocumentSettings reference in sync for methods
                    // that access it directly (CanMoveToTableDocumentSettings, etc.)
                    _dvDocumentSettings = value;

                    // Clear selection when changing document type
                    if (SelectedIndexDocumentNameSetting != -1 || SelectedItemDocumentNameSetting != null)
                    {
                        ClearSelection();
                    }

                    // Notify commands to re-evaluate CanExecute
                    _moveParameterToDocumentNameTableCommand?.NotifyCanExecuteChanged();
                    _removeParameterFromDocumentNameTableCommand?.NotifyCanExecuteChanged();
                    _moveUpCommand?.NotifyCanExecuteChanged();
                    _moveDownCommand?.NotifyCanExecuteChanged();
                }
            }
        }

        #endregion data views

        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI.
        /// </summary>
        public void AddMessage(string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType)
        {
            if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Error)
            {
                _messageStore.EnqueueMessage(message, messageType);
            }
            else if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Information)
            {
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 2);
            }
            else
            {
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 5);
            }
        }


        #region data tables

        /// <summary>
        /// Populates the data table containing the available parameters (sheet properties).
        /// </summary>
        private void PopulateParameterDataTable()
        {
            if (_exportDataModel.ParameterNames == null || _exportDataModel.ParameterNames.Count == 0)
            {
                AddMessage("No parameter names available.", MessageTypes.Error);
                return;
            }

            DataTable dataTable = new();
            dataTable.Columns.Add(_columnNameAvailableProperties);

            foreach (var propname in _exportDataModel.ParameterNames)
            {
                DataRow row = dataTable.NewRow();
                row[_columnNameAvailableProperties] = propname;
                dataTable.Rows.Add(row);
            }

            _dtAvailableParameters = dataTable;
            // _dvAvailableParameters kept in sync for methods that read it directly
            _dvAvailableParameters = new DataView(dataTable);
            DataViewAvailableParameters = _dvAvailableParameters;
        }

        /// <summary>
        /// Creates an empty data table with the default columns for the document settings.
        /// </summary>
        private DataTable CreateEmptySettingsDataTable()
        {
            DataTable dataTable = new();
            dataTable.Columns.Add(_columnNameRulePrefix);
            dataTable.Columns.Add(_columnNameRuleParameter);
            dataTable.Columns.Add(_columnNameRuleSuffix);
            dataTable.Columns.Add(_columnNameRuleSeparator);
            return dataTable;
        }

        /// <summary>
        /// Populates the data table containing the PDF name settings.
        /// </summary>
        private void PopulatePDFSettingsDataTable()
        {
            DataTable dataTable = CreateEmptySettingsDataTable();

            if (_exportDataModel.Settings.PDFRenameString == null || _exportDataModel.Settings.PDFRenameString == "")
            {
                _documentSettingsTables.Add(_documentTypePDFName, dataTable);
                DataViewDocumentTypeSettings = new DataView(dataTable);
                return;
            }

            ObservableCollection<Utils.DocumentSetting> pdfDocumentSettings = Utils.SettingsStringParser.ParsePdfSettingsString(
                _exportDataModel.Settings.PDFRenameString,
                _exportDataModel.ParameterNames
            );
            _documentSettingsDictionary[_documentTypePDFName] = pdfDocumentSettings;

            foreach (var pdfDocumentSetting in pdfDocumentSettings)
            {
                DataRow row = dataTable.NewRow();
                row[_columnNameRulePrefix] = pdfDocumentSetting.Prefix;
                row[_columnNameRuleParameter] = pdfDocumentSetting.PropertyName;
                row[_columnNameRuleSuffix] = pdfDocumentSetting.Suffix;
                row[_columnNameRuleSeparator] = pdfDocumentSetting.Separator;
                dataTable.Rows.Add(row);
            }

            _documentSettingsTables.Add(_documentTypePDFName, dataTable);
            DataViewDocumentTypeSettings = new DataView(dataTable);
        }

        /// <summary>
        /// Populates the data table containing the DWG name settings.
        /// </summary>
        private void PopualateDWGSettingsDataTable()
        {
            DataTable dataTable = CreateEmptySettingsDataTable();

            if (_exportDataModel.Settings.DWGRenameString == null || _exportDataModel.Settings.DWGRenameString == "")
            {
                _documentSettingsTables.Add(_documentTypeDWGName, dataTable);
                return;
            }

            ObservableCollection<Utils.DocumentSetting> dwgDocumentSettings = Utils.SettingsStringParser.ParseDwgSettingsString(
                _exportDataModel.Settings.DWGRenameString,
                _exportDataModel.ParameterNames
            );
            _documentSettingsDictionary[_documentTypeDWGName] = dwgDocumentSettings;

            foreach (var dwgDocumentSetting in dwgDocumentSettings)
            {
                DataRow row = dataTable.NewRow();
                row[_columnNameRulePrefix] = dwgDocumentSetting.Prefix;
                row[_columnNameRuleParameter] = dwgDocumentSetting.PropertyName;
                row[_columnNameRuleSuffix] = dwgDocumentSetting.Suffix;
                row[_columnNameRuleSeparator] = dwgDocumentSetting.Separator;
                dataTable.Rows.Add(row);
            }

            _documentSettingsTables.Add(_documentTypeDWGName, dataTable);
        }

        #endregion data tables

        private void PopulateAvailableFilters()
        {
            _documentTypeNameDefaultList.Add(_documentTypePDFName);
            _documentTypeNameDefaultList.Add(_documentTypeDWGName);

            foreach (var documentType in _documentTypeNameDefaultList)
            {
                _documentSettingsDictionary.Add(documentType, []);
            }

            OnPropertyChanged(nameof(DocumentTypeNameDefaultList));
        }

        private void SetFilterToPDFSettings()
        {
            SelectedDocumentType = _documentTypePDFName;
        }

        /// <summary>
        /// Sets the selected DWG export scheme name from settings.
        /// </summary>
        private void SetSelectedDWGExportScheme()
        {
            if (_exportDataModel.Settings.DWGExportScheme == null || _exportDataModel.Settings.DWGExportScheme == "")
            {
                if (_dwgExportSchemeNameList.Count > 0)
                {
                    SelectedDWGExportSchemeName = _dwgExportSchemeNameList[0];
                }
            }
            else
            {
                if (_dwgExportSchemeNameList.Contains(_exportDataModel.Settings.DWGExportScheme))
                {
                    SelectedDWGExportSchemeName = _exportDataModel.Settings.DWGExportScheme;
                }
                else
                {
                    AddMessage("Retrieved DWG export scheme name not in list.", MessageTypes.Error);
                    if (_dwgExportSchemeNameList.Count > 0)
                    {
                        SelectedDWGExportSchemeName = _dwgExportSchemeNameList[0];
                    }
                }
            }
        }


        #region button underlying functions

        private bool CanMoveToTableDocumentSettings() => _dvAvailableParameters.Count > 0 && _dvAvailableParameters.Count > _dvDocumentSettings.Count;

        private bool CanMoveToTableParameterNames() => _dvDocumentSettings.Count > 0;

        private void MoveParameterToDocumentNameTable()
        {
            SynchronizeDocumentNameTable();

            foreach (Utils.DocumentSetting documentSetting in _documentSettingsDictionary[SelectedDocumentType])
            {
                if (documentSetting.PropertyName == SelectedParameter)
                {
                    AddMessage("Parameter already in document settings table.", MessageTypes.Error);
                    return;
                }
            }

            Utils.DocumentSetting newDocumentSetting = new(SelectedParameter);
            _documentSettingsDictionary[SelectedDocumentType].Add(newDocumentSetting);
            RefreshDocumentNameTable();
        }

        private void RemoveParameterFromDocumentNameTable()
        {
            SynchronizeDocumentNameTable();

            if (_selectedIndexDocumentNameSetting >= 0 && _selectedIndexDocumentNameSetting < _dvDocumentSettings.Count)
            {
                var selectedRow = _dvDocumentSettings[_selectedIndexDocumentNameSetting].Row;
                var parameterName = selectedRow[_columnNameRuleParameter].ToString();
                foreach (Utils.DocumentSetting documentSetting in _documentSettingsDictionary[SelectedDocumentType])
                {
                    if (documentSetting.PropertyName == parameterName)
                    {
                        _documentSettingsDictionary[SelectedDocumentType].Remove(documentSetting);
                        break;
                    }
                }
            }

            RefreshDocumentNameTable();
        }

        /// <summary>
        /// Refreshes the document name table after moving, adding or removing a parameter.
        /// </summary>
        private void RefreshDocumentNameTable()
        {
            DataTable dt = CreateEmptySettingsDataTable();
            foreach (var documentSetting in _documentSettingsDictionary[SelectedDocumentType])
            {
                DataRow row = dt.NewRow();
                row[_columnNameRulePrefix] = documentSetting.Prefix;
                row[_columnNameRuleParameter] = documentSetting.PropertyName;
                row[_columnNameRuleSuffix] = documentSetting.Suffix;
                row[_columnNameRuleSeparator] = documentSetting.Separator;
                dt.Rows.Add(row);
            }

            _documentSettingsTables[SelectedDocumentType].Clear();
            _documentSettingsTables[SelectedDocumentType] = dt;
            DataViewDocumentTypeSettings = new DataView(dt);
        }

        /// <summary>
        /// Synchronizes the document settings dictionary with values entered in the document name table.
        /// </summary>
        private void SynchronizeDocumentNameTable()
        {
            if (SelectedDocumentType == null || _documentSettingsTables[SelectedDocumentType].Rows.Count == 0)
            {
                return;
            }

            foreach (DataRow row in _documentSettingsTables[SelectedDocumentType].Rows)
            {
                string prefix = row[_columnNameRulePrefix].ToString();
                string suffix = row[_columnNameRuleSuffix].ToString();
                string separator = row[_columnNameRuleSeparator].ToString();
                string propertyName = row[_columnNameRuleParameter].ToString();

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

        private bool CanMoveUp(object parameter) => SelectedItemDocumentNameSetting != null &&
            SelectedIndexDocumentNameSetting > 0;

        private bool CanMoveDown(object parameter) => SelectedItemDocumentNameSetting != null &&
            SelectedIndexDocumentNameSetting < _documentSettingsDictionary[SelectedDocumentType].Count - 1;

        private void MoveUp(object parameter)
        {
            SynchronizeDocumentNameTable();

            int index = _documentSettingsDictionary[SelectedDocumentType].IndexOf(SelectedItemDocumentNameSetting);
            if (index > 0)
            {
                var item = _documentSettingsDictionary[SelectedDocumentType][index];
                _documentSettingsDictionary[SelectedDocumentType].RemoveAt(index);
                _documentSettingsDictionary[SelectedDocumentType].Insert(index - 1, item);
                RefreshDocumentNameTable();
            }

            if (parameter is DataGrid dataGrid)
            {
                SelectRowByIndex(dataGrid, index - 1);
            }
        }

        private void MoveDown(object parameter)
        {
            SynchronizeDocumentNameTable();

            int index = _documentSettingsDictionary[SelectedDocumentType].IndexOf(SelectedItemDocumentNameSetting);
            if (index < _documentSettingsDictionary[SelectedDocumentType].Count - 1)
            {
                var item = _documentSettingsDictionary[SelectedDocumentType][index];
                _documentSettingsDictionary[SelectedDocumentType].RemoveAt(index);
                _documentSettingsDictionary[SelectedDocumentType].Insert(index + 1, item);
                RefreshDocumentNameTable();
            }

            if (parameter is DataGrid dataGrid)
            {
                SelectRowByIndex(dataGrid, index + 1);
            }
        }

        /// <summary>
        /// The file path for the export settings file.
        /// Side effect: exports current settings to the given path on change.
        /// Equality guard handled automatically by [ObservableProperty].
        /// </summary>
        [ObservableProperty]
        private string _exportSettingsFilePath;

        partial void OnExportSettingsFilePathChanged(string value)
        {
            Dictionary<string, object> settingsDictionary = new()
            {
                { _documentTypePDFName, _documentSettingsDictionary[_documentTypePDFName] },
                { _documentTypeDWGName, _documentSettingsDictionary[_documentTypeDWGName] },
                { _dwgExportSchemeNameProperty, SelectedDWGExportSchemeName }
            };

            duHastNet.UI.PDFDWGExporterUI.Utils.SettingsExport.ExportSettingsToJson(
                filePath: value,
                settings: settingsDictionary,
                AddMessage: AddMessage);
        }

        /// <summary>
        /// The file path for the import settings file.
        /// Side effect: imports settings from the given path and repopulates all data tables on change.
        /// Equality guard handled automatically by [ObservableProperty].
        /// </summary>
        [ObservableProperty]
        private string _importSettingsFilePath;

        partial void OnImportSettingsFilePathChanged(string value)
        {
            Dictionary<string, string> settingsDictionary = Utils.SettingsImport.ImportSettingsFromJson(
                filePath: value,
                AddMessage: AddMessage
            );

            if (settingsDictionary != null)
            {
                var missingKeys = new List<string>();
                var values = new Dictionary<string, object>();

                foreach (var key in new[] { _documentTypePDFName, _documentTypeDWGName, _dwgExportSchemeNameProperty })
                {
                    if (settingsDictionary.TryGetValue(key, out var settingsValue))
                    {
                        values[key] = settingsValue;
                    }
                    else
                    {
                        missingKeys.Add(key);
                    }
                }

                if (missingKeys.Count != 0)
                {
                    AddMessage($"Settings file is missing required keys: {string.Join(", ", missingKeys)}", MessageTypes.Error);
                    return;
                }

                _documentSettingsTables.Clear();
                PopulatePDFSettingsDataTable();
                PopualateDWGSettingsDataTable();
                SetSelectedDWGExportScheme();
                SetFilterToPDFSettings();
            }
        }

        /// <summary>
        /// Updates the settings in the export data model and closes the window.
        /// </summary>
        private void SaveSettingsAndClose(object window)
        {
            SynchronizeDocumentNameTable();

            _exportDataModel.Settings.PDFRenameString = Utils.SettingsStringParser.ConvertSettingsToPDFString(_documentSettingsDictionary[_documentTypePDFName]);
            _exportDataModel.Settings.DWGRenameString = Utils.SettingsStringParser.ConvertSettingsToDwgString(_documentSettingsDictionary[_documentTypeDWGName]);
            _exportDataModel.Settings.DWGExportScheme = SelectedDWGExportSchemeName;

            if (window is Window w)
            {
                w.Close();
            }
        }

        /// <summary>
        /// Clears the selection in the document naming table.
        /// Used when the document type is changed.
        /// </summary>
        public void ClearSelection()
        {
            SelectedItemDocumentNameSetting = null;
            SelectedIndexDocumentNameSetting = -1;
        }

        /// <summary>
        /// Selects the current row in the data grid by index.
        /// </summary>
        public static void SelectRowByIndex(DataGrid dataGrid, int rowIndex)
        {
            if (rowIndex < 0 || rowIndex >= dataGrid.Items.Count) return;

            DataRowView rowView = dataGrid.Items[rowIndex] as DataRowView;
            if (rowView != null)
            {
                dataGrid.SelectedItem = rowView;
                dataGrid.ScrollIntoView(rowView);
                dataGrid.UpdateLayout();
            }

            DataGridRow row = (DataGridRow)dataGrid.ItemContainerGenerator.ContainerFromItem(rowView);
            row?.Focus();
        }

        #endregion button underlying functions

        /// <summary>
        /// Constructor for the SettingsViewModel class.
        /// </summary>
        public SettingsViewModel(
            Models.ExportDataModel exportDataModel,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {
            _exportDataModel = exportDataModel;
            GlobalMessageViewModel = globalMessageViewModel;
            _messageStore = messageStore;

            RegisterChild(GlobalMessageViewModel);

            _documentSettingsTables = [];
            _documentSettingsDictionary = [];

            PopulateParameterDataTable();
            PopulateAvailableFilters();
            PopulateDWGExportSchemeNameList(_exportDataModel.DWGExportSchemeNames);
            PopulatePDFSettingsDataTable();
            PopualateDWGSettingsDataTable();

            _moveParameterToDocumentNameTableCommand = new RelayCommand(
                MoveParameterToDocumentNameTable,
                CanMoveToTableDocumentSettings
            );

            _removeParameterFromDocumentNameTableCommand = new RelayCommand(
                RemoveParameterFromDocumentNameTable,
                CanMoveToTableParameterNames
            );

            _moveUpCommand = new RelayCommand<object>(
                MoveUp,
                CanMoveUp
            );

            _moveDownCommand = new RelayCommand<object>(
                MoveDown,
                CanMoveDown
            );

            _saveAndCloseCommand = new RelayCommand<object>(
                SaveSettingsAndClose,
                _ => true
            );

            SetSelectedDWGExportScheme();

            // SetFilterToPDFSettings triggers OnSelectedDocumentTypeChanged which sets DataViewDocumentTypeSettings
            // — called last as it triggers a view change
            SetFilterToPDFSettings();
        }
    }
}