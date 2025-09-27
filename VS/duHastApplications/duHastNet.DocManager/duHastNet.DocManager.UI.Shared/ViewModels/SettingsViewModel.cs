using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.Core.Services.Api;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Main ViewModel for the Settings view - handles database configuration and management
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
}