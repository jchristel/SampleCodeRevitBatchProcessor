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
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows;
using System.Windows.Input;
using System.Windows.Interop;

namespace duHastNet.UI.FamilyReloaderUI.ViewModels
{
    public partial class FamiliesSelectionViewModel : AppViewModelBase, INotifyDataErrorInfo
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
        public FamiliesSelectionDataGridViewModel FamiliesSelectionDataGridViewModel { get; }


        /// <summary>
        /// The data model for the export settings
        /// </summary>
        private readonly Models.FamiliesDataModel _familiesDataModel;


        /// <summary>
        /// command to save the settings and close the window
        /// </summary>
        private RelayCommand? _saveAndCloseCommand;

        /// <summary>
        /// command to refresh match status of families in UI
        /// </summary>
        private readonly Commands.RefreshFamilyFileMatchDataCommand _updateCommand;

        public ICommand? SaveAndCloseCommand => _saveAndCloseCommand;
        public Commands.RefreshFamilyFileMatchDataCommand UpdateCommand => _updateCommand;


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


        private void LoadSettings()
        {
            //load settings first
            var settings = duHastNet.UI.FamilyReloaderUI.Utils.SettingsUtils.LoadSettings(AddMessage: AddMessage);

            //cant simply replace the settings object in the data model...since it is used else where....need to update instead
            _familiesDataModel.Settings.UpdateSettingsFromSettings(settings);

            // Load StateStore states if they exist
            if (settings.NavigationStates != null && settings.NavigationStates.Count > 0)
            {
                // Create a factory for DataGridState instances
                _stateStore.LoadStatesFromSettings(settings.NavigationStates, () => new DataGridState());
                System.Diagnostics.Debug.WriteLine($"Loaded {settings.NavigationStates.Count} states from settings into StateStore");
            }
        }

        /// <summary>
        /// The file path for the exports to be saved to
        /// </summary>
        private string _selectedLibraryFilePath;

        /// <summary>
        /// property handling file path changes
        /// </summary>
        public string LibraryFilePath
        {
            get => _selectedLibraryFilePath;
            set
            {
                if (_selectedLibraryFilePath != value)
                {
                    _selectedLibraryFilePath = value;


                    _errorsViewModel.ClearErrors(nameof(LibraryFilePath));

                    // check if the file path is valid, if not add an error
                    if (string.IsNullOrEmpty(value))
                    {
                        // set the data path to invalid
                        LibraryDirectoryPathValid = false;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.AddError(nameof(LibraryFilePath), "Library path path cannot be empty");
                    }
                    else if (!System.IO.Directory.Exists(value))
                    {
                        // set the data path to invalid
                        LibraryDirectoryPathValid = false;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.AddError(nameof(LibraryFilePath), "Library path does not exist");
                    }
                    else
                    {
                        // set the data path to valid
                        LibraryDirectoryPathValid = true;
                        // this will trigger data validation
                        // from the eventhandler ErrorsViewModel_ErrorsChanged
                        _errorsViewModel.ClearErrors(nameof(LibraryFilePath));

                        //save in settings
                        _familiesDataModel.Settings.TargetDirectory = value;
                    }

                    OnPropertyChanged(nameof(LibraryFilePath));
                }
            }
        }

        /// <summary>
        /// if true only existing types will be rleoaded
        /// </summary>
        private bool _updateExistingTypesOnly;
        public bool UpdateExistingTypesOnly
        {
            get => _updateExistingTypesOnly;
            set
            {
                _updateExistingTypesOnly = value;
                OnPropertyChanged(nameof(UpdateExistingTypesOnly));
            }
        }

        /// <summary>
        /// if true all family types will be loaded into the project
        /// </summary>
        private bool _loadAllFamilyTypes;
        public bool LoadAllFamilyTypes
        {
            get => _loadAllFamilyTypes;
            set
            {
                _loadAllFamilyTypes = value;
                //store in settings
                _familiesDataModel.Settings.LoadAllFamilyTypesOnReload = value;
                OnPropertyChanged(nameof(LoadAllFamilyTypes));
            }
        }

        /// <summary>
        /// property indicating as to whether any subdirectories are to be included in search for matching family
        /// </summary>
        private bool _includeSudDirectoriesInSearch;
        public bool IncludeSubDirectoriesInSearch
        {
            get => _includeSudDirectoriesInSearch;
            set
            {
                _includeSudDirectoriesInSearch = value;
                _familiesDataModel.Settings.IncludeSubdirectories = value;
                OnPropertyChanged(nameof(IncludeSubDirectoriesInSearch));

                //refresh the view model data if command is available
                if (UpdateCommand != null)
                {
                    UpdateCommand.Execute(null);
                }
            }
        }


        /// <summary>
        /// Custom closing logic for RoomsSelectionViewModel
        /// Disposes all external events from the event manager
        /// </summary>
        public override void OnClosing()
        {
            //unsubscribe from errors changed event
            _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;

            // close any child view models (base handles GlobalMessageViewModel cleanup)
            base.OnClosing();
        }

        public override void Dispose()
        {
            // Call base to handle disposal of child ViewModels
            base.Dispose();
        }

        /// <summary>
        /// closes the window
        /// </summary>
        private void SaveSettingsAndClose()
        {
            //update the column ids in settings.
            // clear list first
            _familiesDataModel.Settings.ColumnIds.Clear();
            // add current list
            foreach (var columnId in FamiliesSelectionDataGridViewModel.ColumnDefinitions)
            {
                _familiesDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            // FORCE save current grid state to StateStore before getting states for settings
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


            // Get states from StateStore for settings persistence
            var statesForSettings = _stateStore.GetStatesForSettings();

            // Update the settings with the grid states
            _familiesDataModel.Settings.NavigationStates = statesForSettings;

            //store settings
            Utils.SettingsUtils.SaveSettings(_familiesDataModel.Settings);

            // Close the application main window
            Application.Current.MainWindow?.Close();
        }

        #region data validation

        private bool _libraryDirectoryPathValid;
        public bool LibraryDirectoryPathValid
        {
            get => _libraryDirectoryPathValid;
            set
            {
                _libraryDirectoryPathValid = value;
                // call ui update
                OnPropertyChanged(nameof(LibraryDirectoryPathValid));
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
            OnPropertyChanged(nameof(LibraryDirectoryPathValid));

            // Trigger the command to re-evaluate its CanExecute state
            _saveAndCloseCommand?.NotifyCanExecuteChanged();
        }

        #endregion data validation

        public FamiliesSelectionViewModel(
            Models.FamiliesDataModel familiesDataModel,
            duHastNet.Utils.WPF.Stores.NavigationStore navigationStore,
            duHastNet.Utils.WPF.Stores.StateStore stateStore,
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore
            )
        {

            //store the export data model
            _familiesDataModel = familiesDataModel;

            //store the navigation store
            _navigationStore = navigationStore;

            //store the state store
            _stateStore = stateStore;

            //store the message store
            _messageStore = messageStore;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;

            // Register GlobalMessageViewModel as a child for automatic cleanup
            RegisterChild(GlobalMessageViewModel);

            // initialize the errors view model
            _errorsViewModel = new duHastNet.Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //load settings first
            LoadSettings();

            //set the data file path
            LibraryFilePath = _familiesDataModel.Settings.TargetDirectory;

            //update load method readio buttons
            UpdateExistingTypesOnly = !_familiesDataModel.Settings.LoadAllFamilyTypesOnReload;
            LoadAllFamilyTypes = _familiesDataModel.Settings.LoadAllFamilyTypesOnReload;

            //update the include sub dirs in seach checkbox
            IncludeSubDirectoriesInSearch = _familiesDataModel.Settings.IncludeSubdirectories;

            //initialise the families grid view model
            FamiliesSelectionDataGridViewModel = new FamiliesSelectionDataGridViewModel(
               _familiesDataModel,
               _stateStore);

            // Register the child so it gets cleaned up properly
            RegisterChild(FamiliesSelectionDataGridViewModel);

            //commands
            //refresh family match status
            _updateCommand = new Commands.RefreshFamilyFileMatchDataCommand(this, _familiesDataModel);

            //save and exit
            //only if there are no errors
            _saveAndCloseCommand = new RelayCommand(
                SaveSettingsAndClose,
                () => !HasErrors // Only enabled when there are no errors
            );

            //refresh the view model data
            UpdateCommand.Execute(null);
        }
    }
}