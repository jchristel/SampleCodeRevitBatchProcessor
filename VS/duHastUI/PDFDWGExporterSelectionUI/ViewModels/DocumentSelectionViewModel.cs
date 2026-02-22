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


using CommunityToolkit.Mvvm.Input;
using duHastNet.UI.CustomControls;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows;
using System.Windows.Documents;
using System.Windows.Input;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public partial class DocumentSelectionViewModel : AppViewModelBase, INotifyDataErrorInfo
    {
        /// <summary>
        /// Global message view model for displaying messages to the user
        /// </summary>
        public GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// errors view model used for data validation ( export directory )
        /// </summary>
        private readonly ErrorsViewModel _errorsViewModel;

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
        private readonly MessageStore _messageStore;

        /// <summary>
        /// store the navigation store for the application
        /// </summary>
        private readonly NavigationStore _navigationStore;

        /// <summary>
        /// store the state store for the application
        /// </summary>
        private readonly StateStore _stateStore;

        /// <summary>
        /// View model managing the view selection data grid.
        /// </summary>
        public ViewSelectionDataGridViewModel ViewSelectionDataGridViewModel { get; }

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
        private readonly RelayCommand _saveAndCloseCommand;

        private readonly Commands.PrintSetDeleteCommand _printSetDeleteCommand;

        private readonly Commands.PrintSetUpdateCommand _printSetUpdateCommand;

        private readonly Commands.PrintSetDuplicateCommand _printSetDuplicateCommand;

        public ICommand SaveAndCloseCommand { get { return _saveAndCloseCommand; } }

        // Expose command objects directly (not as ICommand) so XAML can bind to generated DeleteCommand property
        public Commands.PrintSetDeleteCommand PrintSetDeleteCommand { get { return _printSetDeleteCommand; } }
        public Commands.PrintSetUpdateCommand PrintSetUpdateCommand { get { return _printSetUpdateCommand; } }
        public Commands.PrintSetDuplicateCommand PrintSetDuplicateCommand { get { return _printSetDuplicateCommand; } }


        #region event handlers

        /// <summary>
        /// On window closing, perform UI-related cleanup
        /// </summary>
        public override void OnClosing()
        {
            System.Diagnostics.Debug.WriteLine("DocumentSelectionViewModel.OnClosing() called");

            // Event cleanup now handled by DisposeManaged()
            // Call base to handle registered child ViewModels
            base.OnClosing();
        }

        /// <summary>
        /// Dispose of managed resources including event subscriptions
        /// </summary>
        public override void Dispose()
        {
            System.Diagnostics.Debug.WriteLine("DocumentSelectionViewModel.DisposeManaged() called");

            // Unsubscribe from events to prevent memory leaks
            if (_errorsViewModel != null)
            {
                _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;
            }

            if (_sheetsDataModel != null)
            {
                _sheetsDataModel.PropertyChanged -= Model_PropertyChanged;
            }

            // Note: GlobalMessageViewModel and ViewSelectionDataGridViewModel are registered
            // as children, so they will be automatically disposed by base.Dispose()

            base.Dispose();
        }

        #endregion event handlers

        #region print set filter

        // Field to return a default list of print set  names
        private ObservableCollection<string> _printSetNamesDefaultList = new ObservableCollection<string>();

        // Property to expose the default list of print sets
        public ObservableCollection<string> PrintSetNamesDefaultList
        {
            get => _printSetNamesDefaultList;
            set
            {
                _printSetNamesDefaultList = value;
                OnPropertyChanged(nameof(PrintSetNamesDefaultList));
            }
        }


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
        /// just setting it to None to avoid filtering issues
        /// </summary>
        private void SetPrintSetFilterFromSettings()
        {
            SelectedPrintSet = Models.Constants.DefaultPrintSetName;
            //update the print set in settings
            _sheetsDataModel.Settings.Printset = Models.Constants.DefaultPrintSetName;

        }


        #endregion print set filter

        #region schedule filter

        // Field to return a default list of print set  names
        private readonly List<string> _sheetScheduleNamesDefaultList = new List<string>();

        // Property to expose the default list of print sets
        public List<string> SheetScheduleNamesDefaultList => _sheetScheduleNamesDefaultList;

        // field to store the selected schedule set
        private string _selectedScheduleSet;
        public string SelectedScheduleSet
        {
            get => _selectedScheduleSet;
            set
            {
                _selectedScheduleSet = value;

                //store print set in settings
                _sheetsDataModel.Settings.Schedule = value;

                // Update the data grid selection
                ViewSelectionDataGridViewModel.UpdateSheetSelectionBySchedule(value);

                //update UI
                OnPropertyChanged(nameof(SelectedScheduleSet));
            }
        }

        /// <summary>
        /// set the schedule at the end of the GUI ini phase
        /// just setting it to None to avoid filtering issues
        /// </summary>
        private void SetSheetSetScheduleFilterFromSettings()
        {
            SelectedScheduleSet = Models.Constants.DefaultPrintSetName;
            //update the print set in settings
            _sheetsDataModel.Settings.Schedule = Models.Constants.DefaultPrintSetName;
        }

        #endregion schedule filter


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


        /// <summary>
        /// used to catch property changed events from the underlying model in order to update the ui
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Model_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check which property changed in the underlying model
            switch (e.PropertyName)
            {
                case Utils.PropertyChangedEventNames.DATA_MODEL_PRINTSETS_UPDATED:
                    //update rooms in the view model
                    PopulateAvailablePrintSets();
                    break;

                // Add more cases for other properties as needed

                default:
                    // Handle changes for properties not explicitly handled
                    break;
            }
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
                    //only add if not marked for deletion
                    if (pSet.UpdateAction != Models.PrintSetUpdateType.Delete)
                    {
                        _printSetNamesDefaultList.Add(pSet.Name);
                    }
                }
            }

            // trigger the property changed event
            OnPropertyChanged(nameof(PrintSetNamesDefaultList));
        }


        /// <summary>
        /// update the default schedules list with the default value and any schedules in the data model
        /// </summary>
        private void PopulateAvailableSchedules()
        {
            //clear just ion case
            _sheetScheduleNamesDefaultList.Clear();

            //populate the available filters list with print set names
            //add the default (None)
            _sheetScheduleNamesDefaultList.Add(Models.Constants.DefaultPrintSetName);

            // add from model
            if (_sheetsDataModel.Schedules != null && _sheetsDataModel.Schedules.Count > 0)
            {
                foreach (Models.RevitSchedule rSchedule in _sheetsDataModel.Schedules)
                {
                    _sheetScheduleNamesDefaultList.Add(rSchedule.Name);
                }
            }

            // trigger the property changed event
            OnPropertyChanged(nameof(SheetScheduleNamesDefaultList));
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
        /// Updates the settings and closes the window - Forces state save before closing
        /// </summary>
        private void SaveSettingsAndClose()
        {
            try
            {
                // Update the column ids in settings (existing logic)
                if (ViewSelectionDataGridViewModel?.ColumnDefinitions != null)
                {
                    _sheetsDataModel.Settings.ColumnIds.Clear();
                    foreach (var columnId in ViewSelectionDataGridViewModel.ColumnDefinitions)
                    {
                        _sheetsDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
                    }
                }

                // FORCE save current grid state to StateStore before getting states for settings
                if (ViewSelectionDataGridViewModel != null && _stateStore != null)
                {
                    try
                    {
                        var currentState = ViewSelectionDataGridViewModel.CreateStateFromViewModel();
                        if (currentState != null)
                        {
                            _stateStore.SaveState(ViewSelectionDataGridViewModel, currentState);
                            System.Diagnostics.Debug.WriteLine($"Forced save of grid state for {ViewSelectionDataGridViewModel.GetGridStateId()} before closing");
                        }
                    }
                    catch (Exception stateEx)
                    {
                        System.Diagnostics.Debug.WriteLine($"Error forcing state save: {stateEx.Message}");
                        AddMessage($"Warning: Could not save grid state: {stateEx.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                    }
                }

                // Get states from StateStore for settings persistence
                var statesForSettings = _stateStore.GetStatesForSettings();

                // Update the settings with the grid states
                _sheetsDataModel.Settings.NavigationStates = statesForSettings;

                // Save the application settings
                duHastNet.UI.PDFDWGExporterSelectionUI.Utils.SettingsUtils.SaveSettings(
                    settings: _sheetsDataModel.Settings,
                    AddMessage: AddMessage);

                // Close the window
                Application.Current.MainWindow?.Close();
            }
            catch (Exception ex)
            {
                AddMessage($"Error saving settings: {ex.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        private void LoadSettings()
        {
            //load settings first
            var settings = duHastNet.UI.PDFDWGExporterSelectionUI.Utils.SettingsUtils.LoadSettings(AddMessage: AddMessage);

            //cant simply replace the settings object in the data model...since it is used else where....need to update instead
            _sheetsDataModel.Settings.UpdateSettingsFromSettings(settings);

            // Load StateStore states if they exist
            if (settings.NavigationStates != null && settings.NavigationStates.Count > 0)
            {
                // Create a factory for DataGridState instances
                _stateStore.LoadStatesFromSettings(settings.NavigationStates, () => new DataGridState());
                System.Diagnostics.Debug.WriteLine($"Loaded {settings.NavigationStates.Count} states from settings into StateStore");
            }
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
            if (_saveAndCloseCommand != null)
            {
                _saveAndCloseCommand.NotifyCanExecuteChanged();
            }
        }

        #endregion data validation


        /// <summary>
        /// Constructor for the DocumentSelectionViewModel class.
        /// </summary>
        /// <param name="sheetDataModel">The sheet data model</param>
        /// <param name="navigationStore">Navigation store for ViewModel management</param>
        /// <param name="stateStore">State store for grid state persistence</param>
        /// <param name="globalMessageViewModel">Global message view model</param>
        /// <param name="messageStore">Message store</param>
        public DocumentSelectionViewModel(
            Models.SheetsDataModel sheetDataModel,
            duHastNet.Utils.WPF.Stores.NavigationStore navigationStore,
            duHastNet.Utils.WPF.Stores.StateStore stateStore,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {

            //store the export data model
            _sheetsDataModel = sheetDataModel;

            //store the navigation store
            _navigationStore = navigationStore;

            //store the state store
            _stateStore = stateStore;

            //store the message store
            _messageStore = messageStore;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;

            // Register GlobalMessageViewModel for automatic cleanup
            RegisterChild(GlobalMessageViewModel);

            //initialize the errors view model
            _errorsViewModel = new duHastNet.Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //load settings first
            LoadSettings();

            //set up the views data model - now pass StateStore instead of NavigationStore
            ViewSelectionDataGridViewModel = new ViewSelectionDataGridViewModel(
                _sheetsDataModel,
                _stateStore        // Pass StateStore for state management
             );

            // Register the child so it gets cleaned up properly
            RegisterChild(ViewSelectionDataGridViewModel);

            //save and exit
            //only if there are no errors
            _saveAndCloseCommand = new RelayCommand(
                SaveSettingsAndClose,
                () => !HasErrors // Only enabled when there are no errors
            );

            //command to delete a print set
            _printSetDeleteCommand = new Commands.PrintSetDeleteCommand(
                this,
                _sheetsDataModel
                );
            // Register command for automatic cleanup
            RegisterChild(_printSetDeleteCommand);

            //command to update a print set
            _printSetUpdateCommand = new Commands.PrintSetUpdateCommand(
                this,
                _sheetsDataModel
                );
            // Register command for automatic cleanup
            RegisterChild(_printSetUpdateCommand);

            //command to duplicate a print set
            _printSetDuplicateCommand = new Commands.PrintSetDuplicateCommand(
                this,
                _sheetsDataModel
                );
            // Register command for automatic cleanup
            RegisterChild(_printSetDuplicateCommand);

            //set the export file path from settings:
            ExportSheetsFilePath = _sheetsDataModel.Settings.ExportFolderPath;

            // set the default export operation from the settings
            SetExportTypeFromSettings();

            //populate the available print set list from the model
            PopulateAvailablePrintSets();

            //populate available schedule names from the model
            PopulateAvailableSchedules();

            //set the filter to display sheets selected depending on print exports set
            //this will be trigger a view change to show the selected data table, hence last thing in the constructor
            SetPrintSetFilterFromSettings();

            //set the filter to select sheets from schedule ( in theory only one, print set or schedule ) should have a 
            //selection 
            SetSheetSetScheduleFilterFromSettings();

            // subscribe to underlying model changes
            // required to update the print set list if changes occur
            _sheetsDataModel.PropertyChanged += Model_PropertyChanged;
        }
    }
}