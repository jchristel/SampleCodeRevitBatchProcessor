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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System.Collections.ObjectModel;


namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge;

/// <summary>
/// Main ViewModel for the Document Manager application
/// </summary>
public partial class MergeViewModel : AppViewModelBase, IActivatable
{
    #region Private Fields

    private readonly IDocManagerApi _docManagerApi;
    private readonly IMessageStore _messageStore;
    private readonly NavigationStore _navigationStore;
    private readonly IManager _manager;
    private readonly ICurrentFolderManager _currentFolderManager;
    private readonly IDialogService _dialogService;

    //function used to navigate to settings view model
    private readonly Func<Settings.SettingsViewModel> _createViewModel;

    #endregion

    // Expose message ViewModel for the view
    public GlobalMessageViewModel GlobalMessageViewModel { get; }

    // Expose document match control ViewModel for the view
    public Merge.MatchedDocs.DocumentMatchControlViewModel DocumentMatchViewModel { get; }

    #region Constructor

    public MergeViewModel(
        IDocManagerApi docManagerApi,
        IMessageStore messageStore,
        NavigationStore navigationStore,
        IManager manager,
        ICurrentFolderManager currentFolderManager,
        IDialogService dialogService,
        Func<Settings.SettingsViewModel> createViewModel
        )
    {
        _docManagerApi = docManagerApi;
        _messageStore = messageStore;
        _navigationStore = navigationStore;
        _createViewModel = createViewModel;
        _manager = manager ?? throw new ArgumentNullException(nameof(manager));
        _currentFolderManager = currentFolderManager ?? throw new ArgumentNullException(nameof(currentFolderManager));
        _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));

        GlobalMessageViewModel = new GlobalMessageViewModel(_messageStore);
        DocumentMatchViewModel = new Merge.MatchedDocs.DocumentMatchControlViewModel(_currentFolderManager, _manager, _messageStore, _dialogService, _docManagerApi);

        // Register child ViewModels for automatic lifecycle management
        RegisterChild(GlobalMessageViewModel);
        RegisterChild(DocumentMatchViewModel);

        // Subscribe to document match changes to update merge button state
        DocumentMatchViewModel.MatchedDocumentsChanged += OnMatchedDocumentsChanged;

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
    /// Determines whether the merge button should be enabled
    /// Requires: Database connected, Revision date set, Revision description set, and documents available to merge
    /// </summary>
    private bool CanMerge() => IsDatabaseReady &&
                               !IsBusy &&
                               RevisionDate.HasValue &&
                               !string.IsNullOrWhiteSpace(RevisionDescription) &&
                               DocumentMatchViewModel.CanMergeCount > 0;

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
            await DocumentMatchViewModel.RefreshMatchingAsync();
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
    [RelayCommand(CanExecute = nameof(CanMerge))]
    private async Task MergeDocumentsAsync()
    {
        //if (!CanMerge) return;

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

            // Step 3.5: Reload Manager after database update to reflect changes
            // This is critical for all documents (especially newly added ones) to show updated revision in the UI
            if (databaseUpdateSuccessful)
            {
                var reloadResult = await _docManagerApi.ReloadDataIntoManagerAsync(_manager);
                if (!reloadResult.Success)
                {
                    _messageStore.EnqueueMessage(
                        $"Database updated but failed to reload data: {reloadResult.Message}",
                        MessageTypes.Warning, dismissAfterSeconds: 20);
                }
            }

            // Step 4: Export metadata to cloud provider (if enabled and database update was successful)
            if (databaseUpdateSuccessful)
            {
                await ExportMetadataAsync();
            }

            // Step 5: Merge incoming files with red and yellow status into their target locations
            // This happens regardless of database update success, as file operations are independent
            await MergeFilesAsync();

            // Step 6: Show merge log dialog with all process messages
            ShowMergeLog();

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
            MergeDocumentsCommand.NotifyCanExecuteChanged();
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
        MergeDocumentsCommand.NotifyCanExecuteChanged();
    }

    /// <summary>
    /// Called when IsBusy changes
    /// </summary>
    partial void OnIsBusyChanged(bool value)
    {
        // Update button states during operations
        UpdateButtonStates();
        MergeDocumentsCommand.NotifyCanExecuteChanged();
    }

    /// <summary>
    /// Called when RevisionDescription changes - filters and displays matching revision descriptions
    /// </summary>
    partial void OnRevisionDescriptionChanged(string value)
    {

        // Update merge button state
        MergeDocumentsCommand.NotifyCanExecuteChanged();

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
        MergeDocumentsCommand.NotifyCanExecuteChanged();
    }

    #endregion

    #region Private Helper Methods

    /// <summary>
    /// Updates the enabled state of various buttons based on current state
    /// </summary>
    private void UpdateButtonStates()
    {
        MergeDocumentsCommand.NotifyCanExecuteChanged();
    }

    /// <summary>
    /// Event handler for when matched documents collection changes
    /// Updates the merge button enabled state
    /// </summary>
    private void OnMatchedDocumentsChanged(object? sender, EventArgs e)
    {
        MergeDocumentsCommand.NotifyCanExecuteChanged();
    }

    #endregion

    #region Lifecycle

    /// <summary>
    /// Called when the ViewModel is being navigated away from or closed.
    /// Unsubscribes from cross-ViewModel events then propagates to child ViewModels via base.
    /// </summary>
    public override void OnClosing()
    {
        // Unsubscribe from DocumentMatchViewModel event before disposing it
        DocumentMatchViewModel.MatchedDocumentsChanged -= OnMatchedDocumentsChanged;

        // Propagate to all registered children
        base.OnClosing();
    }

    /// <summary>
    /// Disposes resources used by this ViewModel and its registered children.
    /// </summary>
    public override void Dispose()
    {
        base.Dispose();
    }

    #endregion
}