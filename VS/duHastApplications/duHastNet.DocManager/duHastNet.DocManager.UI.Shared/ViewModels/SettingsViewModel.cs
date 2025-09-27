using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Main ViewModel for the Document Manager application
/// </summary>
public partial class SettingsViewModel : ObservableObject
{
    #region Private Fields

    private readonly DocManagerApi _docManagerApi;

    #endregion

    #region Constructor

    public SettingsViewModel(DocManagerApi docManagerApi)
    {
        _docManagerApi = docManagerApi;
    }

    #endregion

    #region Observable Properties

    [ObservableProperty]
    private string _databasePath = string.Empty;

    [ObservableProperty]
    private string _statusMessage = "Ready";

    [ObservableProperty]
    private bool _isConnected = false;

    [ObservableProperty]
    private bool _isBusy = false;

    [ObservableProperty]
    private bool _isCreateDatabaseEnabled = true;

    [ObservableProperty]
    private bool _isConnectDatabaseEnabled = true;

    [ObservableProperty]
    private bool _isBrowseEnabled = true;

    [ObservableProperty]
    private bool _isImportExportEnabled = false;

    #endregion

    #region Computed Properties

    /// <summary>
    /// Gets whether database operations are available
    /// </summary>
    public bool IsDatabaseReady => _docManagerApi.IsDatabaseReady();

    /// <summary>
    /// Gets the current database path from the API
    /// </summary>
    public string? CurrentDatabasePath => _docManagerApi.GetDatabasePath();

    #endregion

    #region Commands - To be implemented

    // TODO: Commands will be added here
    // - CreateDatabaseCommand
    // - ConnectDatabaseCommand  
    // - BrowseDatabaseCommand
    // - ImportDocumentsCommand
    // - ExportDocumentsCommand
    // - TestDatabaseCommand

    #endregion

    #region Private Methods - To be implemented

    // TODO: Helper methods will be added here
    // - UpdateConnectionStatus()
    // - ValidateDatabasePath()
    // - ShowSuccessMessage()
    // - ShowErrorMessage()

    #endregion

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

        IsCreateDatabaseEnabled = !IsBusy && hasValidPath;
        IsConnectDatabaseEnabled = !IsBusy && hasValidPath && System.IO.File.Exists(DatabasePath);
        IsBrowseEnabled = !IsBusy;
        IsImportExportEnabled = !IsBusy && IsConnected;
    }

    #endregion
}