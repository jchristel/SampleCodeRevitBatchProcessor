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

namespace duHastNet.DocManager.UI.Shared.ViewModels.Transmittal;

/// <summary>
/// Represents a single revision row in the Transmittal revisions grid.
/// </summary>
public partial class TransmittalRevisionRowViewModel : ObservableObject
{
    #region Private Fields

    private readonly Action _onCheckedChanged;

    #endregion

    #region Observable Properties

    [ObservableProperty]
    private bool _isChecked;

    #endregion

    #region Public Properties

    /// <summary>
    /// Internal database ID — not displayed in the grid.
    /// </summary>
    public int RevisionId { get; }

    /// <summary>
    /// Revision date displayed in the Date column.
    /// </summary>
    public DateTime RevisionDate { get; }

    /// <summary>
    /// Revision description displayed in the Description column.
    /// </summary>
    public string RevisionDescription { get; }

    /// <summary>
    /// IDs of documents associated with this revision.
    /// Used to filter the documents grid in ByRevision mode.
    /// </summary>
    public IReadOnlyList<int> DocumentIds { get; }

    #endregion

    #region Constructor

    /// <summary>
    /// Creates a new instance of TransmittalRevisionRowViewModel.
    /// </summary>
    /// <param name="revisionId">Database ID of the revision.</param>
    /// <param name="revisionDate">Date of the revision.</param>
    /// <param name="revisionDescription">Description of the revision.</param>
    /// <param name="documentIds">Document IDs belonging to this revision.</param>
    /// <param name="onCheckedChanged">Callback invoked when IsChecked changes.</param>
    /// <exception cref="ArgumentNullException">Thrown when onCheckedChanged is null.</exception>
    public TransmittalRevisionRowViewModel(
        int revisionId,
        DateTime revisionDate,
        string revisionDescription,
        IReadOnlyList<int> documentIds,
        Action onCheckedChanged)
    {
        ArgumentNullException.ThrowIfNull(onCheckedChanged);

        RevisionId = revisionId;
        RevisionDate = revisionDate;
        RevisionDescription = revisionDescription ?? string.Empty;
        DocumentIds = documentIds ?? Array.Empty<int>();
        _onCheckedChanged = onCheckedChanged;
    }

    #endregion

    #region Property Change Handlers

    partial void OnIsCheckedChanged(bool value)
    {
        _onCheckedChanged();
    }

    #endregion
}
