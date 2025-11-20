//
//License:
//
//
// Revit Batch Processor Sample Code
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


using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;
namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Main ViewModel for the Document Manager application
/// </summary>
public partial class MergeViewModel : ObservableObject, IActivatable
{
    #region Private Fields

    private readonly DocManagerApi _docManagerApi;
    private readonly MessageStore _messageStore;
    private readonly NavigationStore _navigationStore;
    private readonly Manager _manager;
    private readonly CurrentFolderManager _currentFolderManager;
    private readonly IDialogService _dialogService;

    //function used to navigate to settings view model
    private readonly Func<SettingsViewModel> _createViewModel;

    #endregion

    // Expose message ViewModel for the view
    public GlobalMessageViewModel MessageViewModel { get; }

    // Expose document match control ViewModel for the view
    public DocumentMatchControlViewModel DocumentMatchViewModel { get; }

    #region Constructor

    public MergeViewModel(
        DocManagerApi docManagerApi,
        MessageStore messageStore,
        NavigationStore navigationStore,
        Manager manager,
        CurrentFolderManager currentFolderManager,
        IDialogService dialogService,
        Func<SettingsViewModel> createViewModel
        )
    {
        _docManagerApi = docManagerApi;
        _messageStore = messageStore;
        _navigationStore = navigationStore;
        _createViewModel = createViewModel;
        _manager = manager ?? throw new ArgumentNullException(nameof(manager));
        _currentFolderManager = currentFolderManager ?? throw new ArgumentNullException(nameof(currentFolderManager));
        _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));

        MessageViewModel = new GlobalMessageViewModel(_messageStore);
        DocumentMatchViewModel = new DocumentMatchControlViewModel(_currentFolderManager, _manager,  _messageStore, _dialogService, _docManagerApi);

        // Initialize collections
        FilteredRevisionDescriptions = new ObservableCollection<string>();

        
    }

    #endregion

    #region Observable Properties

    [ObservableProperty]
    private string _statusMessage = "Ready";

    [ObservableProperty]
    private bool _isConnected = false;

    [ObservableProperty]
    private bool _isBusy = false;

    [ObservableProperty]
    private string _revisionDescription = string.Empty;

    [ObservableProperty]
    private ObservableCollection<string> _filteredRevisionDescriptions;

    [ObservableProperty]
    private bool _isRevisionSuggestionsPopupOpen = false;

    [ObservableProperty]
    private DateTime? _revisionDate;

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
    /// Gets whether the merge button should be enabled
    /// Requires: Database connected, Revision date set, Revision description set
    /// </summary>
    public bool CanMerge => IsDatabaseReady && 
                            !IsBusy && 
                            RevisionDate.HasValue && 
                            !string.IsNullOrWhiteSpace(RevisionDescription);

    #endregion

    #region IActivatable Implementation

    /// <summary>
    /// Called when the ViewModel is activated (navigated to)
    /// Refreshes the document matching to show current state
    /// </summary>
    public async Task OnActivatedAsync()
    {
        try
        {
            // Refresh the document matching when the view is displayed
            await DocumentMatchViewModel.RefreshMatchingAsync().ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            _messageStore.EnqueueMessage(
                $"Error initializing merge view: {ex.Message}",
                MessageTypes.Error);
        }
    }

    #endregion

    #region Commands

    /// <summary>
    /// Command to navigate to the Settings view
    /// </summary>
    [RelayCommand]
    private void NavigateToSettings()
    {
        _navigationStore.NavigateTo(() => _createViewModel());
    }

    /// <summary>
    /// Command to select a revision description from the suggestions
    /// </summary>
    [RelayCommand]
    private void SelectRevisionDescription(string selectedDescription)
    {
        if (!string.IsNullOrEmpty(selectedDescription))
        {
            RevisionDescription = selectedDescription;
            IsRevisionSuggestionsPopupOpen = false;
            FilteredRevisionDescriptions.Clear();
        }
    }

    /// <summary>
    /// Command to perform the document merge operation
    /// </summary>
    [RelayCommand]
    private async Task MergeDocumentsAsync()
    {
        if (!CanMerge) return;

        IsBusy = true;
        try
        {
            var currentDocuments = _manager.GetAllDocuments().ToList();

            // Step 2: Load matched documents into the control
            var matchedDocs = _currentFolderManager.GetMatchedDocuments();
            DocumentMatchViewModel.LoadMatchedDocuments(matchedDocs, currentDocuments);

            // Notify that unknown documents may have changed
            //OnPropertyChanged(nameof(HasUnknownDocuments));

            _messageStore.EnqueueMessage(
                $"Document matching complete. {DocumentMatchViewModel.MatchedCount} matched, " +
                $"{DocumentMatchViewModel.WarningCount} warnings, {DocumentMatchViewModel.NoMatchCount} without matches.",
                MessageTypes.Information,
                10
            );

            // Step 3: Update database with documents of green and yellow status
            bool databaseUpdateSuccessful = await UpdateDatabaseAsync();

            // Step 4: Export metadata to cloud provider (if enabled and database update was successful)
            if (databaseUpdateSuccessful)
            {
                await ExportMetadataAsync();
            }

            // Step 5: Merge incoming files with red and yellow status into their target locations
            // This happens regardless of database update success, as file operations are independent
            await MergeFilesAsync();

            // refresh the document list after merge
            await DocumentMatchViewModel.RefreshMatchingAsync();

        }
        catch (Exception ex)
        {
            _messageStore.EnqueueMessage($"Error during merge operation: {ex.Message}", MessageTypes.Error);
        }
        finally
        {
            IsBusy = false;
            OnPropertyChanged(nameof(CanMerge));
        }
    }

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
        OnPropertyChanged(nameof(CanMerge));
    }

    /// <summary>
    /// Called when IsBusy changes
    /// </summary>
    partial void OnIsBusyChanged(bool value)
    {
        // Update button states during operations
        UpdateButtonStates();
        OnPropertyChanged(nameof(CanMerge));
    }

    /// <summary>
    /// Called when RevisionDescription changes - filters and displays matching revision descriptions
    /// </summary>
    partial void OnRevisionDescriptionChanged(string value)
    {

        // Update merge button state
        OnPropertyChanged(nameof(CanMerge));

        // Clear suggestions if input is empty
        if (string.IsNullOrWhiteSpace(value))
        {
            FilteredRevisionDescriptions.Clear();
            IsRevisionSuggestionsPopupOpen = false;
            return;
        }

        // Get all revisions from the manager
        var allRevisions = _manager.GetAllRevisions();

        // Filter revisions that have a description starting with the input text (case-insensitive)
        var matches = allRevisions
            .Where(r => !string.IsNullOrEmpty(r.Description) &&
                       r.Description.StartsWith(value, StringComparison.OrdinalIgnoreCase))
            .Select(r => r.Description)
            .Distinct()
            .OrderBy(d => d)
            .Take(10); // Limit to 10 suggestions for performance

        // Update the filtered collection
        FilteredRevisionDescriptions.Clear();
        foreach (var match in matches)
        {
            FilteredRevisionDescriptions.Add(match!);
        }

        // Show popup if there are suggestions
        IsRevisionSuggestionsPopupOpen = FilteredRevisionDescriptions.Count > 0;
    }

    /// <summary>
    /// Called when RevisionDate changes
    /// </summary>
    partial void OnRevisionDateChanged(DateTime? value)
    {
        // Update merge button state
        OnPropertyChanged(nameof(CanMerge));
    }

    #endregion

    #region Private Helper Methods

    /// <summary>
    /// Updates the enabled state of various buttons based on current state
    /// </summary>
    private void UpdateButtonStates()
    {
        OnPropertyChanged(nameof(CanMerge));
    }

    #endregion
}
