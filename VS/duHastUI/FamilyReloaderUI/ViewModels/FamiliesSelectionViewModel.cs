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
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows;
using System.Windows.Input;

namespace duHastNet.UI.FamilyReloaderUI.ViewModels
{
    public partial class FamiliesSelectionViewModel : AppViewModelBase, INotifyDataErrorInfo
    {
        /// <summary>
        /// Global message view model for displaying messages to the user.
        /// </summary>
        public GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// Errors view model used for data validation (library directory path).
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
        /// View model managing the families selection data grid.
        /// </summary>
        public FamiliesSelectionDataGridViewModel FamiliesSelectionDataGridViewModel { get; }

        /// <summary>
        /// The data model for the families settings.
        /// </summary>
        private readonly Models.FamiliesDataModel _familiesDataModel;

        /// <summary>
        /// Command to save the settings and close the window.
        /// </summary>
        private RelayCommand? _saveAndCloseCommand;

        /// <summary>
        /// Command to refresh match status of families in the UI.
        /// </summary>
        private readonly Commands.RefreshFamilyFileMatchDataCommand _updateCommand;

        public ICommand? SaveAndCloseCommand => _saveAndCloseCommand;
        public Commands.RefreshFamilyFileMatchDataCommand UpdateCommand => _updateCommand;


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


        private void LoadSettings()
        {
            var settings = duHastNet.UI.FamilyReloaderUI.Utils.SettingsUtils.LoadSettings(AddMessage: AddMessage);
            _familiesDataModel.Settings.UpdateSettingsFromSettings(settings);

            if (settings.NavigationStates != null && settings.NavigationStates.Count > 0)
            {
                _stateStore.LoadStatesFromSettings(settings.NavigationStates, () => new DataGridState());
                System.Diagnostics.Debug.WriteLine($"Loaded {settings.NavigationStates.Count} states from settings into StateStore");
            }
        }

        #region observable properties

        /// <summary>
        /// The library directory path.
        /// Side effects: validates path, updates error state and settings.
        /// Equality guard handled automatically by [ObservableProperty].
        /// </summary>
        [ObservableProperty]
        private string _libraryFilePath;

        partial void OnLibraryFilePathChanged(string value)
        {
            _errorsViewModel.ClearErrors(nameof(LibraryFilePath));

            if (string.IsNullOrEmpty(value))
            {
                LibraryDirectoryPathValid = false;
                _errorsViewModel.AddError(nameof(LibraryFilePath), "Library path cannot be empty");
            }
            else if (!System.IO.Directory.Exists(value))
            {
                LibraryDirectoryPathValid = false;
                _errorsViewModel.AddError(nameof(LibraryFilePath), "Library path does not exist");
            }
            else
            {
                LibraryDirectoryPathValid = true;
                _errorsViewModel.ClearErrors(nameof(LibraryFilePath));
                _familiesDataModel.Settings.TargetDirectory = value;
            }
        }

        /// <summary>
        /// If true, only existing types will be reloaded.
        /// </summary>
        [ObservableProperty]
        private bool _updateExistingTypesOnly;

        /// <summary>
        /// If true, all family types will be loaded into the project.
        /// Side effect: updates settings.
        /// </summary>
        [ObservableProperty]
        private bool _loadAllFamilyTypes;

        partial void OnLoadAllFamilyTypesChanged(bool value)
        {
            _familiesDataModel.Settings.LoadAllFamilyTypesOnReload = value;
        }

        /// <summary>
        /// Indicates whether subdirectories are included in the search for matching families.
        /// Side effects: updates settings and triggers a refresh of the family match data.
        /// </summary>
        [ObservableProperty]
        private bool _includeSubDirectoriesInSearch;

        partial void OnIncludeSubDirectoriesInSearchChanged(bool value)
        {
            _familiesDataModel.Settings.IncludeSubdirectories = value;

            if (UpdateCommand != null)
            {
                UpdateCommand.Execute(null);
            }
        }

        #endregion observable properties

        #region data validation

        /// <summary>
        /// Indicates whether the library directory path is valid.
        /// </summary>
        [ObservableProperty]
        private bool _libraryDirectoryPathValid;

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
            OnPropertyChanged(nameof(LibraryDirectoryPathValid));

            _saveAndCloseCommand?.NotifyCanExecuteChanged();
        }

        #endregion data validation

        /// <summary>
        /// Custom closing logic. Unsubscribes from events before base cleanup.
        /// </summary>
        public override void OnClosing()
        {
            _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;

            // base handles GlobalMessageViewModel and FamiliesSelectionDataGridViewModel cleanup
            base.OnClosing();
        }

        public override void Dispose()
        {
            base.Dispose();
        }

        /// <summary>
        /// Saves settings and closes the window.
        /// </summary>
        private void SaveSettingsAndClose()
        {
            _familiesDataModel.Settings.ColumnIds.Clear();
            foreach (var columnId in FamiliesSelectionDataGridViewModel.ColumnDefinitions)
            {
                _familiesDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            if (FamiliesSelectionDataGridViewModel != null && _stateStore != null)
            {
                try
                {
                    var currentState = FamiliesSelectionDataGridViewModel.CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        _stateStore.SaveState(FamiliesSelectionDataGridViewModel, currentState);
                        System.Diagnostics.Debug.WriteLine($"Forced save of grid state for {FamiliesSelectionDataGridViewModel.GetGridStateId()} before closing");
                    }
                }
                catch (Exception stateEx)
                {
                    System.Diagnostics.Debug.WriteLine($"Error forcing state save: {stateEx.Message}");
                    AddMessage($"Warning: Could not save grid state: {stateEx.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
            }

            var statesForSettings = _stateStore.GetStatesForSettings();
            _familiesDataModel.Settings.NavigationStates = statesForSettings;

            Utils.SettingsUtils.SaveSettings(_familiesDataModel.Settings);
            Application.Current.MainWindow?.Close();
        }

        public FamiliesSelectionViewModel(
            Models.FamiliesDataModel familiesDataModel,
            duHastNet.Utils.WPF.Stores.NavigationStore navigationStore,
            duHastNet.Utils.WPF.Stores.StateStore stateStore,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {
            _familiesDataModel = familiesDataModel;
            _navigationStore = navigationStore;
            _stateStore = stateStore;
            _messageStore = messageStore;

            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel);

            _errorsViewModel = new duHastNet.Utils.WPF.ViewModels.ErrorsViewModel();
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            LoadSettings();

            // Setting LibraryFilePath triggers OnLibraryFilePathChanged for validation
            LibraryFilePath = _familiesDataModel.Settings.TargetDirectory;

            // Setting load mode flags — OnLoadAllFamilyTypesChanged updates settings
            UpdateExistingTypesOnly = !_familiesDataModel.Settings.LoadAllFamilyTypesOnReload;
            LoadAllFamilyTypes = _familiesDataModel.Settings.LoadAllFamilyTypesOnReload;

            // Setting IncludeSubDirectoriesInSearch triggers OnIncludeSubDirectoriesInSearchChanged
            // which calls UpdateCommand.Execute — command not yet created, so set backing field directly
            // to avoid a null reference; the initial Execute() at the end of the constructor covers this.
            _includeSubDirectoriesInSearch = _familiesDataModel.Settings.IncludeSubdirectories;

            FamiliesSelectionDataGridViewModel = new FamiliesSelectionDataGridViewModel(
               _familiesDataModel,
               _stateStore);
            RegisterChild(FamiliesSelectionDataGridViewModel);

            _updateCommand = new Commands.RefreshFamilyFileMatchDataCommand(this, _familiesDataModel);

            _saveAndCloseCommand = new RelayCommand(
                SaveSettingsAndClose,
                () => !HasErrors
            );

            // Initial data refresh
            UpdateCommand.Execute(null);
        }
    }
}