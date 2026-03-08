//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, even if advised of the possibility of such damage.
//
//
//

using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.RevitActions.Drofus;
using duHastNet.PushIt.ViewModels.DataSource;
using duHastNet.Utils.WPF.ViewModels;
using System;
using System.Collections.Generic;

namespace duHastNet.PushIt.ViewModels
{
    /// <summary>
    /// ViewModel for the Settings navigation view.
    /// <para>
    /// Takes a snapshot of the current <see cref="DataSourceSettings"/> and
    /// enabled category names when constructed. On Cancel, the snapshot is
    /// restored to the data model and a fresh <see cref="RoomsMainViewModel"/>
    /// is shown — the grid rebuilds identically to before. On Load Data, the
    /// current (edited) state is committed and the grid rebuilds with the new
    /// settings.
    /// </para>
    /// </summary>
    public partial class SettingsViewModel : AppViewModelBase
    {
        // ── Private fields ────────────────────────────────────────────────────

        private readonly Models.RevitDataModel _revitDataModel;
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.StateStore _stateStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;

        // Snapshots taken at construction time — used to restore on Cancel.
        private readonly DataSourceSettings _dataSourceSnapshot;
        private readonly List<string> _enabledCategoryNamesSnapshot;

        // ── Child ViewModels ──────────────────────────────────────────────────

        /// <summary>The global message banner ViewModel.</summary>
        public GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>Data source selector + provider-specific config control.</summary>
        public DataSourceViewModel DataSourceViewModel { get; }

        /// <summary>Supported categories grid.</summary>
        public SupportedCatgeoriesDataGridViewModel SupportedCategoriesDataGridViewModel { get; }

        // ── Commands ──────────────────────────────────────────────────────────

        /// <summary>
        /// Restores the pre-Settings snapshot and navigates back to a fresh
        /// <see cref="RoomsMainViewModel"/> — the grid rebuilds as it was.
        /// </summary>
        public RelayCommand CancelCommand { get; }

        /// <summary>
        /// Commits the current (edited) settings to the data model, persists
        /// them to disk, and navigates back to a fresh
        /// <see cref="RoomsMainViewModel"/> which rebuilds with the new config.
        /// </summary>
        public RelayCommand LoadDataCommand { get; }

        // ── Constructor ───────────────────────────────────────────────────────

        public SettingsViewModel(
            Models.RevitDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.StateStore stateStore,
            Utils.WPF.Stores.MessageStore messageStore,
            GlobalMessageViewModel globalMessageViewModel)
        {
            _revitDataModel = revitDataModel;
            _navigationStore = navigationStore;
            _stateStore = stateStore;
            _messageStore = messageStore;

            // ── Snapshots ─────────────────────────────────────────────────────
            // Deep-copy the data source settings so Cancel can restore them even
            // if the user changes the provider or edits connection fields.
            _dataSourceSnapshot = _revitDataModel.Settings.DataSource.DeepCopy();

            // Shallow copy of the string list is sufficient — strings are immutable.
            _enabledCategoryNamesSnapshot =
                new List<string>(_revitDataModel.Settings.EnabledCategoryNames);

            // ── Children ──────────────────────────────────────────────────────
            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel);

            // DataSourceViewModel operates on the LIVE settings object. Changes
            // made here are live mutations. Cancel restores from the snapshot;
            // Load Data commits and saves.
            DataSourceViewModel = new DataSourceViewModel(
                _revitDataModel.Settings.DataSource,
                _revitDataModel,
                _revitDataModel.GetAllAvailableParameters());
            DataSourceViewModel.LoadFromSettings(_revitDataModel.Settings.DataSource);
            RegisterChild(DataSourceViewModel);

            SupportedCategoriesDataGridViewModel = new SupportedCatgeoriesDataGridViewModel(
                revitDataModel: _revitDataModel);
            RegisterChild(SupportedCategoriesDataGridViewModel);

            // ── Commands ──────────────────────────────────────────────────────
            CancelCommand = new RelayCommand(ExecuteCancel);
            LoadDataCommand = new RelayCommand(ExecuteLoadData);
        }

        // ── Command Implementations ───────────────────────────────────────────

        /// <summary>
        /// Restores the pre-Settings snapshot into the data model, then
        /// navigates to a fresh <see cref="RoomsMainViewModel"/>.
        /// </summary>
        private void ExecuteCancel()
        {
            // Restore data source settings from snapshot.
            _revitDataModel.Settings.DataSource = _dataSourceSnapshot;

            // Restore enabled category names from snapshot.
            _revitDataModel.Settings.EnabledCategoryNames.Clear();
            _revitDataModel.Settings.EnabledCategoryNames.AddRange(_enabledCategoryNamesSnapshot);

            // Restore the category enabled/disabled flags on the live category
            // objects so the grid in the new RoomsMainViewModel reflects the
            // restored state.
            foreach (var category in _revitDataModel.GetAllCategories())
            {
                category.Enabled = _enabledCategoryNamesSnapshot.Contains(category.Name);
            }

            NavigateToRoomsMain();
        }

        /// <summary>
        /// Commits the current (edited) settings to the data model, runs the
        /// source-specific startup sequence (validate + load rooms into the model),
        /// persists settings to disk, then navigates to a fresh
        /// <see cref="RoomsMainViewModel"/> whose <c>RefreshUIFromRevitModelAsyncCommand</c>
        /// will match the loaded rooms against Revit.
        /// </summary>
        private void ExecuteLoadData()
        {
            // Flush the data source ViewModel state into the live settings object.
            DataSourceViewModel.SaveToSettings(_revitDataModel.Settings.DataSource);

            // Commit the enabled category names from the grid to settings.
            _revitDataModel.Settings.EnabledCategoryNames.Clear();
            foreach (var category in _revitDataModel.GetAllCategories())
            {
                if (category.Enabled)
                    _revitDataModel.Settings.EnabledCategoryNames.Add(category.Name);
            }

            // ── Run source-specific startup ───────────────────────────────────
            // Mirrors Main.RunDrofusStartupIfRequired / RunCsvStartupIfRequired.
            // Must run here so rooms are in the model before the fresh
            // RoomsMainViewModel fires _raiseRefreshGUICommand.
            var sourceType = _revitDataModel.Settings.DataSource.SourceType;

            if (sourceType == DataSourceType.Drofus
                && _revitDataModel.Settings.DataSource.Drofus != null)
            {
                var mapper = new Utilities.Drofus.DrofusPropertyMapper(
                    _revitDataModel.Settings.DataSource.Drofus.PropertyMappings);

                try
                {
                    var action = new ValidateDrofusOnStartup(_revitDataModel, mapper);
                    (string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType) =
                        action.Execute();

                    if (messageType != duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                        _messageStore.EnqueueMessage(message, messageType);
                }
                catch (Exception ex)
                {
                    _messageStore.EnqueueMessage(
                        $"drofus load failed: {ex.Message}",
                        duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
            }
            else if (sourceType == DataSourceType.Csv)
            {
                var csvDataSource = new Utilities.CsvDataSource();
                if (!csvDataSource.Validate(_revitDataModel.Settings.DataSource, out string validationError))
                {
                    _messageStore.EnqueueMessage(
                        $"CSV: {validationError}",
                        duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
                else
                {
                    try
                    {
                        var action = new ValidateCsvOnStartup(_revitDataModel);
                        (string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType) =
                            action.Execute();

                        if (messageType != duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                            _messageStore.EnqueueMessage(message, messageType);
                    }
                    catch (Exception ex)
                    {
                        _messageStore.EnqueueMessage(
                            $"CSV load failed: {ex.Message}",
                            duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                    }
                }
            }

            // Persist to disk so the next session starts with the updated config.
            Utilities.SettingsUtils.SaveSettings(_revitDataModel.Settings);

            NavigateToRoomsMain();
        }

        // ── Private Helpers ───────────────────────────────────────────────────

        /// <summary>
        /// Disposes this ViewModel's children and navigates to a freshly
        /// constructed <see cref="RoomsMainViewModel"/>.
        /// </summary>
        private void NavigateToRoomsMain()
        {
            OnClosing();

            var globalMsgVm = new GlobalMessageViewModel(_messageStore);

            var roomsVm = new RoomsMainViewModel(
                _revitDataModel,
                _navigationStore,
                _stateStore,
                _messageStore,
                globalMsgVm);

            // Notify the drofus control VM so Add Mapping button and validation
            // indicators reflect the load results before the view is shown.
            if (_revitDataModel.Settings.DataSource.SourceType == DataSourceType.Drofus)
            {
                if (roomsVm.DataSourceViewModel.CurrentSourceControlViewModel
                        is DrofusDataSourceControlViewModel drofusVm)
                {
                    drofusVm.OnStartupCompleted();
                }
            }

            _navigationStore.CurrentViewModel = roomsVm;
        }
    }
}