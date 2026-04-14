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
    ///       At least one revision on the sheet has an unparseable date string
    ///       (<see cref="RevitRevision.IsDateValid"/> is <c>false</c>). The row cannot be
    ///       selected or imported. Status message: "Revision(s) with invalid date".
    ///     </description>
    ///   </item>
    ///   <item>
    ///     <term>Red</term>
    ///     <description>
    ///       Every revision date is valid, but at least one revision has no matching
    ///       <see cref="Revision"/> in the database (date + description, case-sensitive).
    ///     </description>
    ///   </item>
    ///   <item>
    ///     <term>Yellow</term>
    ///     <description>
    ///       Every revision date is valid and every revision has a database counterpart, but
    ///       at least one is not yet recorded in the document's revision indicator history,
    ///       or the document's current revision indicator does not match the latest sheet
    ///       revision indicator.
    ///     </description>
    ///   </item>
    ///   <item>
    ///     <term>Green</term>
    ///     <description>
    ///       Every revision on the sheet is valid, exists in the database, is recorded in the
    ///       document's revision indicator history, and the document's current revision indicator
    ///       matches the latest sheet revision indicator.
    ///     </description>
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
        /// Grey rows (invalid revision date) cannot be selected — setting this property
        /// has no effect when <see cref="HasInvalidRevisionDate"/> is <c>true</c>.
        /// </summary>
        [ObservableProperty]
        private bool _isSelected;

        /// <summary>Gets the Revit sheet number as read from the model.</summary>
        [ObservableProperty]
        private string _sheetNumber = string.Empty;

        /// <summary>Gets the Revit sheet name as read from the model.</summary>
        [ObservableProperty]
        private string _sheetName = string.Empty;

        /// <summary>
        /// Gets the built document number derived from the sheet number builder rules.
        /// Falls back to the raw sheet number when no builder rule is configured.
        /// </summary>
        [ObservableProperty]
        private string _documentNumber = string.Empty;

        /// <summary>
        /// Gets the built document name derived from the sheet name builder rules.
        /// Falls back to the raw sheet name when no builder rule is configured.
        /// </summary>
        [ObservableProperty]
        private string _documentName = string.Empty;

        /// <summary>
        /// Gets the revision indicator of the most recent revision on the sheet in Revit,
        /// or an empty string when the sheet carries no revisions.
        /// </summary>
        [ObservableProperty]
        private string _currentRevitRevision = string.Empty;

        /// <summary>
        /// Gets the current revision indicator stored on the database document.
        /// </summary>
        [ObservableProperty]
        private string _currentDatabaseRevision = string.Empty;

        /// <summary>
        /// Gets whether at least one revision on the sheet has an unparseable date string.
        /// Grey status — takes precedence over all other status values.
        /// When <c>true</c> the row cannot be selected for database update.
        /// </summary>
        [ObservableProperty]
        private bool _hasInvalidRevisionDate;

        /// <summary>
        /// Gets whether at least one revision on the sheet has no matching database revision
        /// (date + description, case-sensitive). Red status — only evaluated when
        /// <see cref="HasInvalidRevisionDate"/> is <c>false</c>.
        /// </summary>
        [ObservableProperty]
        private bool _hasUnknownRevisions;

        /// <summary>
        /// Gets whether every revision on the sheet exists in the database but at least one
        /// is not recorded in the document's revision indicator history, or the current
        /// revision indicator on the document does not match the latest sheet revision indicator.
        /// Yellow status — only evaluated when both <see cref="HasInvalidRevisionDate"/> and
        /// <see cref="HasUnknownRevisions"/> are <c>false</c>.
        /// </summary>
        [ObservableProperty]
        private bool _hasUnrecordedRevisions;

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

        /// <summary>
        /// Gets a human-readable status description shown in the DataGrid status column and tooltip.
        /// </summary>
        public string StatusMessage
        {
            get
            {
                if (HasInvalidRevisionDate)
                    return "Revision(s) with invalid date";
                if (HasUnknownRevisions)
                    return "One or more revisions on this sheet do not exist in the database";
                if (HasUnrecordedRevisions)
                    return "All revisions exist in the database but are not fully applied to this document";
                return "Revision history up to date";
            }
        }

        /// <summary>
        /// Gets whether this row can be selected and updated.
        /// Grey rows (invalid revision date) are never selectable.
        /// </summary>
        public bool IsSelectable => !HasInvalidRevisionDate;

        /// <summary>
        /// Gets whether this row requires any database update (Yellow or Red, not Grey).
        /// Grey rows require the revision date to be corrected in Revit first.
        /// </summary>
        public bool NeedsUpdate => !HasInvalidRevisionDate && (HasUnknownRevisions || HasUnrecordedRevisions);

        #endregion Computed Properties

        #region Constructor

        /// <summary>
        /// Initializes a new <see cref="RevitSheetRevisionRowViewModel"/> from a matched sheet
        /// and its corresponding database document.
        /// </summary>
        /// <param name="sheet">The Revit sheet. Must not be null.</param>
        /// <param name="document">The matching database document. Must not be null.</param>
        /// <param name="databaseRevisions">
        /// All revisions currently in the database, used to match sheet revisions by date and
        /// description (case-sensitive). Must not be null.
        /// </param>
        /// <param name="onSelectionChanged">
        /// Optional callback invoked whenever <see cref="IsSelected"/> changes.
        /// Pass the parent panel's <c>UpdateCounts</c> so commands re-evaluate on every tick.
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

            // ── Populate display properties ───────────────────────────────────────────

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

            // ── Evaluate revision status ──────────────────────────────────────────────

            EvaluateStatus(sheet.RevisionsOnSheet, document, databaseRevisions);
        }

        #endregion Constructor

        #region Private Helpers

        /// <summary>
        /// Evaluates <see cref="HasInvalidRevisionDate"/>, <see cref="HasUnknownRevisions"/>,
        /// and <see cref="HasUnrecordedRevisions"/>.
        /// <para>
        /// If any revision on the sheet has an invalid date (<see cref="RevitRevision.IsDateValid"/>
        /// is <c>false</c>), sets <see cref="HasInvalidRevisionDate"/> to <c>true</c> and returns
        /// immediately — no red/yellow evaluation is performed for grey rows.
        /// </para>
        /// </summary>
        /// <param name="revisionsOnSheet">Revisions applied to the sheet in Revit.</param>
        /// <param name="document">The matched database document.</param>
        /// <param name="databaseRevisions">All revisions in the database.</param>
        private void EvaluateStatus(
            IEnumerable<RevitRevisionOnSheet> revisionsOnSheet,
            Document document,
            IEnumerable<Revision> databaseRevisions)
        {
            var sheetRevisionList = revisionsOnSheet.ToList();

            // ── Grey check: invalid date takes full precedence ────────────────────────
            bool invalidDateFound = sheetRevisionList.Any(r => !r.RevitRevision.IsDateValid);
            if (invalidDateFound)
            {
                HasInvalidRevisionDate = true;
                HasUnknownRevisions = false;
                HasUnrecordedRevisions = false;
                return;
            }

            HasInvalidRevisionDate = false;

            // ── Red / Yellow checks ───────────────────────────────────────────────────
            var dbRevisionList = databaseRevisions.ToList();
            bool unknownFound = false;
            bool unrecordedFound = false;

            foreach (var revOnSheet in sheetRevisionList)
            {
                // Match by date and description — case-sensitive as specified.
                // IsDateValid is confirmed true for all entries at this point.
                var matchedDbRevision = dbRevisionList.FirstOrDefault(dbRev =>
                    dbRev.RevisionDate.ToString("yyyy-MM-dd") == revOnSheet.RevitRevision.RevisionDate &&
                    dbRev.Description == revOnSheet.RevitRevision.RevisionDescription);

                if (matchedDbRevision == null)
                {
                    // Revision does not exist in the database at all — Red.
                    unknownFound = true;
                    continue;
                }

                // Revision exists in the database — check whether it is recorded on this document.
                if (!document.HasRevisionIndicator(matchedDbRevision.Id))
                {
                    unrecordedFound = true;
                }
            }

            // Also flag yellow if the document's current revision indicator does not match
            // the latest revision indicator on the sheet (and we haven't already gone red).
            if (!unknownFound && sheetRevisionList.Count > 0)
            {
                var lastRevOnSheet = sheetRevisionList[sheetRevisionList.Count - 1];
                if (document.Revision != lastRevOnSheet.RevisionIndicator)
                {
                    unrecordedFound = true;
                }
            }

            HasUnknownRevisions = unknownFound;
            // Yellow only applies when there are no unknown (red) revisions.
            HasUnrecordedRevisions = !unknownFound && unrecordedFound;
        }

        #endregion Private Helpers

        #region Property Change Handlers

        partial void OnIsSelectedChanged(bool value)
        {
            // Grey rows must never be selected — guard defensively against programmatic sets.
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

        #endregion Property Change Handlers

        #region Re-evaluation

        /// <summary>
        /// Re-evaluates the revision status of this row using a refreshed set of database
        /// revisions and the updated document. Called by the panel after a database reload.
        /// </summary>
        /// <param name="sheet">The original Revit sheet (revision-on-sheet data does not change at runtime).</param>
        /// <param name="document">The refreshed database document. Must not be null.</param>
        /// <param name="databaseRevisions">Refreshed database revisions. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="sheet"/>, <paramref name="document"/>, or
        /// <paramref name="databaseRevisions"/> is null.
        /// </exception>
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
