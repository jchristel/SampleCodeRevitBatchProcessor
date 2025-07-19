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


using duHastNet.UI.CustomControls;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows;
using System.Windows.Input;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public class DocumentSelectionViewModel : ViewModelBase, INotifyDataErrorInfo
    {
        /// <summary>
        /// Global message view model for displaying messages to the user
        /// </summary>
        public duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// errors view model used for data validation ( export directory )
        /// </summary>
        private readonly duHastNet.Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        //property to check if there are any errors
        public bool HasErrors => _errorsViewModel.HasErrors;

        // event handler for errors changed
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged
        {
            add { _errorsViewModel.ErrorsChanged += value; }
            remove { _errorsViewModel.ErrorsChanged -= value; }
        }

        /// <summary>
        /// message store for storing messages
        /// </summary>
        private readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;

        /// <summary>
        /// View model managing the view selection data grid.
        /// </summary>
        public duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels.ViewSelectionDataGridViewModel ViewSelectionDataGridViewModel { get; }

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
        /// command to save the settings and close the window
        /// </summary>
        private readonly duHastNet.Utils.WPF.Commands.RelayCommand _saveAndCloseCommand;
        public ICommand SaveAndCloseCommand { get { return _saveAndCloseCommand; } }


        #region event handlers

        /// <summary>
        /// On window closing, unsubscribe from the event to prevent memory leaks
        /// </summary>
        public override void OnClosing()
        {

            // Unsubscribe from the event to prevent memory leaks
            GlobalMessageViewModel?.Dispose();

            //unsubscribe from errors changed event
            _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;

            base.OnClosing();
        }

        #endregion event handlers

        #region print set filter

        // Field to return a default list of print set  names
        private readonly List<string> _printSetNamesDefaultList = [];

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

                //store print set in settings
                _sheetsDataModel.Settings.Printset = value;

                // Update the data grid selection
                ViewSelectionDataGridViewModel.UpdateSheetSelectionByPrintSet(value);

                //update UI
                OnPropertyChanged(nameof(SelectedPrintSet));
            }
        }

        /// <summary>
        /// set the print set at the end of the GUI ini phase
        /// </summary>
        private void SetPrintSetFilterFromSettings()
        {
            //set the filter to the value stored in settings
            //check if valid value
            if (_sheetsDataModel.Settings.Printset == null)
            {
                AddMessage($"No valid print set in settings. Defaulting to {Models.Constants.DefaultPrintSetName}", messageType: MessageTypes.Error);
                SelectedPrintSet = Models.Constants.DefaultPrintSetName;
                //update the print set in settings
                _sheetsDataModel.Settings.Printset = Models.Constants.DefaultPrintSetName;
            }
            //check if print set still exists in model
            else if (_printSetNamesDefaultList.Contains(_sheetsDataModel.Settings.Printset))
            {
                //set the print set and mark sheets belonging to it
                SelectedPrintSet = _sheetsDataModel.Settings.Printset;
            }
            else
            {
                //print set no longer exists in the model...go with default option
                AddMessage($"Print set in settings no longer exists in file. Defaulting to {Models.Constants.DefaultPrintSetName}", messageType: MessageTypes.Error);
                SelectedPrintSet = Models.Constants.DefaultPrintSetName;
                //update the print set in settings
                _sheetsDataModel.Settings.Printset = Models.Constants.DefaultPrintSetName;
            }
        }

        #endregion print set filter


        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType)
        {
            _messageStore.SetCurrentMessage(message, messageType);
        }


        /// <summary>
        /// updates the default print set list with default value and any print sets in the sheet data model
        /// </summary>
        private void PopulateAvailablePrintSets()
        {
            //clear just in case
            _printSetNamesDefaultList.Clear();

            //populate the available filters list with print set names
            //add the default (None)
            _printSetNamesDefaultList.Add(Models.Constants.DefaultPrintSetName);

            // add from model
            if (_sheetsDataModel.PrintSets != null && _sheetsDataModel.PrintSets.Count > 0)
            {
                foreach (Models.RevitPrintSet pSet in _sheetsDataModel.PrintSets)
                {
                    _printSetNamesDefaultList.Add(pSet.Name);
                }
            }

            // trigger the property changed event
            OnPropertyChanged(nameof(PrintSetNamesDefaultList));
        }

        #region export types

        //three way control setting the operation modus
        private ThreeWaySwitch.SwitchState _exportTypes;

        /// <summary>
        /// property containing the three possible export modi
        /// </summary>
        public ThreeWaySwitch.SwitchState ExportTypes
        {
            get => _exportTypes;
            set
            {
                if (_exportTypes != value)
                {
                    _exportTypes = value;

                    if (_exportTypes == ThreeWaySwitch.SwitchState.Left)
                    {
                        ExportButtonText = $"Export {Models.Constants.ExportModusPDF}s";
                        _sheetsDataModel.Settings.ExportModus = Models.Constants.ExportModusPDF;
                    }
                    else if (_exportTypes == ThreeWaySwitch.SwitchState.Centre)
                    {
                        ExportButtonText = $"Export {Models.Constants.ExportModusDWG}s";
                        _sheetsDataModel.Settings.ExportModus = Models.Constants.ExportModusDWG;
                    }
                    else
                    {
                        ExportButtonText = $"Export {Models.Constants.ExportModusPDFandDWG}s";
                        _sheetsDataModel.Settings.ExportModus = Models.Constants.ExportModusPDFandDWG;
                    }

                    OnPropertyChanged(nameof(ExportTypes));
                }
            }
        }
        #endregion export types

        #region button underlying functions

        //default button text for export mode
        string _exportButtonText = $"Export {Models.Constants.ExportModusPDF}s";

        //button text for export button
        public string ExportButtonText
        {
            get => _exportButtonText;
            set
            {
                _exportButtonText = value;
                OnPropertyChanged(nameof(ExportButtonText));
            }
        }

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


                    _errorsViewModel.ClearErrors(nameof(ExportSheetsFilePath));

                    // check if the file path is valid, if not add an error
                    if (string.IsNullOrEmpty(value))
                    {
                        // set the data path to invalid
                        ExportDirectoryPathValid = false;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.AddError(nameof(ExportSheetsFilePath), "Export path path cannot be empty");
                    }
                    else if (!System.IO.Directory.Exists(value))
                    {
                        // set the data path to invalid
                        ExportDirectoryPathValid = false;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.AddError(nameof(ExportSheetsFilePath), "Export path does not exist");
                    }
                    else
                    {
                        // set the data path to valid
                        ExportDirectoryPathValid = true;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.ClearErrors(nameof(ExportSheetsFilePath));

                        //save in settings
                        _sheetsDataModel.Settings.ExportFolderPath = value;
                    }


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


            //update the column ids in settings.
            // clear lisr first
            _sheetsDataModel.Settings.ColumnIds.Clear();
            foreach (var columnId in ViewSelectionDataGridViewModel.ColumnDefinitions)
            {
                _sheetsDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            //save settings to file is done in the main window close event
            duHastNet.UI.PDFDWGExporterSelectionUI.Utils.SettingsUtils.SaveSettings(
                settings: _sheetsDataModel.Settings,
                AddMessage: AddMessage);

            if (window is Window w)
            {
                w.Close(); // Closes the window
            }
        }

        private void LoadSettings()
        {
            //load settings first
            var settings = duHastNet.UI.PDFDWGExporterSelectionUI.Utils.SettingsUtils.LoadSettings(AddMessage: AddMessage);

            //cant simply replace the settings object in the data model...since it is used else where....need to update instead
            _sheetsDataModel.Settings.UpdateSettingsFromSettings(settings);
        }


        /// <summary>
        /// Set the export type selector depending on string from settings
        /// </summary>
        private void SetExportTypeFromSettings()
        {
            string exportType = _sheetsDataModel.Settings.ExportModus;
            //check if dwg modus
            if (exportType == Models.Constants.ExportModusDWG)
            {
                ExportTypes = ThreeWaySwitch.SwitchState.Centre;
            }
            //check if pdf and dwg
            else if (exportType == Models.Constants.ExportModusPDFandDWG)
            {
                ExportTypes = ThreeWaySwitch.SwitchState.Right;
            }
            //assume it is pdf
            else
            {
                ExportTypes = ThreeWaySwitch.SwitchState.Left;
            }
        }

        #endregion button underlying functions


        #region data validation

        private bool _exportDirectoryPathValid;
        public bool ExportDirectoryPathValid
        {
            get => _exportDirectoryPathValid;
            set
            {
                _exportDirectoryPathValid = value;
                // call ui update
                OnPropertyChanged(nameof(ExportDirectoryPathValid));
            }
        }

        /// <summary>
        /// Data validation for text input fields
        /// </summary>
        /// <param name="propertyName">The name of the property of which to get any errors, if they exist, for.</param>
        /// <returns></returns>
        /// <exception cref="NotImplementedException"></exception>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }


        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            // The ErrorsChanged event will be automatically raised through the interface
            OnPropertyChanged(nameof(HasErrors));
            OnPropertyChanged(nameof(ExportDirectoryPathValid));

            // Trigger the command to re-evaluate its CanExecute state
            _saveAndCloseCommand?.RaiseCanExecuteChanged();
        }

        #endregion data validation

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

            //store the message store
            _messageStore = messageStore;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;

            //initialize the errors view model
            _errorsViewModel = new duHastNet.Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //load settings first
            LoadSettings();

            //set up the views data model
            ViewSelectionDataGridViewModel = new ViewSelectionDataGridViewModel(_sheetsDataModel);

            //save and exit
            //only if there are no errors
            _saveAndCloseCommand = new duHastNet.Utils.WPF.Commands.RelayCommand(
                SaveSettingsAndClose,
                parameter => !HasErrors // Only enabled when there are no errors
            );

            //set the export file path from settings:
            ExportSheetsFilePath = _sheetsDataModel.Settings.ExportFolderPath;

            // set the default export operation from the settings
            SetExportTypeFromSettings();

            //populate the available print set list from the model
            PopulateAvailablePrintSets();

            //set the filter to display sheets selected depending on print exports set
            //this will be trigger a view change to show the selected data table, hence last thing in the constructor
            SetPrintSetFilterFromSettings();

        }
    }
}
