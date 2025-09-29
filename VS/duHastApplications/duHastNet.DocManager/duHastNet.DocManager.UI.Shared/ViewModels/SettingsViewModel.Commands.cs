using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.UI.Shared.Stores;
using Microsoft.Win32;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Commands partial class for SettingsViewModel
/// </summary>
public partial class SettingsViewModel
{
    #region Database Commands

    /// <summary>
    /// Command to create a new database - shows save dialog then creates database
    /// </summary>
    [RelayCommand]
    private async Task CreateDatabaseAsync()
    {
        try
        {
            IsBusy = true;

            // Inform user
            _messageStore.SetCurrentMessage("Creating database...", MessageTypes.Information);

            // Configure and show SaveFileDialog
            var saveDialog = new SaveFileDialog
            {
                Title = "Create New Database",
                Filter = "Database files (*.db)|*.db|SQLite files (*.sqlite)|*.sqlite|All files (*.*)|*.*",
                DefaultExt = ".db",
                AddExtension = true,
                OverwritePrompt = true,
                InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
            };

            // Show dialog and check result
            var dialogResult = saveDialog.ShowDialog();
            if (dialogResult != true)
            {
                // User cancelled
                return;
            }

            // Update the database path
            DatabasePath = saveDialog.FileName;

            // Create the database using DocManagerApi
            var setupResult = await _docManagerApi.SetupDatabaseAsync(DatabasePath, overwriteExisting: true);

            if (setupResult.Success)
            {
                // Load data into Manager
                var loadResult = await _docManagerApi.LoadDataIntoManagerAsync(_manager);

                if (loadResult.Success)
                {
                    // Success - update connection status and statistics
                    IsConnected = true;

                    // Inform user of success with auto-dismiss
                    _messageStore.SetCurrentMessage(
                        $"Database created successfully: {Path.GetFileName(DatabasePath)}",
                        MessageTypes.Information,
                        10); // Auto-dismiss after 10 seconds

                    UpdateStatistics();
                }
                else
                {
                    // Database created but data load failed
                    IsConnected = true;
                }

                OnPropertyChanged(nameof(IsDatabaseReady));
                OnPropertyChanged(nameof(CurrentDatabasePath));
                OnPropertyChanged(nameof(IsDataLoaded));
            }
            else
            {
                var errorMessage = string.Join("; ", setupResult.Errors);
                _messageStore.SetCurrentMessage(
                    $"Failed to create database: {errorMessage}",
                    MessageTypes.Error); // No auto-dismiss for errors

                // Failed - database not created
                IsConnected = false;
            }
        }
        catch (Exception ex)
        {
            // Inform user of error
            _messageStore.SetCurrentMessage(
                $"Error creating database: {ex.Message}",
                MessageTypes.Error);

            IsConnected = false;
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Command to connect to an existing database
    /// </summary>
    [RelayCommand]
    private async Task ConnectDatabaseAsync()
    {
        try
        {
            IsBusy = true;

            // Connect to existing database using the API method
            var connectResult = await _docManagerApi.ConnectDatabaseAsync(DatabasePath);

            if (connectResult.Success)
            {
                // Load data into Manager
                var loadResult = await _docManagerApi.LoadDataIntoManagerAsync(_manager);

                if (loadResult.Success)
                {
                    // Success - update connection status and statistics
                    IsConnected = true;
                    UpdateStatistics();
                }
                else
                {
                    // Database connected but data load failed
                    IsConnected = true;
                }

                OnPropertyChanged(nameof(IsDatabaseReady));
                OnPropertyChanged(nameof(CurrentDatabasePath));
                OnPropertyChanged(nameof(IsDataLoaded));
            }
            else
            {
                // Failed - connection failed
                IsConnected = false;
            }
        }
        catch (Exception)
        {
            IsConnected = false;
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Command to browse for an existing database file
    /// </summary>
    [RelayCommand]
    private void BrowseDatabase()
    {
        try
        {
            var openDialog = new OpenFileDialog
            {
                Title = "Select Database File",
                Filter = "Database files (*.db)|*.db|SQLite files (*.sqlite)|*.sqlite|All files (*.*)|*.*",
                CheckFileExists = true,
                Multiselect = false,
                InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
            };

            var dialogResult = openDialog.ShowDialog();
            if (dialogResult == true)
            {
                DatabasePath = openDialog.FileName;
            }
        }
        catch (Exception)
        {
            // Handle silently or add logging
        }
    }

    /// <summary>
    /// Command to test database connection
    /// </summary>
    [RelayCommand]
    private async Task TestDatabaseAsync()
    {
        // TODO: Implement database connection test
        await Task.CompletedTask;
    }

    #endregion

    #region Import/Export Commands

    /// <summary>
    /// Command to import documents from external source
    /// </summary>
    [RelayCommand]
    private async Task ImportDocumentsAsync()
    {
        // TODO: Implement document import
        await Task.CompletedTask;
    }

    /// <summary>
    /// Command to export documents to external format
    /// </summary>
    [RelayCommand]
    private async Task ExportDocumentsAsync()
    {
        // TODO: Implement document export
        await Task.CompletedTask;
    }

    #endregion

    #region Custom Field Commands

    /// <summary>
    /// Command to add a new custom field
    /// </summary>
    [RelayCommand]
    private void AddCustomField()
    {
        // TODO: Implement add custom field
    }

    /// <summary>
    /// Command to remove selected custom field
    /// </summary>
    [RelayCommand]
    private void RemoveCustomField()
    {
        // TODO: Implement remove custom field
    }

    /// <summary>
    /// Command to update database schema with custom fields
    /// </summary>
    [RelayCommand]
    private async Task UpdateDatabaseSchemaAsync()
    {
        // TODO: Implement database schema update
        await Task.CompletedTask;
    }

    #endregion

    #region Helper Methods

    /// <summary>
    /// Updates statistics from the Manager
    /// </summary>
    private void UpdateStatistics()
    {
        LoadedDocumentCount = _manager.DocumentCount;
        LoadedRevisionCount = _manager.RevisionCount;
        CustomPropertyCount = _manager.GetAllCustomPropertyNames().Count();
    }

    #endregion
}