using System.IO;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Win32;

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
            StatusMessage = "Selecting database location...";

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
                StatusMessage = "Database creation cancelled";
                return;
            }

            // Update the database path
            DatabasePath = saveDialog.FileName;
            StatusMessage = "Creating database...";

            // Create the database using DocManagerApi
            var setupResult = await _docManagerApi.SetupDatabaseAsync(DatabasePath, overwriteExisting: true);

            if (setupResult.Success)
            {
                // Success - update connection status
                IsConnected = true;
                StatusMessage = $"Database created successfully: {Path.GetFileName(DatabasePath)}";
                OnPropertyChanged(nameof(IsDatabaseReady));
                OnPropertyChanged(nameof(CurrentDatabasePath));
            }
            else
            {
                // Failed - show errors
                var errorMessage = string.Join("; ", setupResult.Errors);
                StatusMessage = $"Failed to create database: {errorMessage}";
                IsConnected = false;
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error creating database: {ex.Message}";
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
            StatusMessage = "Connecting to database...";

            // Connect to existing database using the API method
            var connectResult = await _docManagerApi.ConnectDatabaseAsync(DatabasePath);

            if (connectResult.Success)
            {
                // Success - update connection status
                IsConnected = true;
                StatusMessage = connectResult.Message;
                OnPropertyChanged(nameof(IsDatabaseReady));
                OnPropertyChanged(nameof(CurrentDatabasePath));

                // Show any warnings if present
                if (connectResult.HasWarnings)
                {
                    var warnings = string.Join("; ", connectResult.Warnings);
                    StatusMessage += $" Warnings: {warnings}";
                }
            }
            else
            {
                // Failed - show errors from API
                var errorMessage = string.Join("; ", connectResult.Errors);
                StatusMessage = errorMessage;
                IsConnected = false;
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error connecting to database: {ex.Message}";
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
                StatusMessage = "Database file selected. Click Connect to open.";
            }
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error selecting database file: {ex.Message}";
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
}