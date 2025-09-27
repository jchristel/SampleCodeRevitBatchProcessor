using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Helpers partial class for SettingsViewModel - property change handlers and utility methods
/// </summary>
public partial class SettingsViewModel
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