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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.UI.Shared.Interfaces;
using System.Collections.ObjectModel;
using System.Text;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge.NewDocs;

/// <summary>
/// ViewModel for the Add New Documents dialog
/// Handles the display and processing of unknown documents from the incoming folder
/// </summary>
public partial class AddNewDocumentsDialogViewModel : ObservableObject
{
    #region Private Fields

    private readonly ICurrentFolderManager _currentFolderManager;
    private readonly List<Document> _existingDocuments;
    private readonly List<CustomFieldDefinition> _customFieldDefinitions;
    private readonly IDialogService _dialogService;

    #endregion

    #region Observable Properties

    /// <summary>
    /// Collection of new document rows for display
    /// </summary>
    [ObservableProperty]
    private ObservableCollection<Merge.NewDocs.NewDocumentRowViewModel> _documentRows;

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
        d.Status == Merge.NewDocs.NewDocumentRowStatus.DuplicateDocumentNumber ||
        d.Status == Merge.NewDocs.NewDocumentRowStatus.DuplicateInList) ?? 0;

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
    /// <param name="dialogService">Dialog service for user interactions</param>
    /// <param name="customFieldDefinitions">List of custom field definitions for the new documents</param>
    public AddNewDocumentsDialogViewModel(
        ICurrentFolderManager currentFolderManager,
        List<Document> existingDocuments,
        List<IncomingDocumentProcessingStatus> unknownDocuments,
        IDialogService dialogService,
        List<CustomFieldDefinition>? customFieldDefinitions = null)
    {
        _currentFolderManager = currentFolderManager ?? throw new ArgumentNullException(nameof(currentFolderManager));
        _existingDocuments = existingDocuments ?? throw new ArgumentNullException(nameof(existingDocuments));
        _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));
        _customFieldDefinitions = customFieldDefinitions ?? new List<CustomFieldDefinition>();

        _documentRows = new ObservableCollection<Merge.NewDocs.NewDocumentRowViewModel>();

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
    /// Returns only unique document numbers - if multiple file types exist for the same document number,
    /// only the first occurrence is returned
    /// </summary>
    public List<Merge.NewDocs.NewDocumentRowViewModel> GetDocumentsToAdd()
    {
        return DocumentRows
            .Where(d => d.CanAdd)
            .GroupBy(d => d.ProposedDocumentNumber, StringComparer.OrdinalIgnoreCase)
            .Select(g => g.First())
            .ToList();
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
        var proposedDocumentNumbers = new Dictionary<string, List<Merge.NewDocs.NewDocumentRowViewModel>>(StringComparer.OrdinalIgnoreCase);

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
            var rowViewModel = new Merge.NewDocs.NewDocumentRowViewModel(
                unknownDoc.NewDocumentPath,
                supportedFileType,
                existingDocumentNumbers,
                revisionPrefix,
                revisionSuffix,
                _customFieldDefinitions,
                ValidateRow,
                HandleRelatedFiles); // Pass related files callback

            // Skip documents without revision indicators (they shouldn't be shown)
            if (rowViewModel.Status == Merge.NewDocs.NewDocumentRowStatus.NoRevisionIndicator)
                continue;

            DocumentRows.Add(rowViewModel);

            // Track the proposed document number for duplicate detection within the list
            // Only track if it's a valid document number (not empty and not missing doc name)
            if (!string.IsNullOrEmpty(rowViewModel.ProposedDocumentNumber) &&
                rowViewModel.Status != Merge.NewDocs.NewDocumentRowStatus.MissingDocumentName)
            {
                if (!proposedDocumentNumbers.ContainsKey(rowViewModel.ProposedDocumentNumber))
                {
                    proposedDocumentNumbers[rowViewModel.ProposedDocumentNumber] = new List<Merge.NewDocs.NewDocumentRowViewModel>();
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
                            duplicate.Status = Merge.NewDocs.NewDocumentRowStatus.DuplicateInList;
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
    private void ValidateRow(Merge.NewDocs.NewDocumentRowViewModel row)
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

    /// <summary>
    /// Handles related files detection when document number or name changes
    /// </summary>
    private void HandleRelatedFiles(Merge.NewDocs.NewDocumentRowViewModel changedRow, List<Merge.NewDocs.NewDocumentRowViewModel> _)
    {
        // Determine if this is a document number change or document name change
        // by checking which property triggered the callback
        
        // Check if document number was shortened (potential for finding related files)
        var relatedFiles = FindRelatedFilesByDocumentNumber(changedRow);
        
        if (relatedFiles.Any())
        {
            // Document number was shortened - ask user for confirmation
            HandleDocumentNumberShorteningWithConfirmation(changedRow, relatedFiles);
        }
        else
        {
            // Check if document name changed and needs synchronization
            var sameDocumentFiles = FindFilesBySameDocumentNumber(changedRow);
            
            if (sameDocumentFiles.Any())
            {
                // Document name changed - silently synchronize
                SynchronizeDocumentNames(changedRow, sameDocumentFiles);
            }
        }
    }

    /// <summary>
    /// Finds related files where their document number starts with the changed row's document number
    /// (indicating they may belong to the same document but have longer document numbers)
    /// </summary>
    private List<Merge.NewDocs.NewDocumentRowViewModel> FindRelatedFilesByDocumentNumber(Merge.NewDocs.NewDocumentRowViewModel changedRow)
    {
        if (string.IsNullOrWhiteSpace(changedRow.ProposedDocumentNumber))
        {
            return new List<Merge.NewDocs.NewDocumentRowViewModel>();
        }

        var relatedFiles = DocumentRows
            .Where(r => r != changedRow &&
                   !string.Equals(r.FileExtension, changedRow.FileExtension, StringComparison.OrdinalIgnoreCase) &&
                   !string.IsNullOrWhiteSpace(r.ProposedDocumentNumber) &&
                   r.ProposedDocumentNumber.StartsWith(changedRow.ProposedDocumentNumber, StringComparison.OrdinalIgnoreCase) &&
                   r.ProposedDocumentNumber.Length > changedRow.ProposedDocumentNumber.Length)
            .ToList();

        return relatedFiles;
    }

    /// <summary>
    /// Finds files with the same document number as the changed row (different file extensions)
    /// </summary>
    private List<Merge.NewDocs.NewDocumentRowViewModel> FindFilesBySameDocumentNumber(Merge.NewDocs.NewDocumentRowViewModel changedRow)
    {
        if (string.IsNullOrWhiteSpace(changedRow.ProposedDocumentNumber))
        {
            return new List<Merge.NewDocs.NewDocumentRowViewModel>();
        }

        var sameDocumentFiles = DocumentRows
            .Where(r => r != changedRow &&
                   !string.Equals(r.FileExtension, changedRow.FileExtension, StringComparison.OrdinalIgnoreCase) &&
                   string.Equals(r.ProposedDocumentNumber, changedRow.ProposedDocumentNumber, StringComparison.OrdinalIgnoreCase))
            .ToList();

        return sameDocumentFiles;
    }

    /// <summary>
    /// Handles document number shortening by asking user for confirmation and updating related files
    /// </summary>
    private void HandleDocumentNumberShorteningWithConfirmation(
        Merge.NewDocs.NewDocumentRowViewModel changedRow,
        List<Merge.NewDocs.NewDocumentRowViewModel> relatedFiles)
    {
        // Build the confirmation message
        var messageBuilder = new StringBuilder();
        messageBuilder.AppendLine("The following files may belong to the same document:");
        messageBuilder.AppendLine();
        
        foreach (var relatedFile in relatedFiles)
        {
            messageBuilder.AppendLine($"  • {relatedFile.FileName}");
        }
        
        messageBuilder.AppendLine();
        messageBuilder.AppendLine("Update these files to use the same document number?");

        // Show confirmation dialog
        var result = _dialogService.ShowMessageBox(
            messageBuilder.ToString(),
            "Related Files Detected",
            System.Windows.MessageBoxButton.YesNo,
            System.Windows.MessageBoxImage.Question);

        if (result == System.Windows.MessageBoxResult.Yes)
        {
            // User confirmed - update all related files
            UpdateRelatedFilesDocumentNumber(changedRow.ProposedDocumentNumber, relatedFiles);
        }
    }

    /// <summary>
    /// Updates the document number for all related files
    /// </summary>
    private void UpdateRelatedFilesDocumentNumber(string newDocumentNumber, List<Merge.NewDocs.NewDocumentRowViewModel> filesToUpdate)
    {
        // Get existing document numbers for validation
        var existingDocumentNumbers = new HashSet<string>(
            _existingDocuments.Select(d => d.Number),
            StringComparer.OrdinalIgnoreCase);

        // Update each file
        foreach (var file in filesToUpdate)
        {
            // Update the document number programmatically (without triggering callbacks)
            file.UpdateDocumentNumberProgrammatically(newDocumentNumber);
            
            // Validate the updated row
            file.Validate(existingDocumentNumbers, DocumentRows);
        }

        // Update counts after all changes
        UpdateCounts();
    }

    /// <summary>
    /// Silently synchronizes document names for files with the same document number
    /// </summary>
    private void SynchronizeDocumentNames(
        Merge.NewDocs.NewDocumentRowViewModel changedRow,
        List<Merge.NewDocs.NewDocumentRowViewModel> sameDocumentFiles)
    {
        // Get existing document numbers for validation
        var existingDocumentNumbers = new HashSet<string>(
            _existingDocuments.Select(d => d.Number),
            StringComparer.OrdinalIgnoreCase);

        // Update each file's document name
        foreach (var file in sameDocumentFiles)
        {
            // Update the document name programmatically (without triggering callbacks)
            file.UpdateDocumentNameProgrammatically(changedRow.ProposedDocumentName);
            
            // Validate the updated row
            file.Validate(existingDocumentNumbers, DocumentRows);
        }

        // Update counts after all changes
        UpdateCounts();
    }

    #endregion
}
