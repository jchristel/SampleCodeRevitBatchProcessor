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
    /// Responsibilities:
    ///   - Hold ApiToken and DatabaseName entered by the user.
    ///   - Run a synchronous connection test via <see cref="DrofusDataSource"/> when
    ///     the user clicks Connect (synchronous because we may be inside a Revit context).
    ///   - Surface a plain-text status message showing the room count or an error.
    ///   - Write the result back to <see cref="DrofusDataSourceSettings"/> so
    ///     RevitDataModel picks it up automatically on the next Load.
    ///
    /// The Connect command deliberately does NOT call RevitTask.RunAsync — it is
    /// triggered from the UI thread by a button click, not from inside a Revit event.
    /// The HTTP call itself is synchronous (WebRequest), so no async machinery is needed.
    /// </summary>
    public partial class DrofusDataSourceControlViewModel : ObservableObject
    {
        private readonly DataSourceSettings _settings;

        // ── Observable properties ─────────────────────────────────────────────

        [ObservableProperty]
        private string _apiToken = string.Empty;

        [ObservableProperty]
        private string _databaseName = string.Empty;

        [ObservableProperty]
        private string _statusMessage = string.Empty;

        [ObservableProperty]
        private bool _isConnected;

        [ObservableProperty]
        private bool _isConnecting;

        // ── Constructor ───────────────────────────────────────────────────────

        /// <param name="settings">
        /// The live <see cref="DataSourceSettings"/> object from the model.
        /// Populated from persisted values on construction; written back on Connect.
        /// </param>
        public DrofusDataSourceControlViewModel(DataSourceSettings settings)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));

            // Restore previously saved values so the user does not have to re-enter them
            var d = settings.Drofus;
            if (d != null)
            {
                _apiToken = d.ApiToken;
                _databaseName = d.DatabaseName;
                _isConnected = d.IsConnected;
                _statusMessage = d.IsConnected
                    ? $"Connected — {d.LastRoomCount} rooms found."
                    : string.Empty;
            }
        }

        // ── Connect command ───────────────────────────────────────────────────

        /// <summary>
        /// Tests the connection synchronously.  Safe to call from the UI thread —
        /// the HTTP call uses WebRequest.GetResponse() (blocking, no async).
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanConnect))]
        private void Connect()
        {
            // Write current UI values into settings so DrofusDataSource reads them
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.ApiToken    = ApiToken.Trim();
            _settings.Drofus.DatabaseName = DatabaseName.Trim();
            _settings.Drofus.IsConnected  = false;

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

                // Synchronous call — returns empty list (PoC), but sets LastRoomCount
                dataSource.GetRoomsData(_settings);

                int count = _settings.Drofus.LastRoomCount;
                IsConnected = true;
                StatusMessage = $"Connected — {count} rooms found.";
            }
            catch (Exception ex)
            {
                IsConnected = false;
                _settings.Drofus.IsConnected = false;
                StatusMessage = ex.Message; // InvalidOperationException messages are user-readable
            }
            finally
            {
                IsConnecting = false;
                ConnectCommand.NotifyCanExecuteChanged();
            }
        }

        private bool CanConnect()
            => !IsConnecting
            && !string.IsNullOrWhiteSpace(ApiToken)
            && !string.IsNullOrWhiteSpace(DatabaseName);

        // Re-evaluate CanExecute when the text fields change
        partial void OnApiTokenChanged(string value)     => ConnectCommand.NotifyCanExecuteChanged();
        partial void OnDatabaseNameChanged(string value) => ConnectCommand.NotifyCanExecuteChanged();

        // ── SaveToSettings ────────────────────────────────────────────────────

        /// <summary>
        /// Called by the host ViewModel before saving settings to disk.
        /// Ensures the latest UI values are written back even if Connect was not pressed.
        /// </summary>
        public void SaveToSettings()
        {
            _settings.Drofus ??= new DrofusDataSourceSettings();
            _settings.Drofus.ApiToken    = ApiToken.Trim();
            _settings.Drofus.DatabaseName = DatabaseName.Trim();
            // IsConnected and LastRoomCount are already kept in sync by Connect()
        }
    }
}
