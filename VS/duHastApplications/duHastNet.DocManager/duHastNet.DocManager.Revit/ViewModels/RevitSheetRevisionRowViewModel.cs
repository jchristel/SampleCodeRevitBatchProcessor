//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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
using duHastNet.DocManager.Revit.Utilities.RevitData;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// Row ViewModel for the Revisions panel DataGrid.
    /// Wraps a Revit sheet that has a matching document in the database and exposes the
    /// revision synchronisation status between the Revit model and the database.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Status colour precedence (highest to lowest):
    /// </para>
    /// <list type="bullet">
    ///   <item>
    ///     <term>Grey</term>
    ///     <description>
    ///       At least one revision on the sheet has <see cref="RevitRevision.IsDateValid"/>
    ///       equal to <c>false</c> (i.e. <see cref="RevitRevision.ParsedDate"/> is null).
    ///       The row cannot be selected. The revision date must be corrected in Revit first.
    ///       Status message: "Revision(s) with invalid date". When valid-date revisions on the
    ///       same sheet are also unrecorded, <see cref="HasUnrecordedRevisionsWithInvalidDate"/>
    ///       is additionally set and the message reflects both problems.
    ///     </description>
    ///   </item>
    ///   <item>
    ///     <term>Red</term>
    ///     <description>
    ///       All dates are valid but at least one revision has no matching
    ///       <see cref="Revision"/> in the database. Matching compares
    ///       <see cref="RevitRevision.ParsedDate"/> directly against
    ///       <see cref="Revision.RevisionDate"/> — locale-format safe.
    ///     </description>
    ///   </item>
    ///   <item>
    ///     <term>Yellow</term>
    ///     <description>
    ///       All revisions match database entries but at least one is not recorded in the
    ///       document's revision indicator history, or the document's current revision
    ///       indicator does not match the latest sheet revision indicator.
    ///     </description>
    ///   </item>
    ///   <item>
    ///     <term>Green</term>
    ///     <description>All revisions are valid, exist in the database, and are fully applied.</description>
    ///   </item>
    /// </list>
    /// </remarks>
    public partial class RevitSheetRevisionRowViewModel : AppViewModelBase
    {
        #region Private Fields

        private readonly Action? _onSelectionChanged;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// Gets or sets whether this row is selected by the user for the Update operation.
        /// Grey rows (invalid revision date) cannot be selected.
        /// </summary>
        [ObservableProperty]
        private bool _isSelected;

        /// <summary>Gets the Revit sheet number as read from the model.</summary>
        [ObservableProperty]
        private string _sheetNumber = string.Empty;

        /// <summary>Gets the Revit sheet name as read from the model.</summary>
        [ObservableProperty]
        private string _sheetName = string.Empty;

        /// <summary>Gets the built document number.</summary>
        [ObservableProperty]
        private string _documentNumber = string.Empty;

        /// <summary>Gets the built document name.</summary>
        [ObservableProperty]
        private string _documentName = string.Empty;

        /// <summary>
        /// Gets the revision indicator of the most recent revision on the sheet in Revit,
        /// or an empty string when the sheet carries no revisions.
        /// </summary>
        [ObservableProperty]
        private string _currentRevitRevision = string.Empty;

        /// <summary>Gets the current revision indicator stored on the database document.</summary>
        [ObservableProperty]
        private string _currentDatabaseRevision = string.Empty;

        /// <summary>
        /// Gets whether at least one revision on the sheet has an unparseable date string.
        /// Grey status — takes precedence over all other status values.
        /// </summary>
        [ObservableProperty]
        private bool _hasInvalidRevisionDate;

        /// <summary>
        /// Gets whether at least one revision on the sheet has no matching database revision.
        /// Red status — only evaluated when <see cref="HasInvalidRevisionDate"/> is <c>false</c>.
        /// </summary>
        [ObservableProperty]
        private bool _hasUnknownRevisions;

        /// <summary>
        /// Gets whether every revision exists in the database but at least one is not recorded
        /// in the document's revision indicator history, or the current revision indicator does
        /// not match the latest sheet revision indicator.
        /// Yellow status — only evaluated when both grey and red flags are <c>false</c>.
        /// </summary>
        [ObservableProperty]
        private bool _hasUnrecordedRevisions;

        /// <summary>
        /// Gets whether the sheet has at least one revision with an invalid date AND at least
        /// one valid revision that is not yet recorded in the document's revision indicator history.
        /// When <c>true</c>, the row remains Grey (invalid date takes precedence) but the status
        /// message includes the unrecorded-revision detail alongside the invalid-date warning.
        /// </summary>
        [ObservableProperty]
        private bool _hasUnrecordedRevisionsWithInvalidDate;

        #endregion Observable Properties

        #region Computed Properties

        /// <summary>
        /// Gets the WPF colour name for the status indicator ellipse.
        /// Precedence: Grey > Red > Yellow > Green.
        /// </summary>
        public string StatusColor
        {
            get
            {
                if (HasInvalidRevisionDate) return "Grey";
                if (HasUnknownRevisions) return "Red";
                if (HasUnrecordedRevisions) return "Yellow";
                return "Green";
            }
        }

        /// <summary>Gets a human-readable status description.</summary>
        public string StatusMessage
        {
            get
            {
                if (HasInvalidRevisionDate)
                    return HasUnrecordedRevisionsWithInvalidDate
                        ? "Revision(s) with invalid date and revision(s) with valid date not yet applied to this document"
                        : "Revision(s) with invalid date";
                if (HasUnknownRevisions)
                    return "One or more revisions on this sheet do not exist in the database";
                if (HasUnrecordedRevisions)
                    return "All revisions exist in the database but are not fully applied to this document";
                return "Revision history up to date";
            }
        }

        /// <summary>
        /// Gets whether this row can be selected and updated.
        /// Grey rows are never selectable.
        /// </summary>
        public bool IsSelectable => !HasInvalidRevisionDate;

        /// <summary>
        /// Gets whether this row requires any database update (Yellow or Red, not Grey).
        /// </summary>
        public bool NeedsUpdate => !HasInvalidRevisionDate && (HasUnknownRevisions || HasUnrecordedRevisions);

        #endregion Computed Properties

        #region Constructor

        /// <summary>
        /// Initializes a new <see cref="RevitSheetRevisionRowViewModel"/>.
        /// </summary>
        /// <param name="sheet">The Revit sheet. Must not be null.</param>
        /// <param name="document">The matching database document. Must not be null.</param>
        /// <param name="databaseRevisions">All revisions currently in the database. Must not be null.</param>
        /// <param name="onSelectionChanged">
        /// Optional callback invoked whenever <see cref="IsSelected"/> changes.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="sheet"/>, <paramref name="document"/>, or
        /// <paramref name="databaseRevisions"/> is null.
        /// </exception>
        public RevitSheetRevisionRowViewModel(
            RevitSheet sheet,
            Document document,
            IEnumerable<Revision> databaseRevisions,
            Action? onSelectionChanged = null)
        {
            _ = sheet ?? throw new ArgumentNullException(nameof(sheet));
            _ = document ?? throw new ArgumentNullException(nameof(document));
            _ = databaseRevisions ?? throw new ArgumentNullException(nameof(databaseRevisions));

            _onSelectionChanged = onSelectionChanged;

            SheetNumber = sheet.SheetNumber?.Value ?? string.Empty;
            SheetName = sheet.SheetName?.Value ?? string.Empty;

            sheet.BuiltDocumentProperties.TryGetValue(
                duHastNet.UI.DocManagerSettingsUI.Utils.Constants.DocumentPropertyKeyDocumentNumber,
                out string? builtNumber);
            DocumentNumber = builtNumber ?? SheetNumber;

            sheet.BuiltDocumentProperties.TryGetValue(
                duHastNet.UI.DocManagerSettingsUI.Utils.Constants.DocumentPropertyKeyDocumentName,
                out string? builtName);
            DocumentName = builtName ?? SheetName;

            var lastRevisionOnSheet = sheet.RevisionsOnSheet.LastOrDefault();
            CurrentRevitRevision = lastRevisionOnSheet?.RevisionIndicator ?? string.Empty;
            CurrentDatabaseRevision = document.Revision;

            EvaluateStatus(sheet.RevisionsOnSheet, document, databaseRevisions);
        }

        #endregion Constructor

        #region Private Helpers

        /// <summary>
        /// Evaluates all status flags.
        /// <para>
        /// Grey check runs first: if any revision has <see cref="RevitRevision.IsDateValid"/>
        /// equal to <c>false</c>, <see cref="HasInvalidRevisionDate"/> is set. The method then
        /// continues to check whether any of the valid-date revisions on the sheet are also
        /// unrecorded in the database, setting <see cref="HasUnrecordedRevisionsWithInvalidDate"/>
        /// so the status message can reflect both problems simultaneously. All date comparisons
        /// use <see cref="RevitRevision.ParsedDate"/> directly against
        /// <see cref="Revision.RevisionDate"/> — no string formatting involved.
        /// </para>
        /// </summary>
        private void EvaluateStatus(
            IEnumerable<RevitRevisionOnSheet> revisionsOnSheet,
            Document document,
            IEnumerable<Revision> databaseRevisions)
        {
            var sheetRevisionList = revisionsOnSheet.ToList();
            var dbRevisionList = databaseRevisions.ToList();

            // ── Grey: check for invalid dates first ───────────────────────────
            bool invalidDateFound = sheetRevisionList.Any(r => !r.RevitRevision.IsDateValid);
            HasInvalidRevisionDate = invalidDateFound;

            // ── Red / Yellow: evaluate valid-date revisions ───────────────────
            bool unknownFound = false;
            bool unrecordedFound = false;

            foreach (var revOnSheet in sheetRevisionList)
            {
                // Skip revisions with invalid dates — they cannot be matched.
                if (!revOnSheet.RevitRevision.IsDateValid)
                    continue;

                DateTime revitDate = revOnSheet.RevitRevision.ParsedDate!.Value.Date;

                var matchedDbRevision = dbRevisionList.FirstOrDefault(dbRev =>
                    dbRev.RevisionDate.Date == revitDate &&
                    dbRev.Description == revOnSheet.RevitRevision.RevisionDescription);

                if (matchedDbRevision == null)
                {
                    unknownFound = true;
                    continue;
                }

                if (!document.HasRevisionIndicator(matchedDbRevision.Id))
                    unrecordedFound = true;
            }

            // Yellow also fires if the document's current revision indicator does not match
            // the latest valid revision indicator on the sheet.
            var validRevisions = sheetRevisionList.Where(r => r.RevitRevision.IsDateValid).ToList();
            if (!unknownFound && validRevisions.Count > 0)
            {
                var lastValidRevOnSheet = validRevisions[validRevisions.Count - 1];
                if (document.Revision != lastValidRevOnSheet.RevisionIndicator)
                    unrecordedFound = true;
            }

            if (invalidDateFound)
            {
                // Grey takes precedence for colour — store unrecorded state in the mixed flag
                // so StatusMessage can surface both problems.
                HasUnrecordedRevisionsWithInvalidDate = unrecordedFound;
                HasUnknownRevisions = false;
                HasUnrecordedRevisions = false;
            }
            else
            {
                HasUnrecordedRevisionsWithInvalidDate = false;
                HasUnknownRevisions = unknownFound;
                HasUnrecordedRevisions = !unknownFound && unrecordedFound;
            }
        }

        #endregion Private Helpers

        #region Property Change Handlers

        partial void OnIsSelectedChanged(bool value)
        {
            if (value && HasInvalidRevisionDate)
            {
                _isSelected = false;
                return;
            }

            _onSelectionChanged?.Invoke();
        }

        partial void OnHasInvalidRevisionDateChanged(bool value)
        {
            OnPropertyChanged(nameof(StatusColor));
            OnPropertyChanged(nameof(StatusMessage));
            OnPropertyChanged(nameof(IsSelectable));
            OnPropertyChanged(nameof(NeedsUpdate));
        }

        partial void OnHasUnknownRevisionsChanged(bool value)
        {
            OnPropertyChanged(nameof(StatusColor));
            OnPropertyChanged(nameof(StatusMessage));
            OnPropertyChanged(nameof(NeedsUpdate));
        }

        partial void OnHasUnrecordedRevisionsChanged(bool value)
        {
            OnPropertyChanged(nameof(StatusColor));
            OnPropertyChanged(nameof(StatusMessage));
            OnPropertyChanged(nameof(NeedsUpdate));
        }

        partial void OnHasUnrecordedRevisionsWithInvalidDateChanged(bool value)
        {
            OnPropertyChanged(nameof(StatusMessage));
        }

        #endregion Property Change Handlers

        #region Re-evaluation

        /// <summary>
        /// Re-evaluates the revision status from refreshed database data.
        /// Called by the panel after a database reload.
        /// </summary>
        /// <exception cref="ArgumentNullException">Thrown when any parameter is null.</exception>
        public void Refresh(RevitSheet sheet, Document document, IEnumerable<Revision> databaseRevisions)
        {
            _ = sheet ?? throw new ArgumentNullException(nameof(sheet));
            _ = document ?? throw new ArgumentNullException(nameof(document));
            _ = databaseRevisions ?? throw new ArgumentNullException(nameof(databaseRevisions));

            CurrentDatabaseRevision = document.Revision;
            EvaluateStatus(sheet.RevisionsOnSheet, document, databaseRevisions);
            OnPropertyChanged(nameof(StatusColor));
            OnPropertyChanged(nameof(StatusMessage));
            OnPropertyChanged(nameof(IsSelectable));
            OnPropertyChanged(nameof(NeedsUpdate));
        }

        #endregion Re-evaluation
    }
}
