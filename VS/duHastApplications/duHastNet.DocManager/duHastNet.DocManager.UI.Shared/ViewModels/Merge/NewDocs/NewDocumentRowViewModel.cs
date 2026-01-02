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
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Models.Database;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge.NewDocs;

/// <summary>
/// ViewModel representing a single row in the Add New Documents dialog
/// </summary>
public partial class NewDocumentRowViewModel : ObservableObject
{
    #region Observable Properties

    /// <summary>
    /// The unknown file name (without path)
    /// </summary>
    [ObservableProperty]
    private string _fileName = string.Empty;

    /// <summary>
    /// The file extension
    /// </summary>
    [ObservableProperty]
    private string _fileExtension = string.Empty;

    /// <summary>
    /// The proposed document number (extracted from filename and modified per file type rules)
    /// </summary>
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CanAdd))]
    private string _proposedDocumentNumber = string.Empty;

    /// <summary>
    /// The proposed document name (default: same as document number)
    /// </summary>
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CanAdd))]
    private string _proposedDocumentName = string.Empty;

    /// <summary>
    /// Indicates whether the proposed document number matches the filename
    /// True if they match, False if the document number modifier changed them
    /// </summary>
    [ObservableProperty]
    private bool _numberMatchesFileName;

    /// <summary>
    /// The status of this document row
    /// </summary>
    [ObservableProperty]
    private NewDocumentRowStatus _status;

    /// <summary>
    /// Status message for display
    /// </summary>
    [ObservableProperty]
    private string _statusMessage = string.Empty;

    /// <summary>
    /// The full file path
    /// </summary>
    [ObservableProperty]
    private string _fullFilePath = string.Empty;

    /// <summary>
    /// The supported file type information
    /// </summary>
    [ObservableProperty]
    private SupportedFileType? _supportedFileType;

    /// <summary>
    /// The original filename without extension (before applying document number modifier)
    /// </summary>
    [ObservableProperty]
    private string _originalFileNameWithoutExtension = string.Empty;

    /// <summary>
    /// Callback to validate document number changes
    /// </summary>
    private Action<NewDocumentRowViewModel>? _validationCallback;

    /// <summary>
    /// Collection of custom field values for this document
    /// </summary>
    [ObservableProperty]
    private ObservableCollection<CustomFieldValueViewModel> _customFieldValues = new();

    #endregion

    #region Computed Properties

    /// <summary>
    /// Gets the status color for UI display
    /// </summary>
    public string StatusColor => Status switch
    {
        NewDocumentRowStatus.ReadyToAdd => "Green",
        NewDocumentRowStatus.DuplicateDocumentNumber => "Red",
        NewDocumentRowStatus.DuplicateInList => "Red",
        NewDocumentRowStatus.NumberDoesNotMatchFileName => "Red",
        NewDocumentRowStatus.NoRevisionIndicator => "Orange",
        NewDocumentRowStatus.MissingDocumentName => "Red",
        _ => "Gray"
    };

    /// <summary>
    /// Gets whether this row represents a valid document that can be added
    /// </summary>
    public bool CanAdd => Status == NewDocumentRowStatus.ReadyToAdd;

    #endregion

    #region Constructor

    /// <summary>
    /// Creates a new instance of NewDocumentRowViewModel
    /// </summary>
    public NewDocumentRowViewModel()
    {
    }

    /// <summary>
    /// Creates a NewDocumentRowViewModel from file information
    /// </summary>
    /// <param name="filePath">The full path to the file</param>
    /// <param name="supportedFileType">The supported file type configuration</param>
    /// <param name="existingDocumentNumbers">List of existing document numbers in the database</param>
    /// <param name="revisionPrefix">The revision prefix character (e.g., '[')</param>
    /// <param name="revisionSuffix">The revision suffix character (e.g., ']')</param>
    /// <param name="customFieldDefinitions">List of custom field definitions to create value placeholders for</param>
    /// <param name="validationCallback">Callback to invoke when validation is needed</param>
    public NewDocumentRowViewModel(
        string filePath,
        SupportedFileType supportedFileType,
        HashSet<string> existingDocumentNumbers,
        string? revisionPrefix,
        string? revisionSuffix,
        IEnumerable<CustomFieldDefinition>? customFieldDefinitions = null,
        Action<NewDocumentRowViewModel>? validationCallback = null)
    {
        FullFilePath = filePath;
        SupportedFileType = supportedFileType;
        _validationCallback = validationCallback;

        // Initialize custom field values from definitions
        CustomFieldValues = new ObservableCollection<CustomFieldValueViewModel>();
        if (customFieldDefinitions != null)
        {
            foreach (var definition in customFieldDefinitions)
            {
                CustomFieldValues.Add(new CustomFieldValueViewModel(definition));
            }
        }

        // Extract filename and extension
        FileName = System.IO.Path.GetFileName(filePath);
        FileExtension = System.IO.Path.GetExtension(filePath);

        // Get filename without extension
        OriginalFileNameWithoutExtension = System.IO.Path.GetFileNameWithoutExtension(filePath);

        // Check if the filename contains revision separators
        bool hasRevisionSeparators = !string.IsNullOrEmpty(revisionPrefix) &&
                                     !string.IsNullOrEmpty(revisionSuffix) &&
                                     OriginalFileNameWithoutExtension.Contains(revisionPrefix) &&
                                     OriginalFileNameWithoutExtension.Contains(revisionSuffix);

        if (!hasRevisionSeparators)
        {
            // No revision separators found - this document should not be shown
            Status = NewDocumentRowStatus.NoRevisionIndicator;
            StatusMessage = "No revision indicator found in filename";
            ProposedDocumentNumber = string.Empty;
            ProposedDocumentName = string.Empty;
            NumberMatchesFileName = false;
            return;
        }

        // Find the revision prefix position
        int revisionPrefixIndex = OriginalFileNameWithoutExtension.IndexOf(revisionPrefix);

        // Extract document number (everything before revision prefix)
        string documentNumberPart = OriginalFileNameWithoutExtension.Substring(0, revisionPrefixIndex).Trim();

        // Find the revision suffix position (after the prefix)
        int revisionSuffixIndex = OriginalFileNameWithoutExtension.IndexOf(revisionSuffix, revisionPrefixIndex);

        // Extract document name (everything after revision suffix)
        string documentNamePart = string.Empty;
        if (revisionSuffixIndex >= 0 && revisionSuffixIndex < OriginalFileNameWithoutExtension.Length - 1)
        {
            documentNamePart = OriginalFileNameWithoutExtension.Substring(revisionSuffixIndex + revisionSuffix.Length).Trim();
        }

        // Apply document number modifier if present
        ProposedDocumentNumber = supportedFileType.GetModifiedDocumentNumber(documentNumberPart);

        // Set proposed name
        ProposedDocumentName = documentNamePart;

        // Check if document name is missing (revision at the end of filename)
        if (string.IsNullOrWhiteSpace(documentNamePart))
        {
            Status = NewDocumentRowStatus.MissingDocumentName;
            StatusMessage = "Missing document name - revision indicator at end of filename";
            NumberMatchesFileName = false;
            return;
        }

        // Check if the proposed document number matches the filename part
        // (considering the file type modifier)
        // We need to check if applying the modifier to the proposed doc number gives us back the original filename part
        string modifiedDocNumber = supportedFileType.GetModifiedDocumentNumber(ProposedDocumentNumber);
        NumberMatchesFileName = string.Equals(
            modifiedDocNumber,
            documentNumberPart,
            StringComparison.OrdinalIgnoreCase);

        // Check for duplicate document numbers
        if (existingDocumentNumbers.Contains(ProposedDocumentNumber))
        {
            Status = NewDocumentRowStatus.DuplicateDocumentNumber;
            StatusMessage = "Document number already exists in database";
        }
        else
        {
            Status = NewDocumentRowStatus.ReadyToAdd;
            StatusMessage = "Ready to add";
        }
    }

    #endregion

    #region Property Change Handlers

    /// <summary>
    /// Called when Status changes - updates status color
    /// </summary>
    partial void OnStatusChanged(NewDocumentRowStatus value)
    {
        OnPropertyChanged(nameof(StatusColor));
        OnPropertyChanged(nameof(CanAdd));
    }

    /// <summary>
    /// Called when ProposedDocumentNumber changes - triggers validation
    /// </summary>
    partial void OnProposedDocumentNumberChanged(string value)
    {
        // Invoke validation callback to check for duplicates across all rows
        _validationCallback?.Invoke(this);
    }

    /// <summary>
    /// Called when ProposedDocumentName changes - triggers validation
    /// </summary>
    partial void OnProposedDocumentNameChanged(string value)
    {
        // Invoke validation callback to re-validate status
        _validationCallback?.Invoke(this);
    }

    #endregion

    #region Public Methods

    /// <summary>
    /// Validates this row against existing document numbers
    /// Called by the dialog ViewModel during validation
    /// </summary>
    /// <param name="existingDocumentNumbers">Set of existing document numbers in the database</param>
    /// <param name="allRows">All rows in the dialog for duplicate checking</param>
    internal void Validate(HashSet<string> existingDocumentNumbers, IEnumerable<Merge.NewDocs.NewDocumentRowViewModel> allRows)
    {
        // Don't validate if this row has fundamental issues (no revision indicator)
        if (Status == NewDocumentRowStatus.NoRevisionIndicator)
        {
            return;
        }

        // Check for empty document number
        if (string.IsNullOrWhiteSpace(ProposedDocumentNumber))
        {
            Status = NewDocumentRowStatus.MissingDocumentName;
            StatusMessage = "Document number is required";
            return;
        }

        // Check for missing document name
        if (string.IsNullOrWhiteSpace(ProposedDocumentName))
        {
            Status = NewDocumentRowStatus.MissingDocumentName;
            StatusMessage = "Document name is required";
            return;
        }

        // Check for duplicate in database
        if (existingDocumentNumbers.Contains(ProposedDocumentNumber.Trim()))
        {
            Status = NewDocumentRowStatus.DuplicateDocumentNumber;
            StatusMessage = "Document number already exists in database";
            return;
        }

        // Check for duplicates in the current list (same doc number AND same file extension)
        var duplicates = allRows
            .Where(r => r != this &&
                   string.Equals(r.ProposedDocumentNumber?.Trim(), ProposedDocumentNumber.Trim(), StringComparison.OrdinalIgnoreCase) &&
                   string.Equals(r.FileExtension, FileExtension, StringComparison.OrdinalIgnoreCase))
            .ToList();

        if (duplicates.Any())
        {
            Status = NewDocumentRowStatus.DuplicateInList;
            StatusMessage = "Duplicate document number in list with same file type";
            return;
        }

        // Check if number matches filename
        // The document number (with modifier applied) should be at the start of the filename
        bool numberMatches = false;
        if (SupportedFileType != null)
        {
            var modifiedDocNumber = SupportedFileType.GetModifiedDocumentNumber(ProposedDocumentNumber.Trim());
            numberMatches = OriginalFileNameWithoutExtension.StartsWith(
                modifiedDocNumber,
                StringComparison.OrdinalIgnoreCase);
            NumberMatchesFileName = numberMatches;
        }

        // If number doesn't match filename, this is a blocking error
        if (!numberMatches)
        {
            Status = NewDocumentRowStatus.NumberDoesNotMatchFileName;
            StatusMessage = "Document number does not match file name";
            return;
        }

        // All validations passed
        Status = NewDocumentRowStatus.ReadyToAdd;
        StatusMessage = "Ready to add";
    }

    #endregion
}

/// <summary>
/// Enum representing the status of a new document row
/// </summary>
public enum NewDocumentRowStatus
{
    /// <summary>
    /// Document is ready to be added
    /// </summary>
    ReadyToAdd,

    /// <summary>
    /// Document number already exists in the database
    /// </summary>
    DuplicateDocumentNumber,

    /// <summary>
    /// Document number is duplicated within the current list of documents being added
    /// </summary>
    DuplicateInList,

    /// <summary>
    /// No revision indicator found in filename
    /// </summary>
    NoRevisionIndicator,

    /// <summary>
    /// Missing document name - revision indicator at end of filename
    /// </summary>
    MissingDocumentName,

    /// <summary>
    /// Document number does not match the file name
    /// </summary>
    NumberDoesNotMatchFileName
}
