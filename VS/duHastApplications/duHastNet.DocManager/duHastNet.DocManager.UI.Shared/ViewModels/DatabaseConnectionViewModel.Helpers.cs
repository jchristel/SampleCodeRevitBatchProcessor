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

using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Helpers partial class for DatabaseConnectionViewModel - property change handlers and utility methods
/// </summary>
public partial class DatabaseConnectionViewModel
{
    #region Property Change Handlers

    /// <summary>
    /// Called when DatabasePath changes
    /// </summary>
    partial void OnDatabasePathChanged(string value)
    {
        // Update button states based on path validity
        UpdateButtonStates();
    }

    /// <summary>
    /// Called when IsConnected changes
    /// </summary>
    partial void OnIsConnectedChanged(bool value)
    {
        // Update dependent properties
        UpdateButtonStates();
        OnPropertyChanged(nameof(IsDatabaseReady));
    }

    /// <summary>
    /// Called when IsBusy changes
    /// </summary>
    partial void OnIsBusyChanged(bool value)
    {
        // Update button states during operations
        UpdateButtonStates();
    }

    #endregion

    #region Private Helper Methods

    /// <summary>
    /// Updates the enabled state of various buttons based on current state
    /// </summary>
    private void UpdateButtonStates()
    {
        var hasValidPath = !string.IsNullOrWhiteSpace(DatabasePath);
        var fileExists = hasValidPath && File.Exists(DatabasePath);

        IsCreateDatabaseEnabled = !IsBusy && hasValidPath;
        IsConnectDatabaseEnabled = !IsBusy && fileExists;
        IsBrowseEnabled = !IsBusy;
        IsImportExportEnabled = !IsBusy && IsConnected;
    }

    /// <summary>
    /// Validates if the current database path is valid for creation
    /// </summary>
    private bool IsValidDatabasePath(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return false;

        try
        {
            // Check if directory exists or can be created
            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
            {
                // Try to create the directory to validate the path
                Directory.CreateDirectory(directory);
            }

            // Check if filename is valid
            var fileName = Path.GetFileName(path);
            if (string.IsNullOrWhiteSpace(fileName))
                return false;

            // Check for invalid characters
            var invalidChars = Path.GetInvalidFileNameChars();
            if (fileName.IndexOfAny(invalidChars) >= 0)
                return false;

            return true;
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Formats error messages for display to user
    /// </summary>
    private string FormatErrorMessage(string operation, Exception ex)
    {
        return $"Error during {operation}: {ex.Message}";
    }

    /// <summary>
    /// Formats success messages for display to user
    /// </summary>
    private string FormatSuccessMessage(string operation, string? details = null)
    {
        var message = $"{operation} completed successfully";
        if (!string.IsNullOrEmpty(details))
            message += $": {details}";
        return message;
    }

    #endregion

    #region Validation Methods

    /// <summary>
    /// Validates database connection requirements
    /// </summary>
    private bool CanConnectToDatabase()
    {
        return !string.IsNullOrWhiteSpace(DatabasePath) &&
               File.Exists(DatabasePath) &&
               !IsBusy;
    }

    /// <summary>
    /// Validates database creation requirements
    /// </summary>
    private bool CanCreateDatabase()
    {
        return !string.IsNullOrWhiteSpace(DatabasePath) &&
               IsValidDatabasePath(DatabasePath) &&
               !IsBusy;
    }

    #endregion
}