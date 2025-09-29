using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Stores;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Main ViewModel for the Settings view - handles database configuration and management
/// </summary>
public partial class SettingsViewModel : ObservableObject
{
    #region Private Fields

    private readonly DocManagerApi _docManagerApi;
    private readonly MessageStore _messageStore;
    private readonly Manager _manager;

    #endregion

    // Expose message ViewModel for the view
    public GlobalMessageViewModel MessageViewModel { get; }

    

    #region Constructor

    public SettingsViewModel(DocManagerApi docManagerApi, Manager manager, Stores.MessageStore messageStore)
    {
        _docManagerApi = docManagerApi;
        _manager = manager;
        _messageStore = messageStore;

        MessageViewModel = new GlobalMessageViewModel(_messageStore);
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

    [ObservableProperty]
    private int _loadedDocumentCount = 0;

    [ObservableProperty]
    private int _loadedRevisionCount = 0;

    [ObservableProperty]
    private int _customPropertyCount = 0;

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

    /// <summary>
    /// Gets whether data is loaded into the Manager
    /// </summary>
    public bool IsDataLoaded => _manager.IsDataLoaded;

    #endregion
}