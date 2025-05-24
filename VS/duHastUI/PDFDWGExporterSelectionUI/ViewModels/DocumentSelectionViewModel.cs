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
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Data;
using System.Net.NetworkInformation;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
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
        private readonly Models.SheetsDataModel _sheetsDataModel;

        /// <summary>
        /// Settings build in UI and to be returned to caller
        /// </summary>
        public Utils.Settings Settings
        {
            get { return _sheetsDataModel.Settings; }

        }

        /// <summary>
        ///  default view of the data table containing sheets for selection
        /// </summary>
        private DataView _dvSheets;

        //command to update the view model if the column order changes
        public RelayCommand ColumnOrderChangedCommand { get; private set; }

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

        #region print set filter

        // Field to return a default list of print set  names
        private readonly List<string> _printSetNamesDefaultList = new List<string>();

        // Property to expose the default list of document type names
        public List<string> PrintSetNamesDefaultList => _printSetNamesDefaultList;

        // field to store the selected Revit print set
        private string _selectedPrintSet;
        public string SelectedPrintSet
        {
            get => _selectedPrintSet;
            set
            {
                _selectedPrintSet = value;

                //set the data view to the pdf settings table
                //this will also clear the selection in the document name table
                //DataViewDocumentTypeSettings = new DataView(_documentSettingsTables[_selectedPrintSet]);

                //update UI
                OnPropertyChanged(nameof(SelectedPrintSet));
            }
        }

        /// <summary>
        /// set the print set at the end of the GUI ini phase
        /// </summary>
        private void setPrintSetFilter()
        {
            //set the filter to display pdf settings by default
            //this will be trigger a view change to show the selected data table
            //SelectedPrintSet = _documentTypePDFName;
        }

        #endregion print set filter

        #region data views

        /// <summary>
        /// binding in xaml property to the default view of the available parameters collection
        /// </summary>
        public DataView DataViewSheets
        {
            get => _dvSheets;
            private set
            {
                _dvSheets = value;
                OnPropertyChanged(nameof(DataViewSheets));
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
        /// Create an empty data table with the default columns for the sheets  (number and name)
        /// </summary>
        /// <returns>An empty data table.</returns>
        private DataTable CreateEmptySheetsDataTable()
        {
            //create an empty data table
            DataTable dataTable = new DataTable();
            //add the default columns
            dataTable.Columns.Add(Models.Constants.ColumnHeaderSheetNumber);
            dataTable.Columns.Add(Models.Constants.ColumnHeaderSheetName);
            
            return dataTable;
        }

        
        /// <summary>
        /// populate the data table containing the dwg name settings
        /// </summary>
        private void popualateSheetsDataTable()
        {
            //populate the data table containing the dwg settings
            //check if the current settings contain a  dwg settings string
            //and set up the data tables accordingly

            //set up an empty table
            DataTable dataTable = CreateEmptySheetsDataTable();

            //TODO:

            ////check if the current settings contain a dwg settings string
            //if (_sheetsDataModel.Settings.DWGRenameString == null || _sheetsDataModel.Settings.DWGRenameString == "")
            //{
            //    //store the table in global
            //    _documentSettingsTables.Add(_documentTypeDWGName, dataTable);
            //    // do not set the data view here, as this will be done in the populateAvailableFilters function
            //    //and the default view will be set to the pdf settings table
            //    // get out of the function
            //    return;
            //}

            ////parse the settings string and add the values
            //ObservableCollection<Utils.DocumentSetting> dwgDocumentSettings = Utils.SettingsStringParser.ParseDwgSettingsString(
            //    _sheetsDataModel.Settings.DWGRenameString,
            //    _sheetsDataModel.ParameterNames
            //);

            ////update the global dictionary with the parsed values
            //_documentSettingsDictionary[_documentTypeDWGName] = dwgDocumentSettings;

            ////update the data table with the parsed values
            //foreach (var dwgDocumentSetting in dwgDocumentSettings)
            //{
            //    // Add a row per room
            //    DataRow row = dataTable.NewRow();
            //    row[_columnNameRulePrefix] = dwgDocumentSetting.Prefix;
            //    row[_columnNameRuleParameter] = dwgDocumentSetting.PropertyName;
            //    row[_columnNameRuleSuffix] = dwgDocumentSetting.Suffix;
            //    row[_columnNameRuleSeparator] = dwgDocumentSetting.Separator;
            //    // Add the row to the data table
            //    dataTable.Rows.Add(row);
            //}

            ////store the table in global
            //_documentSettingsTables.Add(_documentTypeDWGName, dataTable);

            // do not set the data view here, as this will be done in the populateAvailableFilters function
            //and the default view will be set to the pdf settings table
            // get out of the function
            return;

        }

        #endregion data tables

        private void populateAvailablePrintSets()
        {
            //clear just in case
            _printSetNamesDefaultList.Clear();

            //populate the available filters list with print set names
            _printSetNamesDefaultList.Add(Models.Constants.DefaultPrintSetName);

            // trigger the property changed event
            OnPropertyChanged(nameof(PrintSetNamesDefaultList));
        }

        


        #region button underlying functions

        /// <summary>
        /// The file path for the exports to be saved to
        /// </summary>
        private string _selectedSheetsExportFilePath;

        /// <summary>
        /// property handling file path changes
        /// </summary>
        public string ExportSheetsFilePath
        {
            get => _selectedSheetsExportFilePath;
            set
            {
                if (_selectedSheetsExportFilePath != value)
                {
                    _selectedSheetsExportFilePath = value;

                    //TODO:
                    //do something

                    OnPropertyChanged(nameof(ExportSheetsFilePath));
                }
            }
        }

        /// <summary>
        /// updates the settings in the export data model and closes the window
        /// </summary>
        /// <param name="window"></param>
        private void SaveSettingsAndClose(object window)
        {
            //TODO:
            //update settings and save to local app data

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
            //TODO:
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
            Models.SheetsDataModel sheetDataModel,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {

            //store the export data model
            _sheetsDataModel = sheetDataModel;
            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;
            //store the message store
            _messageStore = messageStore;

            //populate the available filters list ( PDF and DWG)
            populateAvailablePrintSets();

            //and set up sheets data table
            popualateSheetsDataTable();

            //set up all commands:
            // create the column order changed command
            ColumnOrderChangedCommand = new RelayCommand(OnColumnOrderChanged);



            ////push in
            //_moveParameterToDocumentNameTableCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
            //    MoveParameterToDocumentNameTable,
            //    CanMoveToTableDocumentSettings
            //);

            ////push out
            //_removeParameterFromDocumentNameTableCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
            //    RemoveParameterFromDocumentNameTable,
            //    CanMoveToTableParameterNames
            //);

            ////push up
            //_moveUpCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
            //    MoveUp,
            //    CanMoveUp
            //);

            ////push down
            //_moveDownCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
            //    MoveDown,
            //    CanMoveDown
            //);

            ////save and exit
            //_saveAndCloseCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
            //    SaveSettingsAndClose,
            //    (object parameter) => true //always enabled
            //);

            //set the filter to display sheets selected depending on print exports set
            //this will be trigger a view change to show the selected data table, hence last thing in the constructor
            setPrintSetFilter();
        }
    }
}
