using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Services.Api;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Main ViewModel for the Document Manager application
/// </summary>
public partial class MergeViewModel : ObservableObject
{
    #region Private Fields

    private readonly DocManagerApi _docManagerApi;

    #endregion

    #region Constructor

    public MergeViewModel(DocManagerApi docManagerApi)
    {
        _docManagerApi = docManagerApi;
    }

    #endregion

    #region Observable Properties

    [ObservableProperty]
    private string _statusMessage = "Ready";

    [ObservableProperty]
    private bool _isConnected = false;

    [ObservableProperty]
    private bool _isBusy = false;

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

    #endregion

    #region Private Methods - To be implemented

    #endregion

    #region Property Change Handlers

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
        
    }

    #endregion
}