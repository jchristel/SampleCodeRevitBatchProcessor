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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CurrentFolder;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// ViewModel representing a matched document for display in the merge grid
/// </summary>
public partial class MatchedDocumentViewModel : ObservableObject
{
    #region Observable Properties

    /// <summary>
    /// The incoming file name (without path)
    /// </summary>
    [ObservableProperty]
    private string _incomingFileName = string.Empty;

    /// <summary>
    /// The full path to the incoming file
    /// </summary>
    [ObservableProperty]
    private string _incomingFilePath = string.Empty;

    /// <summary>
    /// The matched document number, if any
    /// </summary>
    [ObservableProperty]
    private string? _matchedDocumentNumber;

    /// <summary>
    /// The matched document name, if any
    /// </summary>
    [ObservableProperty]
    private string? _matchedDocumentName;

    /// <summary>
    /// The current revision of the matched document, if any
    /// </summary>
    [ObservableProperty]
    private string? _matchedDocumentRevision;

    /// <summary>
    /// The incoming document revision extracted from filename
    /// </summary>
    [ObservableProperty]
    private string? _incomingRevision;

    /// <summary>
    /// The match status of the document
    /// </summary>
    [ObservableProperty]
    private DocumentMatchStatus _matchStatus;

    /// <summary>
    /// A display-friendly status message
    /// </summary>
    [ObservableProperty]
    private string _statusMessage = string.Empty;

    /// <summary>
    /// The matched document ID in the database, if any
    /// </summary>
    [ObservableProperty]
    private int? _matchedDocumentId;

    /// <summary>
    /// Indicates if this row is selected by the user
    /// </summary>
    [ObservableProperty]
    private bool _isSelected;

    #endregion

    #region Computed Properties

    /// <summary>
    /// Gets the status color for UI display
    /// </summary>
    public string StatusColor => MatchStatus switch
    {
        DocumentMatchStatus.Ok => "Green",
        DocumentMatchStatus.WarningRevisionNotSequential => "Orange",
        DocumentMatchStatus.NoMatch => "Red",
        _ => "Gray"
    };

    /// <summary>
    /// Gets whether this document has a match
    /// </summary>
    public bool HasMatch => MatchedDocumentId.HasValue;

    /// <summary>
    /// Gets whether this is a new document (no match)
    /// </summary>
    public bool IsNewDocument => !HasMatch;

    #endregion

    #region Constructor

    /// <summary>
    /// Creates a new instance of MatchedDocumentViewModel
    /// </summary>
    public MatchedDocumentViewModel()
    {
    }

    /// <summary>
    /// Creates a MatchedDocumentViewModel from an IncomingDocumentProcessingStatus
    /// </summary>
    /// <param name="status">The processing status to convert</param>
    /// <param name="matchedDocument">The matched document from database, if any</param>
    public MatchedDocumentViewModel(IncomingDocumentProcessingStatus status, Document? matchedDocument)
    {
        IncomingFilePath = status.NewDocumentPath ?? string.Empty;
        IncomingFileName = System.IO.Path.GetFileName(IncomingFilePath);
        IncomingRevision = status.IncomingDocumentRevision;
        MatchedDocumentId = status.MatchedDocumentId;

        if (matchedDocument != null)
        {
            MatchedDocumentNumber = matchedDocument.Number;
            MatchedDocumentName = matchedDocument.Name;
            MatchedDocumentRevision = matchedDocument.Revision;

            // Determine match status based on revision comparison
            if (!string.IsNullOrEmpty(IncomingRevision) && !string.IsNullOrEmpty(matchedDocument.Revision))
            {
                // Check if revisions are sequential
                if (IsRevisionSequential(matchedDocument.Revision, IncomingRevision))
                {
                    MatchStatus = DocumentMatchStatus.Ok;
                    StatusMessage = "Match OK - Sequential revision";
                }
                else
                {
                    MatchStatus = DocumentMatchStatus.WarningRevisionNotSequential;
                    StatusMessage = $"Warning - Revision not sequential (Current: {matchedDocument.Revision}, Incoming: {IncomingRevision})";
                }
            }
            else
            {
                MatchStatus = DocumentMatchStatus.Ok;
                StatusMessage = "Match found";
            }
        }
        else
        {
            MatchStatus = DocumentMatchStatus.NoMatch;
            StatusMessage = "No match found";
        }
    }

    #endregion

    #region Private Helper Methods

    /// <summary>
    /// Determines if the incoming revision is sequential to the current revision
    /// This is a simplified check - actual implementation may need more sophisticated logic
    /// </summary>
    private bool IsRevisionSequential(string currentRevision, string incomingRevision)
    {
        // Try to parse as integers
        if (int.TryParse(currentRevision, out int currentInt) && 
            int.TryParse(incomingRevision, out int incomingInt))
        {
            return incomingInt == currentInt + 1;
        }

        // Try to parse as single characters (A, B, C, etc.)
        if (currentRevision.Length == 1 && incomingRevision.Length == 1)
        {
            char currentChar = currentRevision[0];
            char incomingChar = incomingRevision[0];
            return incomingChar == currentChar + 1;
        }

        // For complex revision schemes, we'll just return true for now
        // This can be enhanced based on specific business rules
        return true;
    }

    #endregion

    #region Property Change Handlers

    /// <summary>
    /// Called when MatchStatus changes - updates status color
    /// </summary>
    partial void OnMatchStatusChanged(DocumentMatchStatus value)
    {
        OnPropertyChanged(nameof(StatusColor));
    }

    #endregion
}
