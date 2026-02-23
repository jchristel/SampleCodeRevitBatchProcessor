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
using duHastNet.PushIt.Utilities;
using duHastNet.UI.CustomControls;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Linq;
using System.Windows.Input;

namespace duHastNet.PushIt.ViewModels
{
    public partial class RoomsMainViewModel : AppViewModelBase, INotifyDataErrorInfo
    {
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.StateStore _stateStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        // the global message view model
        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// View model managing the supported categories data grid.
        /// </summary>
        public duHastNet.PushIt.ViewModels.SupportedCatgeoriesDataGridViewModel SupportedCategoriesDataGridViewModel { get; }

        /// <summary>
        /// View model managing push it data grid
        /// </summary>
        public duHastNet.PushIt.ViewModels.RoomsDataGridViewModel RoomsDataGridViewModel { get; }

        // default values set inline on [ObservableProperty] declarations below

        //command to raise an event to refresh the gui
        private readonly Commands.RefreshUIFromRevitModelAsyncCommand _raiseRefreshGUICommand;
        //command to push a single room to revit
        private readonly Commands.PushSingleRoomInRevitAsyncCommand _raisePushSingleRoomCommand;
        //command to raise an event to reload data from file path
        private readonly Commands.ReloadDataFromFileAsyncCommand _raiseReloadDataCommand;
        //command to highlight a room in Revit
        private readonly Commands.HighlightRoomsInRevitAsyncCommand _highLightRoomCommand;
        //command to wipe stale rooms data
        private readonly Commands.WipeStaleDataRevitAsyncCommand _wipeStaleRoomsDataCommand;
        //command to update from changed categories
        private readonly Commands.UpdateFromChangedCategoriesAsyncCommand _updateFromChangedCategoriesCommand;
        //command to update all rooms in revit from data model
        private readonly Commands.PushAllRoomsInRevitAsyncCommand _updateAllRoomsCommand;
        //command to wipe selected rooms in revit
        private readonly Commands.WipeSelectedRevitRoomInstancesAsyncCommand _wipeSelectedRoomDataCommand;
        //command to save data to csv file
        private readonly Commands.SaveRoomDataAsyncCommand _saveDataCommand;

        //property to check if there are any errors
        public bool HasErrors => _errorsViewModel.HasErrors;
        // event handler for errors changed
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;

        #region observable properties

        // flag indicating whether the view model is waiting for a Revit command to finish
        [ObservableProperty]
        private bool _isWaitingForRevitCommandToFinish;

        #region push modus

        /// <summary>
        /// Property containing the three possible operation modi.
        /// Side effects: updates PushItButtonText and PushOperationMode.
        /// </summary>
        [ObservableProperty]
        private ThreeWaySwitch.SwitchState _switchState;

        partial void OnSwitchStateChanged(ThreeWaySwitch.SwitchState value)
        {
            if (value == ThreeWaySwitch.SwitchState.Left)
            {
                PushItButtonText = "Push It";
                PushOperationMode = PushIt.Utilities.PushMode.Push;
            }
            else if (value == ThreeWaySwitch.SwitchState.Centre)
            {
                PushItButtonText = "Split It";
                PushOperationMode = PushMode.Split;
            }
            else
            {
                PushItButtonText = "Create New";
                PushOperationMode = PushIt.Utilities.PushMode.New;
            }
        }

        /// <summary>
        /// The mode of operation for the push it command (push, push and split, push and new).
        /// Some commands check this value to determine whether they can execute.
        /// </summary>
        [ObservableProperty]
        private PushIt.Utilities.PushMode _pushOperationMode;

        /// <summary>
        /// Button text reflecting the current push operation mode.
        /// </summary>
        [ObservableProperty]
        private string _pushItButtonText = "Push It";

        #endregion push modus

        #region settings

        /// <summary>
        /// Path to the data file. Validates on set and updates the data model settings.
        /// </summary>
        [ObservableProperty]
        private string _dataFilePath;

        partial void OnDataFilePathChanged(string value)
        {
            _errorsViewModel.ClearErrors(nameof(DataFilePath));

            if (string.IsNullOrEmpty(value))
            {
                DataFilePathValid = false;
                // triggers data validation, which in turn calls OnPropertyChanged(nameof(DataFilePathValid))
                // via ErrorsViewModel_ErrorsChanged
                _errorsViewModel.AddError(nameof(DataFilePath), "Data file path cannot be empty");
            }
            else if (!System.IO.File.Exists(value))
            {
                DataFilePathValid = false;
                _errorsViewModel.AddError(nameof(DataFilePath), "Data file path does not exist");
            }
            else
            {
                DataFilePathValid = true;
                _errorsViewModel.ClearErrors(nameof(DataFilePath));
                _revitDataModel.Settings.DataPath = value;
            }
        }

        [ObservableProperty]
        private bool _dataFilePathValid;

        /// <summary>
        /// The currently active design set name.
        /// </summary>
        [ObservableProperty]
        private string _activeDesignSetName = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME;

        /// <summary>
        /// The currently active design option name.
        /// </summary>
        [ObservableProperty]
        private string _activeDesignOptionName = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME;

        #endregion settings

        #region user selection

        [ObservableProperty]
        private bool _saveFilePathValid;

        /// <summary>
        /// Path to the save file. Validates on set and triggers save command if valid.
        /// </summary>
        [ObservableProperty]
        private string _saveFilePath;

        partial void OnSaveFilePathChanged(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                SaveFilePathValid = false;
                _errorsViewModel.AddError(nameof(SaveFilePath), "Save file path cannot be empty");
                AddMessage($"Save file path cannot be empty: {value}", Utils.WPF.Stores.MessageTypes.Error);
            }
            else
            {
                SaveFilePathValid = true;
                _errorsViewModel.ClearErrors(nameof(SaveFilePath));
                if (_saveDataCommand != null)
                {
                    _saveDataCommand.Command.Execute(null);
                }
            }
        }

        #endregion user selection

        #endregion observable properties

        #region Commands

        public ICommand RefreshGUICommand => _raiseRefreshGUICommand.Command;
        public ICommand PushSingleRoomCommand => _raisePushSingleRoomCommand.Command;
        public ICommand ReloadDataCommand => _raiseReloadDataCommand.Command;
        public ICommand HighLightRoomCommand => _highLightRoomCommand.Command;
        public ICommand WipeStaleRoomsDataCommand => _wipeStaleRoomsDataCommand.Command;
        public ICommand UpdateFromChangedCategoriesCommand => _updateFromChangedCategoriesCommand.Command;
        public ICommand UpdateAllRoomsCommand => _updateAllRoomsCommand.Command;
        public ICommand WipeSelectedRoomDataCommand => _wipeSelectedRoomDataCommand.Command;
        public ICommand SaveDataCommand => _saveDataCommand.Command;

        #endregion Commands


        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {
            if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Error)
            {
                //let user dismiss the message themselves for error messages, since they might want to copy the message text for further use, and errors are more important to see for a longer time
                _messageStore.EnqueueMessage(message, messageType);
            }
            else if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Information)
            {
                //just flash message to user for information messages, since they are less important and user might not need to copy the message text, and it is better to dismiss them after a short time to avoid too many messages building up in the UI
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 2);
            }
            else
            {
                //default to short display time for other message types
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 5);
            }
        }


        public override void Dispose()
        {
            base.Dispose();
        }


        /// <summary>
        /// Custom closing logic for RoomsMainViewModel.
        /// Unsubscribes from events, saves column IDs and grid states to settings.
        /// </summary>
        public override void OnClosing()
        {
            //unsubscribe from errors changed event
            _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;

            //update the column ids in settings.
            _revitDataModel.Settings.ColumnIds.Clear();
            foreach (var columnId in RoomsDataGridViewModel.ColumnDefinitions)
            {
                _revitDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            //save states
            // FORCE save current grid state to StateStore before getting states for settings
            if (RoomsDataGridViewModel != null && _stateStore != null)
            {
                try
                {
                    var currentState = RoomsDataGridViewModel.CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        _stateStore.SaveState(RoomsDataGridViewModel, currentState);
                        System.Diagnostics.Debug.WriteLine($"Forced save of grid state for {RoomsDataGridViewModel.GetGridStateId()} before closing");
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
            _revitDataModel.Settings.NavigationStates = statesForSettings;

            // close any child view models
            // NOTE: base.OnClosing() automatically disposes all registered children
            // (GlobalMessageViewModel, SupportedCategoriesDataGridViewModel, RoomsDataGridViewModel)
            // DO NOT manually call .Dispose() on them here
            base.OnClosing();
        }


        /// <summary>
        /// Data validation for text input fields.
        /// </summary>
        /// <param name="propertyName">The name of the property to get errors for.</param>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }


        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            ErrorsChanged?.Invoke(this, e);
            OnPropertyChanged(nameof(DataFilePathValid));
        }

        /// <summary>
        /// Loads any existing states from settings into the state store.
        /// </summary>
        private void ApplyStateFromSettings()
        {
            if (_revitDataModel.Settings.NavigationStates != null && _revitDataModel.Settings.NavigationStates.Count > 0)
            {
                _stateStore.LoadStatesFromSettings(_revitDataModel.Settings.NavigationStates, () => new DataGridState());
                System.Diagnostics.Debug.WriteLine($"Loaded {_revitDataModel.Settings.NavigationStates.Count} states from settings into StateStore");
            }
        }


        /// <summary>
        /// The rooms selection view model class constructor.
        /// </summary>
        /// <param name="revitDataModel">The underlying revit data model</param>
        /// <param name="navigationStore">A navigation store for the UI</param>
        /// <param name="stateStore">A state store for grid state persistence</param>
        /// <param name="messageStore">A message store used to display messages to the user</param>
        /// <param name="globalMessageViewModel">A message view model the message store uses to display messages to the user.</param>
        public RoomsMainViewModel(
            Models.RevitDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.StateStore stateStore,
            Utils.WPF.Stores.MessageStore messageStore,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel)
        {
            //store services
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;
            _stateStore = stateStore;

            //initialize the errors view model
            _errorsViewModel = new Utils.WPF.ViewModels.ErrorsViewModel();

            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel);

            //load settings first
            ApplyStateFromSettings();

            // supported categories data grid view model
            SupportedCategoriesDataGridViewModel = new SupportedCatgeoriesDataGridViewModel(
                revitDataModel: revitDataModel);
            RegisterChild(SupportedCategoriesDataGridViewModel);

            //push it data grid view model
            RoomsDataGridViewModel = new RoomsDataGridViewModel(
                revitDataModel: revitDataModel,
                stateStore: stateStore);
            RegisterChild(RoomsDataGridViewModel);

            //set the data file path (triggers OnDataFilePathChanged for validation)
            DataFilePath = _revitDataModel.Settings.DataPath;

            // set up commands
            _raiseRefreshGUICommand = new Commands.RefreshUIFromRevitModelAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel);

            _raisePushSingleRoomCommand = new Commands.PushSingleRoomInRevitAsyncCommand(
                roomsMainViewModel: this,
                roomsDataGridViewModel: RoomsDataGridViewModel,
                revitDataModel: _revitDataModel);

            _raiseReloadDataCommand = new Commands.ReloadDataFromFileAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel);

            _highLightRoomCommand = new Commands.HighlightRoomsInRevitAsyncCommand(
                roomsMainViewModel: this,
                roomsDataGridViewModel: RoomsDataGridViewModel,
                revitDataModel: _revitDataModel);

            _wipeStaleRoomsDataCommand = new Commands.WipeStaleDataRevitAsyncCommand(
                roomsSelectionViewModel: this,
                revitDataModel: _revitDataModel);

            _updateFromChangedCategoriesCommand = new Commands.UpdateFromChangedCategoriesAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel);

            _updateAllRoomsCommand = new Commands.PushAllRoomsInRevitAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel);

            _wipeSelectedRoomDataCommand = new Commands.WipeSelectedRevitRoomInstancesAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel);

            _saveDataCommand = new Commands.SaveRoomDataAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel);

            // set the default push operation mode to push
            _pushOperationMode = PushIt.Utilities.PushMode.Push;

            //update rooms data with data from revit through an external event
            _raiseRefreshGUICommand.Command.Execute(null);
        }
    }
}