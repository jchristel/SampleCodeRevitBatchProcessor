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
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge.MatchedDocs;

/// <summary>
/// ViewModel for the DocumentMatchControl
/// Manages the display and interaction with matched document results
/// </summary>
public partial class DocumentMatchControlViewModel : ObservableObject
{
    #region Private Fields

    private readonly CurrentFolderManager _currentFolderManager;
    private readonly Manager _manager;
    private readonly MessageStore _messageStore;
    private readonly IDialogService _dialogService;
    private readonly DocManagerApi _docManagerApi;

    #endregion

    #region Events

    /// <summary>
    /// Event raised when the matched documents collection changes
    /// </summary>
    public event EventHandler? MatchedDocumentsChanged;

    #endregion
    #region Observable Properties

    /// <summary>
    /// Collection of matched documents for display
    /// </summary>
    [ObservableProperty]
    private ObservableCollection<MatchedDocumentViewModel> _matchedDocuments;

    /// <summary>
    /// Indicates if the control is busy performing an operation
    /// </summary>
    [ObservableProperty]
    private bool _isBusy;

    #endregion

    #region Computed Properties

    /// <summary>
    /// Gets the count of documents with OK status
    /// </summary>
    public int MatchedCount => MatchedDocuments?.Count(d => d.MatchStatus == DocumentMatchStatus.Ok) ?? 0;

    /// <summary>
    /// Gets the count of documents with any warning status (non-blocking)
    /// </summary>
    public int WarningCount => MatchedDocuments?.Count(d => d.HasWarning) ?? 0;

    /// <summary>
    /// Gets the count of documents with revision not sequential warning
    /// </summary>
    public int RevisionNotSequentialCount => MatchedDocuments?.Count(d => d.MatchStatus == DocumentMatchStatus.WarningRevisionNotSequential) ?? 0;

    /// <summary>
    /// Gets the count of documents with missing revision error (blocks merge)
    /// </summary>
    public int MissingRevisionCount => MatchedDocuments?.Count(d => d.MatchStatus == DocumentMatchStatus.ErrorMissingRevision) ?? 0;

    /// <summary>
    /// Gets the count of duplicate documents (blocking errors)
    /// </summary>
    public int DuplicateDocumentCount => MatchedDocuments?.Count(d => d.MatchStatus == DocumentMatchStatus.ErrorDuplicateDocument) ?? 0;

    /// <summary>
    /// Gets the count of documents with no match (blocking errors)
    /// </summary>
    public int NoMatchCount => MatchedDocuments?.Count(d => d.MatchStatus == DocumentMatchStatus.NoMatch) ?? 0;

    /// <summary>
    /// Gets the total count of errors (missing revision + duplicates + no match)
    /// </summary>
    public int ErrorCount => MissingRevisionCount + DuplicateDocumentCount + NoMatchCount;

    /// <summary>
    /// Gets the count of documents that can be merged (no blocking errors)
    /// </summary>
    public int CanMergeCount => MatchedDocuments?.Count(d => d.CanMerge) ?? 0;

    #endregion

    #region Constructor

    public DocumentMatchControlViewModel(
        CurrentFolderManager currentFolderManager,
        Manager manager,
        MessageStore messageStore,
        IDialogService dialogService,
        DocManagerApi docManagerApi)
    {
        _currentFolderManager = currentFolderManager ?? throw new ArgumentNullException(nameof(currentFolderManager));
        _manager = manager ?? throw new ArgumentNullException(nameof(manager));
        _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
        _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));
        _docManagerApi = docManagerApi ?? throw new ArgumentNullException(nameof(docManagerApi));

        _matchedDocuments = new ObservableCollection<MatchedDocumentViewModel>();
    }

    #endregion

    #region Commands

    /// <summary>
    /// Command to refresh the document matching
    /// </summary>
    [RelayCommand]
    public async Task RefreshMatchingAsync()
    {
        if (IsBusy) return;

        IsBusy = true;
        try
        {
            // Get all current documents from the database
            var currentDocuments = _manager.GetAllDocuments().ToList();

            // Call the CurrentFolderManager to match incoming files
            bool matchingSuccessful = _currentFolderManager.GetIncomingFilesMetadata(currentDocuments);

            // Get the matched documents from the manager
            var matchedStatuses = _currentFolderManager.GetMatchedDocuments();

            // Convert to ViewModels
            MatchedDocuments.Clear();
            foreach (var status in matchedStatuses)
            {
                // Get the matched document if there is one
                Document? matchedDoc = null;
                if (status.MatchedDocumentId.HasValue)
                {
                    matchedDoc = currentDocuments.FirstOrDefault(d => d.Id == status.MatchedDocumentId.Value);
                }

                var viewModel = new MatchedDocumentViewModel(status, matchedDoc);
                MatchedDocuments.Add(viewModel);
            }

            // Update computed properties
            UpdateCounts();

            // Build detailed warning message (only non-sequential revisions)
            var warningDetails = new List<string>();
            if (RevisionNotSequentialCount > 0)
                warningDetails.Add($"{RevisionNotSequentialCount} non-sequential");

            var warningText = warningDetails.Count > 0 
                ? $" ({string.Join(", ", warningDetails)})" 
                : string.Empty;

            // Build error message (missing revision, duplicates, no match)
            var errorDetails = new List<string>();
            if (MissingRevisionCount > 0)
                errorDetails.Add($"{MissingRevisionCount} missing revision");
            if (DuplicateDocumentCount > 0)
                errorDetails.Add($"{DuplicateDocumentCount} duplicate(s)");
            if (NoMatchCount > 0)
                errorDetails.Add($"{NoMatchCount} no match");

            var errorText = errorDetails.Count > 0
                ? $" Errors: {string.Join(", ", errorDetails)}."
                : string.Empty;

            // Show success message
            if (ErrorCount > 0)
            {
                _messageStore.EnqueueMessage(
                    $"Document matching completed. {CanMergeCount} can be merged, {WarningCount} warnings{warningText}.{errorText}",
                    MessageTypes.Warning, dismissAfterSeconds: 20
                );
            }
            else if (matchingSuccessful)
            {
                _messageStore.EnqueueMessage(
                    $"Successfully matched {MatchedCount} documents. {WarningCount} warnings{warningText}.",
                    MessageTypes.Information, dismissAfterSeconds: 3
                );
            }
            else
            {
                _messageStore.EnqueueMessage(
                    $"Document matching completed with issues. {CanMergeCount} can be merged, {WarningCount} warnings{warningText}.{errorText}",
                    MessageTypes.Warning, dismissAfterSeconds: 20
                );
            }
        }
        catch (Exception ex)
        {
            _messageStore.EnqueueMessage($"Error during document matching: {ex.Message}", MessageTypes.Error);
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Command to add new documents to the database
    /// </summary>
    [RelayCommand]
    private async Task AddNewDocumentsAsync()
    {
        if (IsBusy) return;

        // Get documents with NoMatch status only (third priority error)
        // Exclude documents with RevisionError (first priority) and DuplicateError (second priority)
        var unknownDocuments = _currentFolderManager.MatchedDocuments
            .Where(d => !d.MatchedDocumentId.HasValue && 
                       d.GetHighestPriorityError() == ProcessingErrorType.DocumentNotFoundError)
            .ToList();

        if (!unknownDocuments.Any())
        {
            _messageStore.EnqueueMessage("No unknown documents found to add.", MessageTypes.Information, dismissAfterSeconds: 3);
            return;
        }

        // Filter to only include supported file types
        var supportedFileTypes = _currentFolderManager.Settings.SupportedFileTypes;
        var supportedExtensions = new HashSet<string>(
            supportedFileTypes.Select(ft => ft.FileExtension),
            StringComparer.OrdinalIgnoreCase);

        var supportedUnknownDocuments = unknownDocuments
            .Where(d => !string.IsNullOrEmpty(d.NewDocumentPath) &&
                       supportedExtensions.Contains(System.IO.Path.GetExtension(d.NewDocumentPath)))
            .ToList();

        if (!supportedUnknownDocuments.Any())
        {
            _messageStore.EnqueueMessage("No unknown documents with supported file types found.", MessageTypes.Information, dismissAfterSeconds: 3);
            return;
        }

        // Get current documents for duplicate checking
        var currentDocuments = _manager.GetAllDocuments().ToList();

        // Get custom field definitions for the dialog
        var customFieldDefinitions = _manager.GetActiveCustomFieldDefinitions().ToList();

        // Create and show the dialog
        var dialogViewModel = new Merge.NewDocs.AddNewDocumentsDialogViewModel(
            currentFolderManager: _currentFolderManager,
            existingDocuments: currentDocuments,
            unknownDocuments: supportedUnknownDocuments,
            dialogService: _dialogService,
            customFieldDefinitions: customFieldDefinitions);
        
        var result = _dialogService.ShowDialog(dialogViewModel);

        if (result == true && dialogViewModel.DialogConfirmed)
        {
            // Get documents to add
            var documentsToAdd = dialogViewModel.GetDocumentsToAdd();

            if (documentsToAdd.Any())
            {
                IsBusy = true;
                try
                {
                    // Create Document objects
                    var documents = new List<Document>();
                    foreach (var docRow in documentsToAdd)
                    {
                        var document = new Document(
                            docRow.ProposedDocumentNumber.Trim(),
                            docRow.ProposedDocumentName.Trim(),
                            "",  // Empty revision indicator
                            0    // No revision (RevisionId = 0)
                        );
                        documents.Add(document);
                    }

                    // Insert documents into database using batch insert
                    var unitOfWork = _docManagerApi.GetUnitOfWork();
                    var insertedCount = await unitOfWork.Documents.InsertAllAsync(documents);

                    // Save custom properties for the newly added documents
                    if (insertedCount > 0 && customFieldDefinitions.Any())
                    {
                        var customPropertiesToAdd = new List<CustomProperty>();
                        
                        for (int i = 0; i < documentsToAdd.Count; i++)
                        {
                            var docRow = documentsToAdd[i];
                            var document = documents[i];
                            
                            // Create custom properties for each custom field value
                            foreach (var customFieldValue in docRow.CustomFieldValues)
                            {
                                // Create property for ALL fields, even if value is empty
                                var customProperty = new CustomProperty
                                {
                                    DocumentId = document.Id,
                                    CustomFieldDefinitionId = customFieldValue.CustomFieldDefinitionId,
                                    PropertyValue = customFieldValue.Value ?? string.Empty  // Ensure empty string, not null
                                };
                                customPropertiesToAdd.Add(customProperty);
                            }
                        }
                        
                        // Batch insert custom properties
                        if (customPropertiesToAdd.Any())
                        {
                            await unitOfWork.CustomProperties.InsertAllAsync(customPropertiesToAdd);
                        }
                    }

                    if (insertedCount > 0)
                    {
                        // Reload the manager to include the newly added documents
                        var reloadResult = await _docManagerApi.ReloadDataIntoManagerAsync(_manager);
                        
                        if (!reloadResult.Success)
                        {
                            _messageStore.EnqueueMessage(
                                $"Documents added to database but failed to reload: {reloadResult.Message}",
                                MessageTypes.Warning, dismissAfterSeconds: 20);
                        }
                        else
                        {
                            _messageStore.EnqueueMessage(
                                $"Successfully added {insertedCount} document(s) to database.",
                                MessageTypes.Information, dismissAfterSeconds: 3);
                        }
                    }
                    else
                    {
                        _messageStore.EnqueueMessage(
                            "No documents were added to the database.",
                            MessageTypes.Warning, dismissAfterSeconds: 20);
                    }
                }
                catch (Exception ex)
                {
                    _messageStore.EnqueueMessage(
                        $"Error adding documents to database: {ex.Message}",
                        MessageTypes.Error);
                }
                finally
                {
                    IsBusy = false;
                    
                    // Refresh the document matching after adding documents and releasing IsBusy
                    // This must be done after IsBusy = false, otherwise RefreshMatchingAsync will exit early
                    if (documentsToAdd.Any())
                    {
                        await RefreshMatchingAsync();
                    }
                }
            }
        }
    }

    #endregion

    #region Public Methods

    /// <summary>
    /// Loads the matched documents from the provided list
    /// </summary>
    /// <param name="matchedStatuses">The list of matched document statuses</param>
    /// <param name="currentDocuments">The list of current documents from the database</param>
    public void LoadMatchedDocuments(
        List<IncomingDocumentProcessingStatus> matchedStatuses,
        List<Document> currentDocuments)
    {
        MatchedDocuments.Clear();

        foreach (var status in matchedStatuses)
        {
            // Get the matched document if there is one
            Document? matchedDoc = null;
            if (status.MatchedDocumentId.HasValue)
            {
                matchedDoc = currentDocuments.FirstOrDefault(d => d.Id == status.MatchedDocumentId.Value);
            }

            var viewModel = new MatchedDocumentViewModel(status, matchedDoc);
            MatchedDocuments.Add(viewModel);
        }

        // Update computed properties
        UpdateCounts();
    }

    #endregion

    #region Private Helper Methods

    /// <summary>
    /// Updates all count properties
    /// </summary>
    private void UpdateCounts()
    {
        OnPropertyChanged(nameof(MatchedCount));
        OnPropertyChanged(nameof(WarningCount));
        OnPropertyChanged(nameof(RevisionNotSequentialCount));
        OnPropertyChanged(nameof(MissingRevisionCount));
        OnPropertyChanged(nameof(DuplicateDocumentCount));
        OnPropertyChanged(nameof(NoMatchCount));
        OnPropertyChanged(nameof(ErrorCount));
        OnPropertyChanged(nameof(CanMergeCount));

        // Raise event to notify subscribers that matched documents have changed
        MatchedDocumentsChanged?.Invoke(this, EventArgs.Empty);
    }

    #endregion
}
