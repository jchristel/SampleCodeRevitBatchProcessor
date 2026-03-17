// BSD License - Copyright 2025, Jan Christel

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Models.Drofus;
using duHastNet.PushIt.Utilities.Drofus;
using duHastNet.PushIt.ViewModels.DataSource.Drofus;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;

namespace duHastNet.PushIt.ViewModels.DataSource
{
    /// <summary>
    /// Child ViewModel for the drofus data source configuration panel.
    /// Owns the four connection fields, the Connect command, the
    /// <see cref="DrofusPropertyMapper"/> service instance, the configuration
    /// selector, and the <see cref="MappingRows"/> collection that drives the
    /// mapping ListView.
    /// The Connect command is synchronous — all HTTP calls use blocking
    /// WebRequest so no async machinery is needed in this ViewModel.
    /// </summary>
    public partial class DrofusDataSourceControlViewModel : ObservableObject
    {
        private readonly DataSourceSettings _settings;
        private readonly RevitDataModel? _revitDataModel;
        private readonly IReadOnlyList<AvailableParameter> _availableRevitParameters;

        /// <summary>
        /// Tracks the id of the configuration that was active before the user
        /// began changing the selector, so it can be restored on Scenario 5 cancel.
        /// </summary>
        private int? _previousConfigurationId;

        /// <summary>
        /// Guards against re-entrant calls to <see cref="OnSelectedConfigurationChanged"/>
        /// when we programmatically revert the selector after a cancelled Scenario 5.
        /// </summary>
        private bool _suppressConfigurationChangeHandler;

        /// <summary>
        /// The mapper service instance. Exposed publicly so that
        /// ValidateDrofusMappingsOnStartup can receive it from Main.ExecuteInternal.
        /// </summary>
        public DrofusPropertyMapper Mapper { get; }

        /// <summary>
        /// <c>true</c> when the mapper has at least one available drofus field —
        /// meaning a successful API connection has been made either during the
        /// current session (Connect button) or during startup.
        /// Used as the CanExecute condition for AddMapping so the user can set up
        /// mappings as soon as fields are known, without requiring IsConnected.
        /// </summary>
        public bool HasAvailableFields => Mapper.AvailableFields.Count > 0;

        /// <summary>
        /// <c>true</c> when at least one room attribute configuration is available.
        /// Controls the visibility and enabled state of the configuration selector
        /// and the mapping interface (Add/Edit/Remove buttons, mapping list).
        /// Becomes <c>false</c> when the configurations fetch failed or returned no
        /// room configurations (Gap 2 / Scenario 1).
        /// </summary>
        public bool HasConfigurations => AvailableConfigurations.Count > 0;

        /// <summary>
        /// <c>true</c> when drofus could not be reached at startup and existing
        /// mappings are in a degraded (preserved-but-unverified) state.
        /// Drives the disabled state of the room grid and the Push button.
        /// Cleared as soon as a successful Connect is made.
        /// </summary>
        [ObservableProperty] private bool _isDrofusOffline;

        [ObservableProperty] private string _baseUrl = string.Empty;
        [ObservableProperty] private string _databaseName = string.Empty;
        [ObservableProperty] private string _projectNumber = string.Empty;
        [ObservableProperty] private string _apiToken = string.Empty;
        [ObservableProperty] private string _statusMessage = string.Empty;
        [ObservableProperty] private bool _isConnected;
        [ObservableProperty] private bool _isConnecting;

        /// <summary>
        /// The attribute configurations available for this drofus project.
        /// Populated after a successful Connect and on startup via
        /// <see cref="OnStartupCompleted"/>.
        /// </summary>
        public ObservableCollection<DrofusAttributeConfiguration> AvailableConfigurations { get; }
            = new ObservableCollection<DrofusAttributeConfiguration>();

        /// <summary>
        /// The currently selected attribute configuration. When changed, triggers
        /// Scenario 5 handling (confirmation dialog if mappings would be dropped).
        /// <c>null</c> means no configuration is selected.
        /// </summary>
        [ObservableProperty]
        private DrofusAttributeConfiguration? _selectedConfiguration;

        public ObservableCollection<DrofusPropertyMapViewModel> MappingRows { get; }
            = new ObservableCollection<DrofusPropertyMapViewModel>();

        [ObservableProperty] private DrofusPropertyMapViewModel? _selectedMappingRow;
        [ObservableProperty] private bool _hasValidationWarnings;

        public DrofusDataSourceControlViewModel(
            DataSourceSettings settings,
            RevitDataModel? revitDataModel,
            IReadOnlyList<AvailableParameter> availableRevitParameters)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));
            _revitDataModel = revitDataModel;
            _availableRevitParameters = availableRevitParameters
                ?? Array.Empty<AvailableParameter>();

            _settings.Drofus ??= new DrofusDataSourceSettings();
            var d = _settings.Drofus;

            _baseUrl = d.BaseUrl;
            _databaseName = d.DatabaseName;
            _projectNumber = d.ProjectNumber;
            _apiToken = d.ApiToken;
            _statusMessage = string.Empty;

            Mapper = new DrofusPropertyMapper(d.PropertyMappings);

            // If startup validation has already run (before the window opened),
            // the field catalogue and configurations were cached on the settings
            // object so the ViewModel can initialise without a second API call.
            if (d.StartupFieldCatalogue.Count > 0)
                Mapper.UpdateAvailableFields(d.StartupFieldCatalogue);

            if (d.StartupAttributeConfigurations.Count > 0)
            {
                Mapper.UpdateAvailableConfigurations(d.StartupAttributeConfigurations);
                Mapper.SelectConfiguration(d.SelectedAttributeConfigurationId, d);
                RebuildConfigurationSelector(d.SelectedAttributeConfigurationId);
            }

            RebuildMappingRows();
        }

        // ── Connect ───────────────────────────────────────────────────────────

        [RelayCommand(CanExecute = nameof(CanConnect))]
        private void Connect()
        {
            _settings.Drofus ??= new DrofusDataSourceSettings();
            var d = _settings.Drofus;

            d.BaseUrl = BaseUrl.Trim();
            d.DatabaseName = DatabaseName.Trim();
            d.ProjectNumber = ProjectNumber.Trim();
            d.ApiToken = ApiToken.Trim();

            IsConnecting = true;
            StatusMessage = "Connecting...";

            try
            {
                var dataSource = new DrofusDataSource();

                if (!dataSource.Validate(_settings, out string validationError))
                {
                    StatusMessage = validationError;
                    IsConnected = false;
                    return;
                }

                // ── 1. Field catalogue (fatal on failure — Gap 1) ─────────────
                List<DrofusRoomField> fieldCatalogue;
                try
                {
                    fieldCatalogue = dataSource.GetFieldCatalogue(_settings);
                }
                catch (Exception ex)
                {
                    IsConnected = false;
                    StatusMessage = "Could not retrieve the room field catalogue from drofus. " +
                                    $"Check your connection and reconnect. Detail: {ex.Message}";
                    // HasAvailableFields remains false → mapping interface stays disabled.
                    return;
                }

                Mapper.UpdateAvailableFields(fieldCatalogue);
                d.StartupFieldCatalogue = fieldCatalogue;

                // ── 2. Attribute configurations (fatal to mapping interface — Gap 2) ──
                List<DrofusAttributeConfiguration> configurations;
                try
                {
                    configurations = dataSource.GetAttributeConfigurations(_settings);
                }
                catch (Exception ex)
                {
                    // Treat identically to Scenario 1 (no room configurations).
                    configurations = new List<DrofusAttributeConfiguration>();
                    StatusMessage = "No room attribute configurations are set up in drofus. " +
                                    "At least one is required to configure mappings. " +
                                    "Please create a room attribute configuration in drofus and reconnect. " +
                                    $"Detail: {ex.Message}";
                }

                Mapper.UpdateAvailableConfigurations(configurations);
                d.StartupAttributeConfigurations = configurations;

                IsConnected = true;
                IsDrofusOffline = false;

                // ── 3. Scenario 1: no room configurations ─────────────────────
                if (configurations.Count == 0)
                {
                    RebuildConfigurationSelector(null);
                    OnPropertyChanged(nameof(HasConfigurations));
                    AddMappingCommand.NotifyCanExecuteChanged();
                    // Message already set above in the catch or here:
                    if (string.IsNullOrEmpty(StatusMessage) || StatusMessage == "Connecting...")
                    {
                        StatusMessage = "No room attribute configurations are set up in drofus. " +
                                        "At least one is required to configure mappings.";
                    }
                    return;
                }

                // ── 4. Scenario 3: selected configuration was deleted ──────────
                // Only checked on a successful connect — Gap 9 requires we do NOT
                // call HandleDeletedConfiguration on connection failure.
                if (d.SelectedAttributeConfigurationId != null)
                {
                    bool configStillExists = configurations.Any(
                        c => c.Id == d.SelectedAttributeConfigurationId.Value);

                    if (!configStillExists)
                    {
                        string deletedMsg = Mapper.HandleDeletedConfiguration();
                        Mapper.SaveMappingsToSettings(d);
                        Mapper.SelectConfiguration(null, d);

                        RebuildConfigurationSelector(null);
                        OnPropertyChanged(nameof(HasConfigurations));
                        RebuildMappingRows();
                        AddMappingCommand.NotifyCanExecuteChanged();

                        StatusMessage = deletedMsg;
                        return;
                    }
                }

                // ── 5. Normal connect: cleanup stale mappings, rebuild UI ──────
                List<string> removed = Mapper.CleanupStaleMappings();
                Mapper.SaveMappingsToSettings(d);

                RebuildConfigurationSelector(d.SelectedAttributeConfigurationId);
                OnPropertyChanged(nameof(HasConfigurations));
                RebuildMappingRows();
                AddMappingCommand.NotifyCanExecuteChanged();

                var sb = new StringBuilder("Connected.");
                if (removed.Count > 0)
                    sb.Append($" {removed.Count} stale mapping(s) removed: {string.Join(", ", removed)}.");
                StatusMessage = sb.ToString();
            }
            catch (Exception ex)
            {
                IsConnected = false;
                StatusMessage = ex.Message;
            }
            finally
            {
                IsConnecting = false;
                ConnectCommand.NotifyCanExecuteChanged();
            }
        }

        private bool CanConnect()
            => !IsConnecting
            && !string.IsNullOrWhiteSpace(BaseUrl)
            && !string.IsNullOrWhiteSpace(DatabaseName)
            && !string.IsNullOrWhiteSpace(ProjectNumber)
            && !string.IsNullOrWhiteSpace(ApiToken);

        partial void OnBaseUrlChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnDatabaseNameChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnProjectNumberChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnApiTokenChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();

        // ── Configuration selector ────────────────────────────────────────────

        partial void OnSelectedConfigurationChanged(DrofusAttributeConfiguration? value)
        {
            // Guard: skip when we are programmatically reverting after a cancel.
            if (_suppressConfigurationChangeHandler) return;

            var d = _settings.Drofus;
            if (d is null) return;

            int? newId = value?.Id;

            // No-op if the selection didn't actually change.
            if (newId == Mapper.SelectedConfigurationId) return;

            // Scenario 5: check whether switching would drop any existing mappings.
            if (newId != null && Mapper.Mappings.Count > 0)
            {
                // Compute which current mappings reference field ids that are NOT
                // in the new configuration's elements.
                DrofusAttributeConfiguration? newConfig =
                    Mapper.AvailableConfigurations.FirstOrDefault(c => c.Id == newId.Value);

                if (newConfig != null)
                {
                    var newConfigIds = new HashSet<string>(
                        newConfig.Elements.Select(e => e.DrofusAttributeId),
                        StringComparer.OrdinalIgnoreCase);

                    var wouldDrop = Mapper.Mappings
                        .Where(m => !newConfigIds.Contains(m.DrofusFieldName))
                        .ToList();

                    if (wouldDrop.Count > 0)
                    {
                        int wouldKeep = Mapper.Mappings.Count - wouldDrop.Count;
                        var dropLabels = wouldDrop
                            .Select(m => Mapper.GetFieldLabel(m.DrofusFieldName))
                            .ToList();

                        bool confirmed = ShowConfigurationChangeConfirmation(
                            newConfig.Name,
                            dropLabels,
                            wouldKeep);

                        if (!confirmed)
                        {
                            // Revert the selector to the previous configuration.
                            _suppressConfigurationChangeHandler = true;
                            try
                            {
                                SelectedConfiguration = _previousConfigurationId == null
                                    ? null
                                    : AvailableConfigurations.FirstOrDefault(
                                        c => c.Id == _previousConfigurationId.Value);
                            }
                            finally
                            {
                                _suppressConfigurationChangeHandler = false;
                            }
                            return;
                        }
                    }
                }
            }

            // Confirmed (or no mappings would be dropped): apply the switch.
            _previousConfigurationId = Mapper.SelectedConfigurationId;
            Mapper.SelectConfiguration(newId, d);
            List<string> removed = Mapper.CleanupStaleMappings();
            Mapper.SaveMappingsToSettings(d);
            RebuildMappingRows();
            AddMappingCommand.NotifyCanExecuteChanged();

            if (removed.Count > 0)
                StatusMessage = $"{removed.Count} mapping(s) removed after configuration change: " +
                                $"{string.Join(", ", removed)}.";
        }

        /// <summary>
        /// Shows a confirmation dialog when switching configuration would drop
        /// one or more existing mappings (Scenario 5).
        /// </summary>
        /// <param name="newConfigName">The name of the configuration being switched to.</param>
        /// <param name="dropLabels">Human-readable labels of mappings that would be dropped.</param>
        /// <param name="keepCount">Number of mappings that would be kept.</param>
        /// <returns><c>true</c> if the user confirmed; <c>false</c> to cancel.</returns>
        protected virtual bool ShowConfigurationChangeConfirmation(
            string newConfigName,
            IReadOnlyList<string> dropLabels,
            int keepCount)
        {
            string dropList = string.Join(", ", dropLabels);
            string message = $"Switching to '{newConfigName}' will remove " +
                             $"{dropLabels.Count} mapping(s): {dropList}. " +
                             $"{keepCount} mapping(s) will be kept. Continue?";

            return System.Windows.MessageBox.Show(
                message,
                "Confirm configuration change",
                System.Windows.MessageBoxButton.YesNo,
                System.Windows.MessageBoxImage.Warning) == System.Windows.MessageBoxResult.Yes;
        }

        // ── Mapping commands ──────────────────────────────────────────────────

        [RelayCommand(CanExecute = nameof(CanAddMapping))]
        private void AddMapping()
        {
            bool hasExistingId = Mapper.Mappings.Any(m => m.IsUniqueId);

            // Exclude drofus fields already claimed by an existing mapping.
            var usedFields = new HashSet<string>(
                Mapper.Mappings.Select(m => m.DrofusFieldName),
                StringComparer.OrdinalIgnoreCase);

            // Use the configuration-scoped field list so the dialog only shows
            // fields relevant to the active configuration.
            var availableFields = Mapper.GetFieldsForSelectedConfiguration()
                .Where(f => !usedFields.Contains(f.Id))
                .ToList();

            // Exclude Revit parameters already claimed by an existing mapping.
            var usedParams = new HashSet<string>(
                Mapper.Mappings.Select(m => m.RevitParameterName),
                StringComparer.OrdinalIgnoreCase);
            var availableParams = _availableRevitParameters
                .Where(p => !usedParams.Contains(p.ParameterName))
                .ToList();

            var dialogVm = new DrofusPropertyMappingDialogViewModel(
                availableFields,
                availableParams,
                hasExistingId,
                Mapper,
                Mapper.SelectedConfigurationId);

            if (!ShowMappingDialog(dialogVm)) return;
            if (dialogVm.CreatedMapping is null) return;

            if (!Mapper.AddMapping(dialogVm.CreatedMapping)) return;
            PersistAndRefresh();
        }

        private bool CanAddMapping() => HasAvailableFields && HasConfigurations;

        partial void OnIsConnectedChanged(bool value)
        {
            // IsConnected changing also implies fields/configurations may have changed.
            AddMappingCommand.NotifyCanExecuteChanged();
            EditMappingCommand.NotifyCanExecuteChanged();
            RemoveMappingCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Called by <c>Main</c> on the dispatcher thread after
        /// <see cref="ValidateDrofusOnStartup"/> completes — whether or not
        /// rooms were loaded. Rebuilds the configuration selector and mapping-row
        /// validation indicators from the startup caches.
        /// </summary>
        public void OnStartupCompleted()
        {
            var d = _settings.Drofus;
            if (d is null) return;

            // Rebuild configuration selector from startup cache.
            if (d.StartupAttributeConfigurations.Count > 0)
            {
                Mapper.UpdateAvailableConfigurations(d.StartupAttributeConfigurations);
                RebuildConfigurationSelector(d.SelectedAttributeConfigurationId);
                OnPropertyChanged(nameof(HasConfigurations));
            }

            RefreshMappingRowValidationState();
            HasValidationWarnings = Mapper.HasValidationWarnings;
            AddMappingCommand.NotifyCanExecuteChanged();

            // Gap 9: if startup failed to connect, surface degraded state.
            // IsDrofusOffline is set here when the mapper has no available fields
            // after startup — the catalogue fetch failed (Gap 1 path in
            // ValidateDrofusOnStartup returns early without populating fields).
            if (Mapper.AvailableFields.Count == 0 && d.PropertyMappings.Count > 0)
            {
                IsDrofusOffline = true;
                StatusMessage = "Could not connect to drofus at startup. " +
                                "Existing mappings are preserved. Reconnect to load room data.";
            }
        }

        [RelayCommand(CanExecute = nameof(CanEditOrRemoveMapping))]
        private void EditMapping()
        {
            if (SelectedMappingRow is null) return;

            bool hasExistingId = Mapper.Mappings
                .Any(m => m.IsUniqueId && m != SelectedMappingRow.Model);

            // Exclude fields claimed by other mappings (not the one being edited).
            var usedFields = new HashSet<string>(
                Mapper.Mappings
                    .Where(m => m != SelectedMappingRow.Model)
                    .Select(m => m.DrofusFieldName),
                StringComparer.OrdinalIgnoreCase);

            var availableFields = Mapper.GetFieldsForSelectedConfiguration()
                .Where(f => !usedFields.Contains(f.Id))
                .ToList();

            // Exclude Revit parameters claimed by other mappings (not the one being edited).
            var usedParams = new HashSet<string>(
                Mapper.Mappings
                    .Where(m => m != SelectedMappingRow.Model)
                    .Select(m => m.RevitParameterName),
                StringComparer.OrdinalIgnoreCase);
            var availableParams = _availableRevitParameters
                .Where(p => !usedParams.Contains(p.ParameterName))
                .ToList();

            var dialogVm = new DrofusPropertyMappingDialogViewModel(
                availableFields,
                availableParams,
                SelectedMappingRow.Model,
                hasExistingId,
                Mapper,
                Mapper.SelectedConfigurationId);

            if (!ShowMappingDialog(dialogVm)) return;
            if (dialogVm.CreatedMapping is null) return;

            DrofusPropertyMap target = SelectedMappingRow.Model;
            target.DrofusFieldName = dialogVm.CreatedMapping.DrofusFieldName;
            target.RevitParameterName = dialogVm.CreatedMapping.RevitParameterName;
            target.RevitParameterGuid = dialogVm.CreatedMapping.RevitParameterGuid;
            target.FlowDirection = dialogVm.CreatedMapping.FlowDirection;
            target.IsUniqueId = dialogVm.CreatedMapping.IsUniqueId;

            PersistAndRefresh();
        }

        [RelayCommand(CanExecute = nameof(CanEditOrRemoveMapping))]
        private void RemoveMapping()
        {
            if (SelectedMappingRow is null) return;
            Mapper.RemoveMapping(SelectedMappingRow.Model);
            PersistAndRefresh();
        }

        private bool CanEditOrRemoveMapping()
            => SelectedMappingRow is not null;

        partial void OnSelectedMappingRowChanged(DrofusPropertyMapViewModel? value)
        {
            EditMappingCommand.NotifyCanExecuteChanged();
            RemoveMappingCommand.NotifyCanExecuteChanged();
        }

        // ── Settings persistence ──────────────────────────────────────────────

        public void SaveToSettings()
        {
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.BaseUrl = BaseUrl.Trim();
            _settings.Drofus.DatabaseName = DatabaseName.Trim();
            _settings.Drofus.ProjectNumber = ProjectNumber.Trim();
            _settings.Drofus.ApiToken = ApiToken.Trim();
            Mapper.SaveMappingsToSettings(_settings.Drofus);
            SaveRevitPrecedenceToSettings();
        }

        /// <summary>
        /// Persists the current per-row RevitTakesPrecedenceAfterInitialPush checkboxes
        /// into <see cref="DrofusDataSourceSettings.RevitPrecedencePropertyNames"/>.
        /// Called by <see cref="SaveToSettings"/> and <see cref="PersistAndRefresh"/>.
        /// </summary>
        private void SaveRevitPrecedenceToSettings()
        {
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.RevitPrecedencePropertyNames = MappingRows
                .Where(r => r.RevitTakesPrecedenceAfterInitialPush)
                .Select(r => r.Model.RevitParameterName)
                .ToList();
        }

        /// <summary>
        /// Serialises the full live settings object to a user-chosen .json file
        /// so that team members can share drofus project configurations.
        /// The file format is identical to the default startup settings file.
        /// </summary>
        [RelayCommand]
        private void SaveSettingsToFile()
        {
            SaveToSettings();

            using var dialog = new System.Windows.Forms.SaveFileDialog
            {
                Title = "Save drofus settings",
                Filter = "JSON settings files (*.json)|*.json|All files (*.*)|*.*",
                FilterIndex = 1,
                DefaultExt = "json",
                FileName = "pushIt_drofus_settings.json",
            };

            if (dialog.ShowDialog() != System.Windows.Forms.DialogResult.OK) return;

            var wrapper = new Models.Settings
            {
                DataSource = new Models.DataSourceSettings
                {
                    SourceType = Models.DataSourceType.Drofus,
                    Drofus = _settings.Drofus,
                }
            };

            Utilities.SettingsUtils.SaveSettingsToPath(wrapper, dialog.FileName);
        }

        /// <summary>
        /// Loads the drofus block from a user-chosen .json file and applies it
        /// to the live settings, replacing only the drofus configuration.
        /// All other settings (categories, column layout, CSV config) are untouched.
        /// </summary>
        [RelayCommand]
        private void LoadSettingsFromFile()
        {
            using var dialog = new System.Windows.Forms.OpenFileDialog
            {
                Title = "Load drofus settings",
                Filter = "JSON settings files (*.json)|*.json|All files (*.*)|*.*",
                FilterIndex = 1,
                CheckFileExists = true,
            };

            if (dialog.ShowDialog() != System.Windows.Forms.DialogResult.OK) return;

            Models.Drofus.DrofusDataSourceSettings? loaded =
                Utilities.SettingsUtils.LoadDrofusSettingsFromPath(dialog.FileName);

            if (loaded is null) return;

            ApplyDrofusSettings(loaded);
        }

        /// <summary>
        /// Replaces the live drofus configuration with <paramref name="drofus"/>
        /// and refreshes all observable properties and the mapping list.
        /// Used by <see cref="LoadSettingsFromFile"/> and could be reused for
        /// any future path that injects a new drofus config at runtime.
        /// </summary>
        private void ApplyDrofusSettings(Models.Drofus.DrofusDataSourceSettings drofus)
        {
            _settings.Drofus = drofus;

            BaseUrl = drofus.BaseUrl;
            DatabaseName = drofus.DatabaseName;
            ProjectNumber = drofus.ProjectNumber;
            ApiToken = drofus.ApiToken;

            IsConnected = false;
            IsDrofusOffline = false;
            StatusMessage = "Settings loaded — click Connect to verify.";

            Mapper.ReplaceMappings(drofus.PropertyMappings);
            PersistAndRefresh();
        }

        // ── Private UI helpers ────────────────────────────────────────────────

        /// <summary>
        /// Rebuilds <see cref="AvailableConfigurations"/> from the mapper and
        /// restores the selected item to the configuration whose id matches
        /// <paramref name="selectedId"/>.
        /// </summary>
        private void RebuildConfigurationSelector(int? selectedId)
        {
            _suppressConfigurationChangeHandler = true;
            try
            {
                AvailableConfigurations.Clear();
                foreach (var config in Mapper.AvailableConfigurations)
                    AvailableConfigurations.Add(config);

                SelectedConfiguration = selectedId == null
                    ? null
                    : AvailableConfigurations.FirstOrDefault(c => c.Id == selectedId.Value);

                _previousConfigurationId = selectedId;
            }
            finally
            {
                _suppressConfigurationChangeHandler = false;
            }
        }

        private void RebuildMappingRows()
        {
            var precedenceSet = new HashSet<string>(
                _settings.Drofus?.RevitPrecedencePropertyNames ?? new List<string>(),
                StringComparer.OrdinalIgnoreCase);

            MappingRows.Clear();
            foreach (DrofusPropertyMap mapping in Mapper.Mappings)
            {
                var row = new DrofusPropertyMapViewModel(mapping, Mapper);
                row.RevitTakesPrecedenceAfterInitialPush = precedenceSet.Contains(mapping.RevitParameterName);
                MappingRows.Add(row);
            }
            HasValidationWarnings = Mapper.HasValidationWarnings;
        }

        private void RefreshMappingRowValidationState()
        {
            foreach (DrofusPropertyMapViewModel row in MappingRows)
                row.RefreshValidationState(Mapper);
        }

        private void PersistAndRefresh()
        {
            Mapper.SaveMappingsToSettings(_settings.Drofus!);
            SaveRevitPrecedenceToSettings();
            SyncParametersToDataModel();
            RebuildMappingRows();
        }

        /// <summary>
        /// Rebuilds the data model's parameter store from the current mappings list
        /// so that <c>VerifyParametersInModel</c> always reflects the latest set of
        /// mapped Revit parameters.
        /// </summary>
        private void SyncParametersToDataModel()
        {
            if (_revitDataModel is null) return;

            _revitDataModel.ClearParameters();
            foreach (DrofusPropertyMap mapping in Mapper.Mappings)
            {
                _revitDataModel.AddParameter(new Models.RoomDataProperty(
                    name: mapping.RevitParameterName,
                    parameterGUID: mapping.RevitParameterGuid,
                    parameterName: mapping.RevitParameterName,
                    value: string.Empty,
                    showInUI: true,
                    isReadOnly: false,
                    isUniqueId: mapping.IsUniqueId));
            }
        }

        protected virtual bool ShowMappingDialog(DrofusPropertyMappingDialogViewModel dialogVm)
        {
            var window = new Views.DataSource.Drofus.DrofusPropertyMappingDialog
            {
                DataContext = dialogVm,
            };

            System.Windows.Window? owner = null;
            if (System.Windows.Application.Current != null)
            {
                foreach (System.Windows.Window w in System.Windows.Application.Current.Windows)
                {
                    if (w.IsLoaded && w.IsVisible) { owner = w; break; }
                }
            }

            if (owner != null) window.Owner = owner;

            dialogVm.RequestClose += (_, _) => window.Close();
            window.ShowDialog();
            return true;
        }
    }
}
