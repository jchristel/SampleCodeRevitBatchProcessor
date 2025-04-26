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


using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;

namespace duHastNet.UI.PDFDWGExporterUI.ViewModels
{
    public class SettingsViewModel : ViewModelBase
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
        /// default view of the data table containing PDF naming settings
        /// </summary>
        private DataTable _dtDocumentSettingsPDF;

        /// <summary>
        /// default view of the data table containing DWG naming settings
        /// </summary>
        private DataTable _dtDocumentSettingsDWG;

        /// <summary>
        ///  default view of the data table containing document settings
        /// </summary>
        private DataView _dvDocumentSettings;


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
                OnPropertyChanged(nameof(SelectedDocumentType));
            }
        }

        #endregion document type filter

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
                }
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
                _dtDocumentSettingsPDF = dataTable;
                //setup a new data view based on the table created
                //this will also trigger an on property changed event
                DataViewDocumentTypeSettings = new DataView(dataTable);

                // get out of the function
                return;
            }

            //parse the settings string and add the values
            List<Utils.DocumentSetting> pdfDocumentSettings = Utils.SettingsStringParser.ParsePdfSettingsString(_exportDataModel.Settings.PDFRenameString);

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
            _dtDocumentSettingsPDF = dataTable;

            //setup a new data view based on the table created
            //this will also trigger an on property changed event
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
                _dtDocumentSettingsDWG = dataTable;
                // do not set the data view here, as this will be done in the populateAvailableFilters function
                //and the default view will be set to the pdf settings table
                // get out of the function
                return;
            }

            //parse the settings string and add the values
            List<Utils.DocumentSetting> dwgDocumentSettings = Utils.SettingsStringParser.ParseDwgSettingsString(_exportDataModel.Settings.DWGRenameString);
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
            _dtDocumentSettingsDWG = dataTable;

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
        /// Constructor for the SettingsViewModel class.
        /// </summary>
        /// <param name="globalMessageViewModel"></param>
        /// <param name="messageStore"></param>
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

            //populate the data table containing the available parameters
            populateParameterDataTable();

            //check if the current settings contain a dwg or pdf settings string
            //and set up the data tables accordingly
            populatePDFSettingsDataTable();
            popualateDWGSettingsDataTable();

            //populate the available filters list ( PDF and DWG)
            populateAvailableFilters();

            //set the filter to display pdf settings by default
            //this will be trigger a view change to show the selected data table
            setFilterToPDFSettings();

            
            //set up all commands:
            //push in
            //push out
            //push up
            //push down
            //save and exit
            //cancel and exit
        }
    }
}
