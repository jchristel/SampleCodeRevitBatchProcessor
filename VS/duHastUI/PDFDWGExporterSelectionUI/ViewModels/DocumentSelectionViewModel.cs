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
using System.Windows.Input;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public partial class DocumentSelectionViewModel : AppViewModelBase, INotifyDataErrorInfo
    {
        /// <summary>
        /// Global message view model for displaying messages to the user.
        /// </summary>
        public GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// Errors view model used for data validation (export directory).
        /// </summary>
        private readonly ErrorsViewModel _errorsViewModel;

        //property to check if there are any errors
        public bool HasErrors => _errorsViewModel.HasErrors;

        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged
        {
            add { _errorsViewModel.ErrorsChanged += value; }
            remove { _errorsViewModel.ErrorsChanged -= value; }
        }

        /// <summary>
        /// Message store for storing messages.
        /// </summary>
        private readonly MessageStore _messageStore;

        /// <summary>
        /// Navigation store for the application.
        /// </summary>
        private readonly NavigationStore _navigationStore;

        /// <summary>
        /// State store for the application.
        /// </summary>
        private readonly StateStore _stateStore;

        /// <summary>
        /// View model managing the view selection data grid.
        /// </summary>
        public ViewSelectionDataGridViewModel ViewSelectionDataGridViewModel { get; }

        /// <summary>
        /// The data model for the export settings.
        /// </summary>
        private readonly Models.SheetsDataModel _sheetsDataModel;

        /// <summary>
        /// Settings built in UI and to be returned to caller.
        /// </summary>
        public Utils.Settings Settings => _sheetsDataModel.Settings;

        /// <summary>
        /// Command to save the settings and close the window.
        /// </summary>
        private readonly RelayCommand<Window> _saveAndCloseCommand;

        private readonly Commands.PrintSetDeleteCommand _printSetDeleteCommand;
        private readonly Commands.PrintSetUpdateCommand _printSetUpdateCommand;
        private readonly Commands.PrintSetDuplicateCommand _printSetDuplicateCommand;

        public ICommand SaveAndCloseCommand => _saveAndCloseCommand;

        // Expose command objects directly (not as ICommand) so XAML can bind to generated command properties
        public Commands.PrintSetDeleteCommand PrintSetDeleteCommand => _printSetDeleteCommand;
        public Commands.PrintSetUpdateCommand PrintSetUpdateCommand => _printSetUpdateCommand;
        public Commands.PrintSetDuplicateCommand PrintSetDuplicateCommand => _printSetDuplicateCommand;


        #region event handlers

        /// <summary>
        /// On window closing, perform UI-related cleanup.
        /// </summary>
        public override void OnClosing()
        {
            System.Diagnostics.Debug.WriteLine("DocumentSelectionViewModel.OnClosing() called");

            // Call base to handle registered child ViewModels
            base.OnClosing();
        }

        /// <summary>
        /// Dispose of managed resources including event subscriptions.
        /// </summary>
        public override void Dispose()
        {
            System.Diagnostics.Debug.WriteLine("DocumentSelectionViewModel.Dispose() called");

            if (_errorsViewModel != null)
            {
                _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;
            }

            if (_sheetsDataModel != null)
            {
                _sheetsDataModel.PropertyChanged -= Model_PropertyChanged;
            }

            // Note: GlobalMessageViewModel and ViewSelectionDataGridViewModel are registered
            // as children and will be automatically disposed by base.Dispose()
            base.Dispose();
        }

        #endregion event handlers

        #region print set filter

        // Backing collection mutated in place by PopulateAvailablePrintSets(); the property
        // notifies via OnPropertyChanged(nameof(PrintSetNamesDefaultList)) in that method.
        [ObservableProperty]
        private ObservableCollection<string> _printSetNamesDefaultList = new ObservableCollection<string>();

        /// <summary>
        /// The selected Revit print set.
        /// Side effects: updates settings and triggers data grid sheet selection.
        /// </summary>
        [ObservableProperty]
        private string _selectedPrintSet;

        partial void OnSelectedPrintSetChanged(string value)
        {
            _sheetsDataModel.Settings.Printset = value;
            ViewSelectionDataGridViewModel.UpdateSheetSelectionByPrintSet(value);
        }

        /// <summary>
        /// Sets the print set filter from settings at the end of the GUI init phase.
        /// </summary>
        private void SetPrintSetFilterFromSettings()
        {
            SelectedPrintSet = Models.Constants.DefaultPrintSetName;
            _sheetsDataModel.Settings.Printset = Models.Constants.DefaultPrintSetName;
        }

        #endregion print set filter

        #region schedule filter

        // Get-only: backing list is mutated in place by PopulateAvailableSchedules()
        private readonly List<string> _sheetScheduleNamesDefaultList = new List<string>();
        public List<string> SheetScheduleNamesDefaultList => _sheetScheduleNamesDefaultList;

        /// <summary>
        /// The selected schedule set.
        /// Side effects: updates settings and triggers data grid sheet selection.
        /// </summary>
        [ObservableProperty]
        private string _selectedScheduleSet;

        partial void OnSelectedScheduleSetChanged(string value)
        {
            _sheetsDataModel.Settings.Schedule = value;
            ViewSelectionDataGridViewModel.UpdateSheetSelectionBySchedule(value);
        }

        /// <summary>
        /// Sets the schedule filter from settings at the end of the GUI init phase.
        /// </summary>
        private void SetSheetSetScheduleFilterFromSettings()
        {
            SelectedScheduleSet = Models.Constants.DefaultPrintSetName;
            _sheetsDataModel.Settings.Schedule = Models.Constants.DefaultPrintSetName;
        }

        #endregion schedule filter


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


        /// <summary>
        /// Catches property changed events from the underlying model to update the UI.
        /// </summary>
        private void Model_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            switch (e.PropertyName)
            {
                case Utils.PropertyChangedEventNames.DATA_MODEL_PRINTSETS_UPDATED:
                    PopulateAvailablePrintSets();
                    break;

                default:
                    break;
            }
        }


        /// <summary>
        /// Updates the default print set list with the default value and any print sets in the sheet data model.
        /// </summary>
        private void PopulateAvailablePrintSets()
        {
            _printSetNamesDefaultList.Clear();
            _printSetNamesDefaultList.Add(Models.Constants.DefaultPrintSetName);

            if (_sheetsDataModel.PrintSets != null && _sheetsDataModel.PrintSets.Count > 0)
            {
                foreach (Models.RevitPrintSet pSet in _sheetsDataModel.PrintSets)
                {
                    if (pSet.UpdateAction != Models.PrintSetUpdateType.Delete)
                    {
                        _printSetNamesDefaultList.Add(pSet.Name);
                    }
                }
            }

            // Notify UI since the collection is mutated in place, not replaced
            OnPropertyChanged(nameof(PrintSetNamesDefaultList));
        }


        /// <summary>
        /// Updates the default schedules list with the default value and any schedules in the data model.
        /// </summary>
        private void PopulateAvailableSchedules()
        {
            _sheetScheduleNamesDefaultList.Clear();
            _sheetScheduleNamesDefaultList.Add(Models.Constants.DefaultPrintSetName);

            if (_sheetsDataModel.Schedules != null && _sheetsDataModel.Schedules.Count > 0)
            {
                foreach (Models.RevitSchedule rSchedule in _sheetsDataModel.Schedules)
                {
                    _sheetScheduleNamesDefaultList.Add(rSchedule.Name);
                }
            }

            OnPropertyChanged(nameof(SheetScheduleNamesDefaultList));
        }

        #region export types

        /// <summary>
        /// The three-way switch state representing the export mode (PDF / DWG / PDF+DWG).
        /// Side effects: updates ExportButtonText and settings export modus.
        /// Equality guard is handled automatically by [ObservableProperty].
        /// </summary>
        [ObservableProperty]
        private ThreeWaySwitch.SwitchState _exportTypes;

        partial void OnExportTypesChanged(ThreeWaySwitch.SwitchState value)
        {
            if (value == ThreeWaySwitch.SwitchState.Left)
            {
                ExportButtonText = $"Export {Models.Constants.ExportModusPDF}s";
                _sheetsDataModel.Settings.ExportModus = Models.Constants.ExportModusPDF;
            }
            else if (value == ThreeWaySwitch.SwitchState.Centre)
            {
                ExportButtonText = $"Export {Models.Constants.ExportModusDWG}s";
                _sheetsDataModel.Settings.ExportModus = Models.Constants.ExportModusDWG;
            }
            else
            {
                ExportButtonText = $"Export {Models.Constants.ExportModusPDFandDWG}s";
                _sheetsDataModel.Settings.ExportModus = Models.Constants.ExportModusPDFandDWG;
            }
        }

        #endregion export types

        #region button underlying functions

        /// <summary>
        /// Button text reflecting the current export mode.
        /// </summary>
        [ObservableProperty]
        private string _exportButtonText = $"Export {Models.Constants.ExportModusPDF}s";

        /// <summary>
        /// The directory path for exports.
        /// Side effects: validates path, updates error state and settings.
        /// Equality guard is handled automatically by [ObservableProperty].
        /// </summary>
        [ObservableProperty]
        private string _exportSheetsFilePath;

        partial void OnExportSheetsFilePathChanged(string value)
        {
            _errorsViewModel.ClearErrors(nameof(ExportSheetsFilePath));

            if (string.IsNullOrEmpty(value))
            {
                ExportDirectoryPathValid = false;
                _errorsViewModel.AddError(nameof(ExportSheetsFilePath), "Export path cannot be empty");
            }
            else if (!System.IO.Directory.Exists(value))
            {
                ExportDirectoryPathValid = false;
                _errorsViewModel.AddError(nameof(ExportSheetsFilePath), "Export path does not exist");
            }
            else
            {
                ExportDirectoryPathValid = true;
                _errorsViewModel.ClearErrors(nameof(ExportSheetsFilePath));
                _sheetsDataModel.Settings.ExportFolderPath = value;
            }
        }

        /// <summary>
        /// Updates the settings and closes the window. Forces state save before closing.
        /// </summary>
        private void SaveSettingsAndClose(Window window)
        {
            try
            {
                if (ViewSelectionDataGridViewModel?.ColumnDefinitions != null)
                {
                    _sheetsDataModel.Settings.ColumnIds.Clear();
                    foreach (var columnId in ViewSelectionDataGridViewModel.ColumnDefinitions)
                    {
                        _sheetsDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
                    }
                }

                // Force save current grid state to StateStore before getting states for settings
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

                var statesForSettings = _stateStore.GetStatesForSettings();
                _sheetsDataModel.Settings.NavigationStates = statesForSettings;

                duHastNet.UI.PDFDWGExporterSelectionUI.Utils.SettingsUtils.SaveSettings(
                    settings: _sheetsDataModel.Settings,
                    AddMessage: AddMessage);

                window?.Close();
            }
            catch (Exception ex)
            {
                AddMessage($"Error saving settings: {ex.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        private void LoadSettings()
        {
            var settings = duHastNet.UI.PDFDWGExporterSelectionUI.Utils.SettingsUtils.LoadSettings(AddMessage: AddMessage);
            _sheetsDataModel.Settings.UpdateSettingsFromSettings(settings);

            if (settings.NavigationStates != null && settings.NavigationStates.Count > 0)
            {
                _stateStore.LoadStatesFromSettings(settings.NavigationStates, () => new DataGridState());
                System.Diagnostics.Debug.WriteLine($"Loaded {settings.NavigationStates.Count} states from settings into StateStore");
            }
        }

        /// <summary>
        /// Sets the export type selector from the settings string.
        /// </summary>
        private void SetExportTypeFromSettings()
        {
            string exportType = _sheetsDataModel.Settings.ExportModus;
            if (exportType == Models.Constants.ExportModusDWG)
            {
                ExportTypes = ThreeWaySwitch.SwitchState.Centre;
            }
            else if (exportType == Models.Constants.ExportModusPDFandDWG)
            {
                ExportTypes = ThreeWaySwitch.SwitchState.Right;
            }
            else
            {
                ExportTypes = ThreeWaySwitch.SwitchState.Left;
            }
        }

        #endregion button underlying functions


        #region data validation

        /// <summary>
        /// Indicates whether the export directory path is valid.
        /// </summary>
        [ObservableProperty]
        private bool _exportDirectoryPathValid;

        /// <summary>
        /// Data validation for text input fields.
        /// </summary>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }

        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            OnPropertyChanged(nameof(HasErrors));
            OnPropertyChanged(nameof(ExportDirectoryPathValid));

            _saveAndCloseCommand?.NotifyCanExecuteChanged();
        }

        #endregion data validation


        /// <summary>
        /// Constructor for the DocumentSelectionViewModel class.
        /// </summary>
        /// <param name="sheetDataModel">The sheet data model.</param>
        /// <param name="navigationStore">Navigation store for ViewModel management.</param>
        /// <param name="stateStore">State store for grid state persistence.</param>
        /// <param name="globalMessageViewModel">Global message view model.</param>
        /// <param name="messageStore">Message store.</param>
        public DocumentSelectionViewModel(
            Models.SheetsDataModel sheetDataModel,
            duHastNet.Utils.WPF.Stores.NavigationStore navigationStore,
            duHastNet.Utils.WPF.Stores.StateStore stateStore,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {
            _sheetsDataModel = sheetDataModel;
            _navigationStore = navigationStore;
            _stateStore = stateStore;
            _messageStore = messageStore;

            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel);

            _errorsViewModel = new duHastNet.Utils.WPF.ViewModels.ErrorsViewModel();
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            LoadSettings();

            ViewSelectionDataGridViewModel = new ViewSelectionDataGridViewModel(
                _sheetsDataModel,
                _stateStore
             );
            RegisterChild(ViewSelectionDataGridViewModel);

            _saveAndCloseCommand = new RelayCommand<Window>(
                SaveSettingsAndClose,
                (window) => !HasErrors
            );

            _printSetDeleteCommand = new Commands.PrintSetDeleteCommand(this, _sheetsDataModel);
            RegisterChild(_printSetDeleteCommand);

            _printSetUpdateCommand = new Commands.PrintSetUpdateCommand(this, _sheetsDataModel);
            RegisterChild(_printSetUpdateCommand);

            _printSetDuplicateCommand = new Commands.PrintSetDuplicateCommand(this, _sheetsDataModel);
            RegisterChild(_printSetDuplicateCommand);

            // Setting ExportSheetsFilePath triggers OnExportSheetsFilePathChanged for validation
            ExportSheetsFilePath = _sheetsDataModel.Settings.ExportFolderPath;

            SetExportTypeFromSettings();
            PopulateAvailablePrintSets();
            PopulateAvailableSchedules();

            // These set filter state — called last as they trigger view changes
            SetPrintSetFilterFromSettings();
            SetSheetSetScheduleFilterFromSettings();

            _sheetsDataModel.PropertyChanged += Model_PropertyChanged;
        }
    }
}