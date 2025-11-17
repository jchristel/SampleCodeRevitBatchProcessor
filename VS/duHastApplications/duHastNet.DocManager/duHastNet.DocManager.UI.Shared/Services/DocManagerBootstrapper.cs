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

using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.MetaData;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Stores;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels;
using duHastNet.DocManager.UI.Shared.Views;
using System.Windows;

namespace duHastNet.DocManager.UI.Shared.Services;

/// <summary>
/// Bootstrapper class that initializes and wires up the entire DocManager application
/// Can be used from Standalone WPF app, PyRevit, or Revit Add-in
/// </summary>
public class DocManagerBootstrapper : IDisposable
{
    #region Private Fields - Singleton instances for application lifetime

    private DocManagerApi? _docManagerApi;
    private Manager? _manager;
    private MessageStore? _messageStore;
    private SettingsService? _settingsService;
    private NavigationStore? _navigationStore;
    private IDialogService? _dialogService;
    private duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManager? _currentFolderManager;
    private CloudDocumentManager? _cloudDocumentManager;
    private Window? _mainWindow;
    private bool _disposed = false;

    #endregion

    #region Public Properties

    /// <summary>
    /// Gets whether the bootstrapper has been initialized
    /// </summary>
    public bool IsInitialized { get; private set; }

    /// <summary>
    /// Gets the DocManagerApi instance (available after initialization)
    /// </summary>
    public DocManagerApi? DocManagerApi => _docManagerApi;

    /// <summary>
    /// Gets the Manager instance (available after initialization)
    /// </summary>
    public Manager? Manager => _manager;

    /// <summary>
    /// Gets the MessageStore instance (available after initialization)
    /// </summary>
    public MessageStore? MessageStore => _messageStore;

    #endregion

    #region Initialization Methods

    /// <summary>
    /// Initializes the DocManager application asynchronously
    /// Creates all services, loads settings, connects to database, and creates main window
    /// </summary>
    /// <returns>The main window ready to be shown</returns>
    public async Task<Window> InitializeAsync()
    {
        if (IsInitialized)
        {
            throw new InvalidOperationException("Bootstrapper has already been initialized. Create a new instance to initialize again.");
        }

        // Initialize the settings service (singleton for application lifetime)
        _settingsService = new SettingsService();

        // Initialize the API service (singleton for application lifetime)
        _docManagerApi = new DocManagerApi();

        // Initialize MessageStore (singleton for application lifetime)
        _messageStore = new MessageStore();

        // Initialize NavigationStore (singleton for application lifetime)
        _navigationStore = new NavigationStore();

        // Initialize DialogService (singleton for application lifetime)
        _dialogService = new DialogService();

        // Load settings from JSON files
        var (databaseConnectionSettings, currentFolderManagerSettings, cloudDocumentManager) = await LoadSettingsAsync();

        _cloudDocumentManager = cloudDocumentManager;

        // Initialize Manager (singleton for application lifetime)
        // Manager starts empty - will be populated after database connection
        // Pass loaded CloudDocumentManager
        _manager = new Manager(_cloudDocumentManager);

        // Create CurrentFolderManager with loaded settings
        _currentFolderManager = new duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManager(currentFolderManagerSettings);

        // Attempt to connect to saved database if path exists
        await ConnectToSavedDatabaseAsync(databaseConnectionSettings);

        // Create the NavigationHostViewModel
        var navigationHostViewModel = new NavigationHostViewModel(
            docManagerApi: _docManagerApi,
            manager: _manager,
            currentFolderManager: _currentFolderManager,
            messageStore: _messageStore,
            navigationStore: _navigationStore,
            dialogService: _dialogService);

        // Create the NavigationHostView (UserControl)
        var navigationHostView = new NavigationHostView()
        {
            DataContext = navigationHostViewModel
        };

        // Create a Window to host the NavigationHostView
        _mainWindow = new Window()
        {
            Title = "DocManager",
            Content = navigationHostView,
            Width = 1200,
            Height = 800,
            WindowStartupLocation = WindowStartupLocation.CenterScreen
        };

        // Subscribe to the Closed event to ensure proper cleanup
        _mainWindow.Closed += MainWindow_Closed;

        // Subscribe to Closing event to notify ViewModel
        _mainWindow.Closing += (s, e) =>
        {
            if (navigationHostViewModel is ICloseable closeable)
            {
                closeable.OnClosing();
            }
        };

        IsInitialized = true;

        return _mainWindow;
    }

    /// <summary>
    /// Initializes the DocManager application synchronously (for IronPython compatibility)
    /// Creates all services, loads settings, connects to database, and creates main window
    /// </summary>
    /// <returns>The main window ready to be shown</returns>
    public Window Initialize()
    {
        return InitializeAsync().GetAwaiter().GetResult();
    }

    #endregion

    #region Settings Management

    /// <summary>
    /// Loads settings from JSON files, creating default instances if files don't exist
    /// </summary>
    /// <returns>Tuple containing DatabaseConnectionSettings, CurrentFolderManagerSettings, and CloudDocumentManager</returns>
    private async Task<(DatabaseConnectionSettings, duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings, CloudDocumentManager)> LoadSettingsAsync()
    {
        DatabaseConnectionSettings? databaseConnectionSettings = null;
        duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings? currentFolderManagerSettings = null;
        CloudDocumentManager? cloudDocumentManager = null;

        try
        {
            // Load DatabaseConnectionSettings
            databaseConnectionSettings = await _settingsService!.LoadAsync<DatabaseConnectionSettings>(
                SettingsFileNames.DatabaseConnection);

            if (databaseConnectionSettings == null)
            {
                // First run - create default empty settings
                databaseConnectionSettings = new DatabaseConnectionSettings();

                // Log to message store that default settings were created
                _messageStore?.SetCurrentMessage(
                    $"{SettingsFileNames.DatabaseConnection} not found. Created default empty settings.",
                    MessageTypes.Information);
            }
            else
            {
                // Settings loaded successfully
                _messageStore?.SetCurrentMessage(
                    "DatabaseConnection settings loaded successfully.",
                    MessageTypes.Information);
            }
        }
        catch (Exception ex)
        {
            // Error loading settings - create defaults and log error
            databaseConnectionSettings = new DatabaseConnectionSettings();

            _messageStore?.SetCurrentMessage(
                $"Error loading DatabaseConnection settings: {ex.Message}. Using default settings.",
                MessageTypes.Error);
        }

        try
        {
            // Load CurrentFolderManagerSettings
            currentFolderManagerSettings = await _settingsService!.LoadAsync<duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings>(
                SettingsFileNames.CurrentFolderManager);

            if (currentFolderManagerSettings == null)
            {
                // First run - create default empty settings
                currentFolderManagerSettings = new duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings();

                // Log to message store that default settings were created
                _messageStore?.SetCurrentMessage(
                    $"{SettingsFileNames.CurrentFolderManager} not found. Created default empty settings.",
                    MessageTypes.Information);
            }
            else
            {
                // Settings loaded successfully
                _messageStore?.SetCurrentMessage(
                    "CurrentFolderManagerSettings loaded successfully.",
                    MessageTypes.Information);
            }
        }
        catch (Exception ex)
        {
            // Error loading settings - create defaults and log error
            currentFolderManagerSettings = new duHastNet.DocManager.Core.Models.CurrentFolder.CurrentFolderManagerSettings();

            _messageStore?.SetCurrentMessage(
                $"Error loading CurrentFolderManagerSettings: {ex.Message}. Using default settings.",
                MessageTypes.Error);
        }

        try
        {
            // Load CloudDocumentManager
            cloudDocumentManager = await _settingsService!.LoadAsync<CloudDocumentManager>(
                SettingsFileNames.CloudDocumentManager);

            if (cloudDocumentManager == null)
            {
                // First run - create default empty mapper
                cloudDocumentManager = new CloudDocumentManager();

                // Log to message store that default mapper was created
                _messageStore?.SetCurrentMessage(
                    $"{SettingsFileNames.CloudDocumentManager} not found. Created default empty mapper.",
                    MessageTypes.Information);
            }
            else
            {
                // Settings loaded successfully
                _messageStore?.SetCurrentMessage(
                    "CloudDocumentManager loaded successfully.",
                    MessageTypes.Information);
            }
        }
        catch (Exception ex)
        {
            // Error loading settings - create defaults and log error
            cloudDocumentManager = new CloudDocumentManager();

            _messageStore?.SetCurrentMessage(
                $"Error loading CloudDocumentManager: {ex.Message}. Using default mapper.",
                MessageTypes.Error);
        }

        return (databaseConnectionSettings, currentFolderManagerSettings, cloudDocumentManager);
    }

    /// <summary>
    /// Attempts to connect to the saved database from DatabaseConnectionSettings
    /// If successful, loads all documents into Manager
    /// </summary>
    /// <param name="databaseConnectionSettings">Database connection settings loaded from file</param>
    private async Task ConnectToSavedDatabaseAsync(DatabaseConnectionSettings databaseConnectionSettings)
    {
        // Check if there's a saved database path
        if (string.IsNullOrWhiteSpace(databaseConnectionSettings.DatabasePath))
        {
            // No saved database - this is normal for first run
            _messageStore?.SetCurrentMessage(
                "No saved database connection. Please connect to or create a database.",
                MessageTypes.Information);
            return;
        }

        // Check if the database file still exists
        if (!System.IO.File.Exists(databaseConnectionSettings.DatabasePath))
        {
            // Database file no longer exists
            _messageStore?.SetCurrentMessage(
                $"Saved database file not found: {databaseConnectionSettings.DatabasePath}. Please reconnect to a database.",
                MessageTypes.Warning);
            return;
        }

        try
        {
            // Attempt to connect to the database
            var connectResult = await _docManagerApi!.ConnectDatabaseAsync(databaseConnectionSettings.DatabasePath);

            if (!connectResult.Success)
            {
                // Connection failed
                _messageStore?.SetCurrentMessage(
                    $"Failed to connect to saved database: {string.Join("; ", connectResult.Errors)}",
                    MessageTypes.Error);
                return;
            }

            // Connection successful - now load data into Manager
            var loadResult = await _docManagerApi.LoadDataIntoManagerAsync(_manager!);

            if (loadResult.Success)
            {
                int count = _manager!.GetAllDocuments().ToList().Count;

                // Success - database connected and data loaded
                _messageStore?.SetCurrentMessage(
                    $"Connected to database: {System.IO.Path.GetFileName(databaseConnectionSettings.DatabasePath)}. Loaded {count} documents.",
                    MessageTypes.Information,
                    dismissAfterSeconds: 10);
            }
            else
            {
                // Database connected but data load failed
                _messageStore?.SetCurrentMessage(
                    $"Database connected but failed to load data: {string.Join("; ", loadResult.Errors)}",
                    MessageTypes.Warning);
            }
        }
        catch (Exception ex)
        {
            // Unexpected error during connection
            _messageStore?.SetCurrentMessage(
                $"Error connecting to saved database: {ex.Message}",
                MessageTypes.Error);
        }
    }

    #endregion

    #region Cleanup Methods

    /// <summary>
    /// Shuts down the application and cleans up resources
    /// </summary>
    public void Shutdown()
    {
        if (_disposed)
        {
            return;
        }

        // Dispose MessageStore to cancel timers
        if (_messageStore is IDisposable disposableStore)
        {
            disposableStore.Dispose();
        }

        // Clean up resources
        _docManagerApi?.Dispose();

        _disposed = true;
    }

    /// <summary>
    /// Handles main window closed event - ensures cleanup happens
    /// </summary>
    private void MainWindow_Closed(object? sender, EventArgs e)
    {
        Shutdown();
    }

    #endregion

    #region IDisposable Implementation

    public void Dispose()
    {
        Shutdown();
        GC.SuppressFinalize(this);
    }

    #endregion
}
