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

using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.UI.Shared.Stores;
using Microsoft.Win32;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Commands partial class for SettingsViewModel
/// </summary>
public partial class DatabaseConnectionViewModel
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

            // Use dialog service instead of direct dialog
            var selectedPath = _dialogService.ShowSaveFileDialog(
                "Create New Database",
                "Database files (*.db)|*.db|SQLite files (*.sqlite)|*.sqlite|All files (*.*)|*.*",
                ".db");

            if (string.IsNullOrEmpty(selectedPath))
            {
                // User cancelled
                return;
            }

            // Update the database path
            DatabasePath = selectedPath;

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

                    // Initialize custom fields after data load
                    InitializeCustomFields();

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

                    // Initialize custom fields after data load
                    InitializeCustomFields();

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

            var filePath = _dialogService.ShowOpenFileDialog(
                "Select Database File",
                "Database files (*.db)|*.db|SQLite files (*.sqlite)|*.sqlite|All files (*.*)|*.*");

            // Check for cancellation
            if (filePath == null || filePath.Length == 0)
            {
                // User cancelled
                return;
            }

            //set database path
            DatabasePath = filePath[0];
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
        try
        {
            IsBusy = true;
            _messageStore.SetCurrentMessage("Importing documents...", MessageTypes.Information);

            // Check if data is loaded
            if (!_manager.IsDataLoaded)
            {
                _messageStore.SetCurrentMessage("No data loaded. Please connect to a database first.", MessageTypes.Error);
                return;
            }

            // Show open file dialog
            var selectedPath = _dialogService.ShowOpenFileDialog(
                "Import Documents",
                "CSV files (*.csv)|*.csv|All files (*.*)|*.*");

            // Check for cancellation
            if (selectedPath == null || selectedPath.Length == 0)
            {
                _messageStore.SetCurrentMessage("Import cancelled.", MessageTypes.Information);
                return;
            }

            // Create import service with unit of work
            var importService = new Core.Services.DocumentImportService(_docManagerApi.GetUnitOfWork());
            
            // Perform import on background thread
            var result = await Task.Run(() => importService.ImportDocumentsAsync(selectedPath[0]));

            if (result.IsImportSuccessful)
            {
                _messageStore.SetCurrentMessage(
                    $"Successfully imported: {result.DocumentsCreated} documents created, {result.DocumentsProcessed - result.DocumentsCreated} updated",
                    MessageTypes.Information);

                // Reload data into manager
                await _docManagerApi.ReloadDataIntoManagerAsync(_manager);
                UpdateStatistics();
            }
            else
            {
                var errorMessage = result.HasErrors 
                    ? $"Import completed with errors. {result.Message}. First error: {result.Errors.FirstOrDefault()}" 
                    : result.Message;
                    
                _messageStore.SetCurrentMessage(errorMessage, MessageTypes.Error);
            }
        }
        catch (Exception ex)
        {
            _messageStore.SetCurrentMessage($"Import failed: {ex.Message}", MessageTypes.Error);
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Command to export documents to external format
    /// </summary>
    [RelayCommand]
    private async Task ExportDocumentsAsync()
    {
        try
        {
            IsBusy = true;
            _messageStore.SetCurrentMessage("Exporting documents...", MessageTypes.Information);

            // Check if data is loaded
            if (!_manager.IsDataLoaded)
            {
                _messageStore.SetCurrentMessage("No data loaded. Please connect to a database first.", MessageTypes.Error);
                return;
            }

            // Show save file dialog
            var selectedPath = _dialogService.ShowSaveFileDialog(
                "Export Documents",
                "CSV files (*.csv)|*.csv|All files (*.*)|*.*",
                "Documents.csv");

            // Check for cancellation
            if (string.IsNullOrEmpty(selectedPath))
            {
                _messageStore.SetCurrentMessage("Export cancelled.", MessageTypes.Information);
                return;
            }

            // Get data from manager
            var documents = _manager.GetAllDocuments().ToList();
            var customFieldDefinitions = _manager.GetActiveCustomFieldDefinitions().ToList();
            var revisions = _manager.GetAllRevisions().ToList();

            // Create export service and perform export
            var exportService = new Core.Services.DocumentExportService();
            var success = await Task.Run(() =>
                exportService.ExportDocuments(
                    selectedPath,
                    documents,
                    customFieldDefinitions,
                    revisions));

            if (success)
            {
                _messageStore.SetCurrentMessage(
                    $"Successfully exported {documents.Count} documents to {Path.GetFileName(selectedPath)}",
                    MessageTypes.Information);
            }
            else
            {
                _messageStore.SetCurrentMessage("Export failed. Please check the file path and try again.", MessageTypes.Error);
            }
        }
        catch (Exception ex)
        {
            _messageStore.SetCurrentMessage($"Export failed: {ex.Message}", MessageTypes.Error);
        }
        finally
        {
            IsBusy = false;
        }
    }

    #endregion

    #region Helper Methods

    /// <summary>
    /// Updates statistics from the Manager
    /// </summary>
    #endregion

    private void UpdateStatistics()
    {
        //TODO
    }
}

