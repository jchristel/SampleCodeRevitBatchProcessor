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
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// ViewModel for the Add New Documents dialog
/// Handles the display and processing of unknown documents from the incoming folder
/// </summary>
public partial class AddNewDocumentsDialogViewModel : ObservableObject
{
    #region Private Fields

    private readonly CurrentFolderManager _currentFolderManager;
    private readonly List<Document> _existingDocuments;
    private readonly List<CustomFieldDefinition> _customFieldDefinitions;

    #endregion

    #region Observable Properties

    /// <summary>
    /// Collection of new document rows for display
    /// </summary>
    [ObservableProperty]
    private ObservableCollection<NewDocumentRowViewModel> _documentRows;

    /// <summary>
    /// Indicates if the dialog is busy performing an operation
    /// </summary>
    [ObservableProperty]
    private bool _isBusy;

    /// <summary>
    /// Dialog title
    /// </summary>
    public string DialogTitle => "Add New Documents";

    /// <summary>
    /// Indicates whether the user confirmed the dialog (set when OK is clicked)
    /// </summary>
    [ObservableProperty]
    private bool _dialogConfirmed;

    #endregion

    #region Computed Properties

    /// <summary>
    /// Gets the count of documents that can be added
    /// </summary>
    public int ReadyToAddCount => DocumentRows?.Count(d => d.CanAdd) ?? 0;

    /// <summary>
    /// Gets the count of documents with duplicate document numbers
    /// </summary>
    public int DuplicateCount => DocumentRows?.Count(d =>
        d.Status == NewDocumentRowStatus.DuplicateDocumentNumber ||
        d.Status == NewDocumentRowStatus.DuplicateInList) ?? 0;

    /// <summary>
    /// Gets the total count of documents
    /// </summary>
    public int TotalCount => DocumentRows?.Count ?? 0;

    /// <summary>
    /// Gets the custom field definitions for dynamic column generation
    /// </summary>
    public IReadOnlyList<CustomFieldDefinition> CustomFieldDefinitions => _customFieldDefinitions;

    #endregion

    #region Events

    /// <summary>
    /// Event raised when the ViewModel requests the view to close
    /// </summary>
    public event EventHandler? RequestClose;

    #endregion

    #region Constructor

    /// <summary>
    /// Constructor for AddNewDocumentsDialogViewModel
    /// </summary>
    /// <param name="currentFolderManager">The current folder manager containing file matching information</param>
    /// <param name="existingDocuments">List of existing documents in the database</param>
    /// <param name="unknownDocuments">List of unknown document processing statuses</param>
    /// <param name="customFieldDefinitions">List of custom field definitions for the new documents</param>
    public AddNewDocumentsDialogViewModel(
        CurrentFolderManager currentFolderManager,
        List<Document> existingDocuments,
        List<IncomingDocumentProcessingStatus> unknownDocuments,
        List<CustomFieldDefinition>? customFieldDefinitions = null)
    {
        _currentFolderManager = currentFolderManager ?? throw new ArgumentNullException(nameof(currentFolderManager));
        _existingDocuments = existingDocuments ?? throw new ArgumentNullException(nameof(existingDocuments));
        _customFieldDefinitions = customFieldDefinitions ?? new List<CustomFieldDefinition>();

        _documentRows = new ObservableCollection<NewDocumentRowViewModel>();

        // Load the unknown documents
        LoadUnknownDocuments(unknownDocuments);
    }

    #endregion

    #region Commands

    /// <summary>
    /// Determines if OK button should be enabled
    /// </summary>
    private bool CanExecuteOk()
    {
        // Must have at least one document that can be added
        return ReadyToAddCount > 0;
    }

    /// <summary>
    /// Command to accept dialog (OK button)
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanExecuteOk))]
    private void Ok()
    {
        // Set confirmation flag
        DialogConfirmed = true;

        // Close the dialog
        RequestClose?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>
    /// Command to cancel dialog (Cancel button)
    /// </summary>
    [RelayCommand]
    private void Cancel()
    {
        // Close the dialog without confirming
        RequestClose?.Invoke(this, EventArgs.Empty);
    }

    #endregion

    #region Public Methods

    /// <summary>
    /// Gets the list of documents that are ready to be added
    /// </summary>
    public List<NewDocumentRowViewModel> GetDocumentsToAdd()
    {
        return DocumentRows.Where(d => d.CanAdd).ToList();
    }

    #endregion

    #region Private Helper Methods

    /// <summary>
    /// Loads unknown documents into the view model
    /// </summary>
    private void LoadUnknownDocuments(List<IncomingDocumentProcessingStatus> unknownDocuments)
    {
        DocumentRows.Clear();

        if (unknownDocuments == null || !unknownDocuments.Any())
        {
            return;
        }

        // Get existing document numbers for duplicate checking
        var existingDocumentNumbers = new HashSet<string>(
            _existingDocuments.Select(d => d.Number),
            StringComparer.OrdinalIgnoreCase);

        // Get supported file types from the manager
        var supportedFileTypes = _currentFolderManager.Settings.SupportedFileTypes;

        // Get revision separators
        var revisionPrefix = _currentFolderManager.Settings.RevisionPrefix;
        var revisionSuffix = _currentFolderManager.Settings.RevisionSuffix;

        // Track proposed document numbers within this list to detect duplicates
        var proposedDocumentNumbers = new Dictionary<string, List<NewDocumentRowViewModel>>(StringComparer.OrdinalIgnoreCase);

        // Create view models for each unknown document
        foreach (var unknownDoc in unknownDocuments)
        {
            if (string.IsNullOrEmpty(unknownDoc.NewDocumentPath))
                continue;

            // Get the file extension
            var fileExtension = System.IO.Path.GetExtension(unknownDoc.NewDocumentPath);

            // Find the matching supported file type
            var supportedFileType = supportedFileTypes.FirstOrDefault(ft =>
                string.Equals(ft.FileExtension, fileExtension, StringComparison.OrdinalIgnoreCase));

            // Only process files with supported file types
            if (supportedFileType == null)
                continue;

            // Create the row view model
            var rowViewModel = new NewDocumentRowViewModel(
                unknownDoc.NewDocumentPath,
                supportedFileType,
                existingDocumentNumbers,
                revisionPrefix,
                revisionSuffix,
                _customFieldDefinitions,
                ValidateRow); // Pass validation callback

            // Skip documents without revision indicators (they shouldn't be shown)
            if (rowViewModel.Status == NewDocumentRowStatus.NoRevisionIndicator)
                continue;

            DocumentRows.Add(rowViewModel);

            // Track the proposed document number for duplicate detection within the list
            // Only track if it's a valid document number (not empty and not missing doc name)
            if (!string.IsNullOrEmpty(rowViewModel.ProposedDocumentNumber) &&
                rowViewModel.Status != NewDocumentRowStatus.MissingDocumentName)
            {
                if (!proposedDocumentNumbers.ContainsKey(rowViewModel.ProposedDocumentNumber))
                {
                    proposedDocumentNumbers[rowViewModel.ProposedDocumentNumber] = new List<NewDocumentRowViewModel>();
                }
                proposedDocumentNumbers[rowViewModel.ProposedDocumentNumber].Add(rowViewModel);
            }
        }

        // Check for duplicates within the list (same document number, different file types)
        foreach (var kvp in proposedDocumentNumbers)
        {
            if (kvp.Value.Count > 1)
            {
                // Group by file extension
                var groupedByExtension = kvp.Value.GroupBy(vm => vm.FileExtension);

                // Check if there are duplicates with the same file extension
                foreach (var extensionGroup in groupedByExtension)
                {
                    if (extensionGroup.Count() > 1)
                    {
                        // Multiple files with same extension and same document number - this is an error
                        foreach (var duplicate in extensionGroup)
                        {
                            duplicate.Status = NewDocumentRowStatus.DuplicateInList;
                            duplicate.StatusMessage = $"Duplicate document number in list with same file type";
                        }
                    }
                }

                // Different file extensions with same document number is OK
            }
        }

        // Update counts
        UpdateCounts();
    }

    /// <summary>
    /// Updates all count properties
    /// </summary>
    private void UpdateCounts()
    {
        OnPropertyChanged(nameof(ReadyToAddCount));
        OnPropertyChanged(nameof(DuplicateCount));
        OnPropertyChanged(nameof(TotalCount));

        // Update OK button state
        OkCommand.NotifyCanExecuteChanged();
    }

    /// <summary>
    /// Validates a single row when its document number changes
    /// </summary>
    private void ValidateRow(NewDocumentRowViewModel row)
    {
        // Get existing document numbers for validation
        var existingDocumentNumbers = new HashSet<string>(
            _existingDocuments.Select(d => d.Number),
            StringComparer.OrdinalIgnoreCase);

        // Validate this row against database and other rows
        row.Validate(existingDocumentNumbers, DocumentRows);

        // Update counts after validation
        UpdateCounts();
    }

    #endregion
}
