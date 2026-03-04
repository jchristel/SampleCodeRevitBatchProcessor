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

namespace duHastNet.PushIt.ViewModels.DataSource
{
    /// <summary>
    /// Child ViewModel for the drofus data source configuration panel.
    /// Owns the four connection fields, the Connect command, the
    /// <see cref="DrofusPropertyMapper"/> service instance, and the
    /// <see cref="MappingRows"/> collection that drives the mapping ListView.
    /// The Connect command is synchronous — all HTTP calls use blocking
    /// WebRequest so no async machinery is needed in this ViewModel.
    /// </summary>
    public partial class DrofusDataSourceControlViewModel : ObservableObject
    {
        private readonly DataSourceSettings _settings;

        /// <summary>
        /// Reference to the data model used to keep the parameter store in sync
        /// with the current mappings list. Set by Main after construction.
        /// When non-null, <c>PersistAndRefresh</c> rebuilds the parameter store
        /// from the active mappings so <c>VerifyParametersInModel</c> always
        /// sees the latest set of mapped Revit parameters.
        /// </summary>
        public RevitDataModel? RevitDataModel { get; set; }

        /// <summary>
        /// The mapper service instance. Exposed publicly so that
        /// ValidateDrofusMappingsOnStartup can receive it from Main.ExecuteInternal.
        /// </summary>
        public DrofusPropertyMapper Mapper { get; }

        /// <summary>
        /// Revit shared parameters available in the current document.
        /// Set by Main after construction from RevitDataModel.GetAllAvailableParameters().
        /// Passed into the Add/Edit dialog for the parameter ComboBox.
        /// </summary>
        public IReadOnlyList<AvailableParameter> AvailableRevitParameters { get; set; }
            = Array.Empty<AvailableParameter>();

        /// <summary>
        /// <c>true</c> when the mapper has at least one available drofus field —
        /// meaning a successful API connection has been made either during the
        /// current session (Connect button) or during startup (no-mappings path).
        /// Used as the CanExecute condition for AddMapping so the user can set up
        /// mappings as soon as fields are known, without requiring IsConnected.
        /// </summary>
        public bool HasAvailableFields => Mapper.AvailableFields.Count > 0;

        [ObservableProperty] private string _baseUrl = string.Empty;
        [ObservableProperty] private string _databaseName = string.Empty;
        [ObservableProperty] private string _projectNumber = string.Empty;
        [ObservableProperty] private string _apiToken = string.Empty;
        [ObservableProperty] private string _statusMessage = string.Empty;
        [ObservableProperty] private bool _isConnected;
        [ObservableProperty] private bool _isConnecting;

        public ObservableCollection<DrofusPropertyMapViewModel> MappingRows { get; }
            = new ObservableCollection<DrofusPropertyMapViewModel>();

        [ObservableProperty] private DrofusPropertyMapViewModel? _selectedMappingRow;
        [ObservableProperty] private bool _hasValidationWarnings;

        public DrofusDataSourceControlViewModel(DataSourceSettings settings)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));
            _settings.Drofus ??= new DrofusDataSourceSettings();
            var d = _settings.Drofus;

            _baseUrl       = d.BaseUrl;
            _databaseName  = d.DatabaseName;
            _projectNumber = d.ProjectNumber;
            _apiToken      = d.ApiToken;
            _isConnected   = d.IsConnected;
            _statusMessage = d.IsConnected ? $"Connected - {d.LastRoomCount} rooms found." : string.Empty;

            Mapper = new DrofusPropertyMapper(d.PropertyMappings);
            RebuildMappingRows();
        }

        [RelayCommand(CanExecute = nameof(CanConnect))]
        private void Connect()
        {
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.BaseUrl       = BaseUrl.Trim();
            _settings.Drofus.DatabaseName  = DatabaseName.Trim();
            _settings.Drofus.ProjectNumber = ProjectNumber.Trim();
            _settings.Drofus.ApiToken      = ApiToken.Trim();
            _settings.Drofus.IsConnected   = false;

            IsConnecting  = true;
            StatusMessage = "Connecting...";

            try
            {
                var dataSource = new DrofusDataSource();

                if (!dataSource.Validate(_settings, out string validationError))
                {
                    StatusMessage = validationError;
                    IsConnected   = false;
                    return;
                }

                List<string> fields = dataSource.GetAvailableFields(_settings);
                int count = _settings.Drofus.LastRoomCount;
                IsConnected = true;

                Mapper.UpdateAvailableFields(fields);
                List<string> removed = Mapper.CleanupStaleMappings();
                Mapper.SaveMappingsToSettings(_settings.Drofus);
                RebuildMappingRows();

                string baseStatus = $"Connected - {count} rooms found.";
                StatusMessage = removed.Count == 0
                    ? baseStatus
                    : $"{baseStatus} {removed.Count} stale mapping(s) removed: {string.Join(", ", removed)}.";
            }
            catch (Exception ex)
            {
                IsConnected = false;
                _settings.Drofus!.IsConnected = false;
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

        partial void OnBaseUrlChanged(string value)       => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnDatabaseNameChanged(string value)  => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnProjectNumberChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnApiTokenChanged(string value)      => ConnectCommand.NotifyCanExecuteChanged();

        [RelayCommand(CanExecute = nameof(CanAddMapping))]
        private void AddMapping()
        {
            bool hasExistingId = Mapper.Mappings.Any(m => m.IsUniqueId);

            // Exclude drofus fields already claimed by an existing mapping.
            var usedFields = new HashSet<string>(
                Mapper.Mappings.Select(m => m.DrofusFieldName),
                StringComparer.OrdinalIgnoreCase);
            var availableFields = Mapper.AvailableFields
                .Where(f => !usedFields.Contains(f))
                .ToList();

            // Exclude Revit parameters already claimed by an existing mapping.
            var usedParams = new HashSet<string>(
                Mapper.Mappings.Select(m => m.RevitParameterName),
                StringComparer.OrdinalIgnoreCase);
            var availableParams = AvailableRevitParameters
                .Where(p => !usedParams.Contains(p.ParameterName))
                .ToList();

            var dialogVm = new DrofusPropertyMappingDialogViewModel(
                availableFields,
                availableParams,
                hasExistingId);

            if (!ShowMappingDialog(dialogVm)) return;
            if (dialogVm.CreatedMapping is null) return;

            if (!Mapper.AddMapping(dialogVm.CreatedMapping)) return;
            PersistAndRefresh();
        }

        private bool CanAddMapping() => HasAvailableFields;

        partial void OnIsConnectedChanged(bool value)
        {
            // IsConnected changing also implies fields may now be available.
            AddMappingCommand.NotifyCanExecuteChanged();
            EditMappingCommand.NotifyCanExecuteChanged();
            RemoveMappingCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Called by Main after the no-mappings startup path has successfully
        /// queried the drofus API and populated AvailableFields on the mapper.
        /// Sets IsConnected so the UI reflects the live connection state and
        /// notifies commands that depend on HasAvailableFields.
        /// </summary>
        public void OnStartupFieldsLoaded()
        {
            IsConnected = true;
            AddMappingCommand.NotifyCanExecuteChanged();
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
            var availableFields = Mapper.AvailableFields
                .Where(f => !usedFields.Contains(f))
                .ToList();

            // Exclude Revit parameters claimed by other mappings (not the one being edited).
            var usedParams = new HashSet<string>(
                Mapper.Mappings
                    .Where(m => m != SelectedMappingRow.Model)
                    .Select(m => m.RevitParameterName),
                StringComparer.OrdinalIgnoreCase);
            var availableParams = AvailableRevitParameters
                .Where(p => !usedParams.Contains(p.ParameterName))
                .ToList();

            var dialogVm = new DrofusPropertyMappingDialogViewModel(
                availableFields,
                availableParams,
                SelectedMappingRow.Model,
                hasExistingId);

            if (!ShowMappingDialog(dialogVm)) return;
            if (dialogVm.CreatedMapping is null) return;

            DrofusPropertyMap target = SelectedMappingRow.Model;
            target.DrofusFieldName    = dialogVm.CreatedMapping.DrofusFieldName;
            target.RevitParameterName = dialogVm.CreatedMapping.RevitParameterName;
            target.RevitParameterGuid = dialogVm.CreatedMapping.RevitParameterGuid;
            target.FlowDirection      = dialogVm.CreatedMapping.FlowDirection;
            target.IsUniqueId         = dialogVm.CreatedMapping.IsUniqueId;

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
            => IsConnected && SelectedMappingRow is not null;

        partial void OnSelectedMappingRowChanged(DrofusPropertyMapViewModel? value)
        {
            EditMappingCommand.NotifyCanExecuteChanged();
            RemoveMappingCommand.NotifyCanExecuteChanged();
        }

        public void OnStartupValidationCompleted()
        {
            RefreshMappingRowValidationState();
            HasValidationWarnings = Mapper.HasValidationWarnings;
        }

        public void SaveToSettings()
        {
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.BaseUrl       = BaseUrl.Trim();
            _settings.Drofus.DatabaseName  = DatabaseName.Trim();
            _settings.Drofus.ProjectNumber = ProjectNumber.Trim();
            _settings.Drofus.ApiToken      = ApiToken.Trim();
            Mapper.SaveMappingsToSettings(_settings.Drofus);
        }

        private void RebuildMappingRows()
        {
            MappingRows.Clear();
            foreach (DrofusPropertyMap mapping in Mapper.Mappings)
                MappingRows.Add(new DrofusPropertyMapViewModel(mapping, Mapper));
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
            SyncParametersToDataModel();
            RebuildMappingRows();
        }

        /// <summary>
        /// Rebuilds the data model's parameter store from the current mappings list
        /// so that <c>VerifyParametersInModel</c> always reflects the latest set of
        /// mapped Revit parameters.
        /// <para>
        /// Called after every Add, Edit, or Remove operation. No-ops when
        /// <see cref="RevitDataModel"/> has not been injected.
        /// </para>
        /// </summary>
        private void SyncParametersToDataModel()
        {
            if (RevitDataModel is null) return;

            RevitDataModel.ClearParameters();
            foreach (DrofusPropertyMap mapping in Mapper.Mappings)
            {
                RevitDataModel.AddParameter(new Models.RoomDataProperty(
                    name:          mapping.RevitParameterName,
                    parameterGUID: mapping.RevitParameterGuid,
                    parameterName: mapping.RevitParameterName,
                    value:         string.Empty,
                    showInUI:      true,
                    isReadOnly:    false,
                    isUniqueId:    mapping.IsUniqueId));
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
