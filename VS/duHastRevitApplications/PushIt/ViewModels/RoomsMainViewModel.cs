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
using duHastNet.PushIt.ViewModels.DataSource;
using duHastNet.UI.CustomControls;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using System;
using System.Collections;
using System.ComponentModel;
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

        // ── Child ViewModels ──────────────────────────────────────────────────────

        /// <summary>The global message banner ViewModel.</summary>
        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>ViewModel managing the supported categories data grid.</summary>
        public duHastNet.PushIt.ViewModels.SupportedCatgeoriesDataGridViewModel SupportedCategoriesDataGridViewModel { get; }

        /// <summary>ViewModel managing the rooms data grid.</summary>
        public duHastNet.PushIt.ViewModels.RoomsDataGridViewModel RoomsDataGridViewModel { get; }

        /// <summary>
        /// Host ViewModel for the data source configuration UI.
        /// Owns the provider dropdown and the provider-specific child control.
        /// Replaces the old <c>DataFilePath</c> / <c>DataFilePathValid</c>
        /// properties that were previously inlined here.
        /// </summary>
        public DataSourceViewModel DataSourceViewModel { get; }

        // ── Commands ──────────────────────────────────────────────────────────────

        private readonly Commands.RefreshUIFromRevitModelAsyncCommand _raiseRefreshGUICommand;
        private readonly Commands.PushSingleRoomInRevitAsyncCommand _raisePushSingleRoomCommand;
        private readonly Commands.ReloadDataFromFileAsyncCommand _raiseReloadDataCommand;
        private readonly Commands.HighlightRoomsInRevitAsyncCommand _highLightRoomCommand;
        private readonly Commands.WipeStaleDataRevitAsyncCommand _wipeStaleRoomsDataCommand;
        private readonly Commands.UpdateFromChangedCategoriesAsyncCommand _updateFromChangedCategoriesCommand;
        private readonly Commands.PushAllRoomsInRevitAsyncCommand _updateAllRoomsCommand;
        private readonly Commands.WipeSelectedRevitRoomInstancesAsyncCommand _wipeSelectedRoomDataCommand;
        private readonly Commands.SaveRoomDataAsyncCommand _saveDataCommand;

        // ── INotifyDataErrorInfo ──────────────────────────────────────────────────

        /// <summary>
        /// True when either the local <see cref="_errorsViewModel"/> has errors
        /// or <see cref="DataSourceViewModel.HasValidationErrors"/> is true.
        /// </summary>
        public bool HasErrors =>
            _errorsViewModel.HasErrors || DataSourceViewModel.HasValidationErrors;

        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;

        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }

        // ── Observable Properties ─────────────────────────────────────────────────

        #region observable properties

        [ObservableProperty]
        private bool _isWaitingForRevitCommandToFinish;

        /// <summary>
        /// The active Revit document title, read from <see cref="Models.RevitDataModel.RevitDocumentTitle"/>.
        /// Long titles are split into lines of at most 16 characters so the blue
        /// header row can display them without overflowing.
        /// </summary>
        public string RevitDocumentTitle =>
            WrapAtWidth(_revitDataModel.RevitDocumentTitle, 16);

        /// <summary>
        /// Splits <paramref name="text"/> into lines of at most
        /// <paramref name="maxChars"/> characters, breaking on whole words where
        /// possible, and joins them with a newline so WPF TextBlock can render them.
        /// </summary>
        private static string WrapAtWidth(string text, int maxChars)
        {
            if (string.IsNullOrEmpty(text) || text.Length <= maxChars)
                return text;

            var lines = new System.Collections.Generic.List<string>();
            int start = 0;
            while (start < text.Length)
            {
                if (start + maxChars >= text.Length)
                {
                    lines.Add(text.Substring(start));
                    break;
                }

                // Try to break on a space within the window
                int breakAt = text.LastIndexOf(' ', start + maxChars, maxChars);
                if (breakAt <= start)
                    breakAt = start + maxChars; // hard break

                lines.Add(text.Substring(start, breakAt - start).TrimEnd());
                start = breakAt + (text[breakAt] == ' ' ? 1 : 0);
            }
            return string.Join("\n", lines);
        }

        #region push modus

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

        [ObservableProperty]
        private PushIt.Utilities.PushMode _pushOperationMode;

        [ObservableProperty]
        private string _pushItButtonText = "Push It";

        #endregion push modus

        #region settings

        // DataFilePath and DataFilePathValid have been removed.
        // All data-source configuration is now owned by DataSourceViewModel.
        // ReloadDataFromFileAsyncCommand reads DataSourceViewModel.HasValidationErrors
        // instead of the old DataFilePathValid flag.

        [ObservableProperty]
        private string _activeDesignSetName = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME;

        [ObservableProperty]
        private string _activeDesignOptionName = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME;

        #endregion settings

        #region user selection

        [ObservableProperty]
        private bool _saveFilePathValid;

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

        // ── ICommand Wrappers ─────────────────────────────────────────────────────

        public ICommand RefreshGUICommand => _raiseRefreshGUICommand.Command;
        public ICommand PushSingleRoomCommand => _raisePushSingleRoomCommand.Command;
        public ICommand ReloadDataCommand => _raiseReloadDataCommand.Command;
        public ICommand HighLightRoomCommand => _highLightRoomCommand.Command;
        public ICommand WipeStaleRoomsDataCommand => _wipeStaleRoomsDataCommand.Command;
        public ICommand UpdateFromChangedCategoriesCommand => _updateFromChangedCategoriesCommand.Command;
        public ICommand UpdateAllRoomsCommand => _updateAllRoomsCommand.Command;
        public ICommand WipeSelectedRoomDataCommand => _wipeSelectedRoomDataCommand.Command;
        public ICommand SaveDataCommand => _saveDataCommand.Command;

        // ── Helpers ───────────────────────────────────────────────────────────────

        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
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

        // ── Event Handlers ────────────────────────────────────────────────────────

        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            ErrorsChanged?.Invoke(this, e);
            // Notify commands whose CanExecute depends on error state
            OnPropertyChanged(nameof(HasErrors));
        }

        private void OnRevitDataModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(Models.RevitDataModel.RevitDocumentTitle))
                OnPropertyChanged(nameof(RevitDocumentTitle));
        }

        /// <summary>
        /// Handles PropertyChanged from <see cref="DataSourceViewModel"/>.
        /// When its <see cref="DataSourceViewModel.HasValidationErrors"/> changes,
        /// we forward that to our own <see cref="HasErrors"/> and notify the
        /// reload command to re-evaluate CanExecute.
        /// </summary>
        private void OnDataSourceViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(DataSourceViewModel.HasValidationErrors) ||
                string.IsNullOrEmpty(e.PropertyName))
            {
                OnPropertyChanged(nameof(HasErrors));
                // The reload command watches IsWaitingForRevitCommandToFinish and
                // HasValidationErrors via RoomsMainViewModel.PropertyChanged, so
                // raising HasErrors is sufficient to trigger re-evaluation.
            }
        }

        // ── Lifecycle ─────────────────────────────────────────────────────────────

        public override void Dispose()
        {
            base.Dispose();
        }

        /// <summary>
        /// Custom closing logic. Unsubscribes from events, writes column and grid
        /// state back to settings, and calls <c>base.OnClosing()</c> to dispose
        /// all registered children.
        /// </summary>
        public override void OnClosing()
        {
            // Unsubscribe from child error events
            _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;
            DataSourceViewModel.PropertyChanged -= OnDataSourceViewModelPropertyChanged;
            _revitDataModel.PropertyChanged -= OnRevitDataModelPropertyChanged;

            // Persist current data source config back to settings before closing.
            // Must be called before base.OnClosing() which triggers DataSourceViewModel.OnClosing().
            DataSourceViewModel.SaveToSettings(_revitDataModel.Settings.DataSource);

            // Update column ids
            _revitDataModel.Settings.ColumnIds.Clear();
            foreach (var columnId in RoomsDataGridViewModel.ColumnDefinitions)
            {
                _revitDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            // Force save current grid state before closing
            if (RoomsDataGridViewModel != null && _stateStore != null)
            {
                try
                {
                    var currentState = RoomsDataGridViewModel.CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        _stateStore.SaveState(RoomsDataGridViewModel, currentState);
                    }
                }
                catch (Exception stateEx)
                {
                    AddMessage($"Warning: Could not save grid state: {stateEx.Message}",
                        duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
            }

            _revitDataModel.Settings.NavigationStates = _stateStore.GetStatesForSettings();

            // Dispose all registered children (GlobalMessageViewModel,
            // SupportedCategoriesDataGridViewModel, RoomsDataGridViewModel)
            base.OnClosing();
        }

        // ── Private Helpers ───────────────────────────────────────────────────────

        private void ApplyStateFromSettings()
        {
            if (_revitDataModel.Settings.NavigationStates != null &&
                _revitDataModel.Settings.NavigationStates.Count > 0)
            {
                _stateStore.LoadStatesFromSettings(
                    _revitDataModel.Settings.NavigationStates,
                    () => new DataGridState());
            }
        }

        // ── Constructor ───────────────────────────────────────────────────────────

        public RoomsMainViewModel(
            Models.RevitDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.StateStore stateStore,
            Utils.WPF.Stores.MessageStore messageStore,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel)
        {
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;
            _stateStore = stateStore;

            // Forward RevitDocumentTitle changes from the data model to the UI
            _revitDataModel.PropertyChanged += OnRevitDataModelPropertyChanged;

            // Errors ViewModel for local validation (SaveFilePath, etc.)
            _errorsViewModel = new Utils.WPF.ViewModels.ErrorsViewModel();
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            // Global message banner
            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel);

            // Restore grid states from persisted settings
            ApplyStateFromSettings();

            // Data grids
            SupportedCategoriesDataGridViewModel = new SupportedCatgeoriesDataGridViewModel(
                revitDataModel: revitDataModel);
            RegisterChild(SupportedCategoriesDataGridViewModel);

            RoomsDataGridViewModel = new RoomsDataGridViewModel(
                revitDataModel: revitDataModel,
                stateStore: stateStore);
            RegisterChild(RoomsDataGridViewModel);

            // ── Data Source ViewModel ─────────────────────────────────────────────
            // Create host ViewModel, load current settings into it, and subscribe
            // to its validation changes so HasErrors and command CanExecute stay
            // in sync. This replaces the old DataFilePath / DataFilePathValid pair.
            DataSourceViewModel = new DataSourceViewModel(_revitDataModel.Settings.DataSource);
            DataSourceViewModel.LoadFromSettings(_revitDataModel.Settings.DataSource);
            DataSourceViewModel.PropertyChanged += OnDataSourceViewModelPropertyChanged;
            RegisterChild(DataSourceViewModel);

            // ── Commands ──────────────────────────────────────────────────────────
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

            _pushOperationMode = PushIt.Utilities.PushMode.Push;

            // Trigger initial Revit model refresh
            _raiseRefreshGUICommand.Command.Execute(null);
        }
    }
}