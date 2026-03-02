// BSD License - Copyright 2025, Jan Christel

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Utilities;
using System;

namespace duHastNet.PushIt.ViewModels.DataSource
{
    /// <summary>
    /// Child ViewModel for the drofus PoC data source panel.
    ///
    /// Holds the four fields the user must supply (BaseUrl, DatabaseName,
    /// ProjectNumber, ApiToken) and runs a synchronous connection test via
    /// DrofusDataSource when the user clicks Connect.
    ///
    /// The Connect command is synchronous — the HTTP call uses blocking
    /// WebRequest so no async machinery is needed or wanted here.
    /// </summary>
    public partial class DrofusDataSourceControlViewModel : ObservableObject
    {
        private readonly DataSourceSettings _settings;

        // ── Observable properties ─────────────────────────────────────────────

        [ObservableProperty]
        private string _baseUrl = string.Empty;

        [ObservableProperty]
        private string _databaseName = string.Empty;

        [ObservableProperty]
        private string _projectNumber = string.Empty;

        [ObservableProperty]
        private string _apiToken = string.Empty;

        [ObservableProperty]
        private string _statusMessage = string.Empty;

        [ObservableProperty]
        private bool _isConnected;

        [ObservableProperty]
        private bool _isConnecting;

        // ── Constructor ───────────────────────────────────────────────────────

        public DrofusDataSourceControlViewModel(DataSourceSettings settings)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));

            // Restore previously saved values
            var d = settings.Drofus;
            if (d != null)
            {
                _baseUrl = d.BaseUrl;
                _databaseName = d.DatabaseName;
                _projectNumber = d.ProjectNumber;
                _apiToken = d.ApiToken;
                _isConnected = d.IsConnected;
                _statusMessage = d.IsConnected
                    ? $"Connected — {d.LastRoomCount} rooms found."
                    : string.Empty;
            }
        }

        // ── Connect command ───────────────────────────────────────────────────

        [RelayCommand(CanExecute = nameof(CanConnect))]
        private void Connect()
        {
            // Write current UI values into settings before calling the data source
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.BaseUrl = BaseUrl.Trim();
            _settings.Drofus.DatabaseName = DatabaseName.Trim();
            _settings.Drofus.ProjectNumber = ProjectNumber.Trim();
            _settings.Drofus.ApiToken = ApiToken.Trim();
            _settings.Drofus.IsConnected = false;

            IsConnecting = true;
            StatusMessage = "Connecting…";

            try
            {
                var dataSource = new DrofusDataSource();

                if (!dataSource.Validate(_settings, out string validationError))
                {
                    StatusMessage = validationError;
                    IsConnected = false;
                    return;
                }

                // Synchronous — returns empty list (PoC) but sets LastRoomCount
                dataSource.GetRoomsData(_settings);

                int count = _settings.Drofus.LastRoomCount;
                IsConnected = true;
                StatusMessage = $"Connected — {count} rooms found.";
            }
            catch (Exception ex)
            {
                IsConnected = false;
                _settings.Drofus.IsConnected = false;
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

        // Re-evaluate CanExecute when any field changes
        partial void OnBaseUrlChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnDatabaseNameChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnProjectNumberChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnApiTokenChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();

        // ── SaveToSettings ────────────────────────────────────────────────────

        /// <summary>
        /// Called by the host DataSourceViewModel before saving settings to disk.
        /// </summary>
        public void SaveToSettings()
        {
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.BaseUrl = BaseUrl.Trim();
            _settings.Drofus.DatabaseName = DatabaseName.Trim();
            _settings.Drofus.ProjectNumber = ProjectNumber.Trim();
            _settings.Drofus.ApiToken = ApiToken.Trim();
        }
    }
}