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

            var filePath = _dialogService.ShowOpenFileDialog(
                "Select Database File",
                "Database files (*.db)|*.db|SQLite files (*.sqlite)|*.sqlite|All files (*.*)|*.*");

            // Check for cancellation
            if (filePath == null || filePath.Length==0)
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