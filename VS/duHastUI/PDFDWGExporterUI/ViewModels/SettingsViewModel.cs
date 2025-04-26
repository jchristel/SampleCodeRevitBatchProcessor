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
        public duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel? GlobalMessageViewModel { get; }

        /// <summary>
        /// message store for storing messages
        /// </summary>
        private readonly duHastNet.Utils.WPF.Stores.MessageStore? _messageStore;

        /// <summary>
        /// The data model for the export settings
        /// </summary>
        private readonly Models.ExportDataModel? _exportDataModel;

        /// <summary>
        /// Settings build in UI and to be returned to caller
        /// </summary>
        public Utils.Settings? Settings
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
        /// default view of the data table containing available parameters
        /// </summary>
        private DataTable _dtDocumentSettings;

        /// <summary>
        ///  default view of the data table containing document settings
        /// </summary>
        private DataView _dvDocumentSettings;


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

        // Field to return a default list of document type names
        private readonly List<string> _documentTypeNameDefaultList = new List<string>
        {
            "PDF",
            "DWG"
        };

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

        private void populateParameterDataTable()
        {
            //populate the data table containing the available parameters
            //check if the current settings contain a dwg or pdf settings string
            //and set up the data tables accordingly
        }

        private void populatePDFSettingsDataTable()
        {
            //populate the data table containing the pdf settings
            //check if the current settings contain a  pdf settings string
            //and set up the data tables accordingly
        }

        private void popualateDWGSettingsDataTable()
        {
            //populate the data table containing the dwg settings
            //check if the current settings contain a  dwg settings string
            //and set up the data tables accordingly
        }

        private void populateAvailableFilters()
        {
            //populate the available filters list ( PDF and DWG)
            //set the filter to display pdf settings by default
            //this will be trigger a view change to show the selected data table
        }

        private void setFilterToPDFSettings()
        {
            //set the filter to display pdf settings by default
            //this will be trigger a view change to show the selected data table
        }



        /// <summary>
        /// Constructor for the SettingsViewModel class.
        /// </summary>
        /// <param name="globalMessageViewModel"></param>
        /// <param name="messageStore"></param>
        public SettingsViewModel(
            Models.ExportDataModel? exportDataModel,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel? globalMessageViewModel, 
            duHastNet.Utils.WPF.Stores.MessageStore? messageStore
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
