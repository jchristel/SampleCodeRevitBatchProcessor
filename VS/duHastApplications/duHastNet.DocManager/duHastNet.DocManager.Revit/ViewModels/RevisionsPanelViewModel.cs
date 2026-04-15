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
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Revit.Models.Database;
using duHastNet.DocManager.Revit.Models.Revit;
using duHastNet.DocManager.Revit.Utilities.RevitData;
using duHastNet.Utils.WPF.Stores;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// ViewModel for the Revisions panel.
    /// <para>
    /// Displays all Revit sheets that have a matching document in the database, showing their
    /// revision synchronisation status. The user can select sheets and click "Update" to push
    /// their Revit revision history into the database.
    /// </para>
    /// <para>
    /// Status colour rules — precedence: Grey > Red > Yellow > Green:
    /// </para>
    /// <list type="bullet">
    ///   <item>
    ///     <term>Grey</term>
    ///     <description>
    ///       At least one revision on the sheet has an unparseable date string. The row
    ///       cannot be selected. The revision date must be corrected in Revit first.
    ///     </description>
    ///   </item>
    ///   <item>
    ///     <term>Red</term>
    ///     <description>
    ///       Every revision date is valid but at least one revision has no matching
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
    ///     <description>All revisions are valid, exist in the database, and are fully applied.</description>
    ///   </item>
    /// </list>
    /// <para>
    /// The Update workflow (synchronous, using <c>GetUnitOfWorkSync()</c>):
    /// 1. Any revision on a selected sheet with no database counterpart is created first.
    /// 2. For each selected document, <see cref="Document.Revision"/> and
    ///    <see cref="Document.RevisionId"/> are updated to reflect the latest sheet revision,
    ///    and <see cref="Document.RevisionIndicatorHistory"/> is populated for all revisions.
    /// 3. Bidirectional: <see cref="Revision.DocumentIds"/> updated for every affected revision.
    /// 4. <see cref="RefreshRequested"/> is raised so <see cref="RevitIntegrationViewModel"/>
    ///    reloads the database collections in place.
    /// </para>
    /// </summary>
    public partial class RevisionsPanelViewModel : AppViewModelBase
    {
        #region Private Fields

        private readonly RevitDataModel _revitDataModel;
        private readonly DatabaseDataModel _databaseDataModel;
        private readonly MessageStore _messageStore;

        // Lookup from built document number → RevitSheet, built once and reused on refresh.
        private readonly Dictionary<string, RevitSheet> _sheetByDocumentNumber;

        #endregion Private Fields

        #region Constructor

        /// <summary>
        /// Initializes a new instance of <see cref="RevisionsPanelViewModel"/>.
        /// </summary>
        /// <param name="revitDataModel">Revit data collected before the window opened. Must not be null.</param>
        /// <param name="databaseDataModel">Shared database data model whose collections are observed directly. Must not be null.</param>
        /// <param name="messageStore">Message store for surfacing errors and status to the UI banner. Must not be null.</param>
        /// <exception cref="ArgumentNullException">Thrown when any parameter is null.</exception>
        public RevisionsPanelViewModel(
            RevitDataModel revitDataModel,
            DatabaseDataModel databaseDataModel,
            MessageStore messageStore)
        {
            _revitDataModel = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));
            _databaseDataModel = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));

            _displayedSheets = new ObservableCollection<RevitSheetRevisionRowViewModel>();

            // Build lookup once — Revit sheet data never changes while the window is open.
            _sheetByDocumentNumber = BuildSheetLookup();

            // Re-evaluate command states whenever the database connection state changes.
            _databaseDataModel.PropertyChanged += OnDatabaseDataModelPropertyChanged;

            BuildSheetRows();
        }

        #endregion Constructor

        #region Events

        /// <summary>
        /// Raised after a successful database write to signal <see cref="RevitIntegrationViewModel"/>
        /// to reload the database collections.
        /// </summary>
        public event EventHandler? RefreshRequested;

        /// <summary>Raises <see cref="RefreshRequested"/>.</summary>
        protected void OnRefreshRequested()
        {
            RefreshRequested?.Invoke(this, EventArgs.Empty);
        }

        #endregion Events

        #region Observable Properties

        /// <summary>
        /// All matched sheet rows, filtered to sheets that have a database document counterpart.
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<RevitSheetRevisionRowViewModel> _displayedSheets;

        /// <summary>
        /// Gets or sets whether the panel is busy performing a database write.
        /// All commands are disabled while this is <c>true</c>.
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(UpdateCommand))]
        [NotifyCanExecuteChangedFor(nameof(SelectAllCommand))]
        [NotifyCanExecuteChangedFor(nameof(SelectNoneCommand))]
        private bool _isBusy;

        #endregion Observable Properties

        #region Derived Properties

        /// <summary>Gets the total number of matched sheet rows.</summary>
        public int TotalCount => DisplayedSheets?.Count ?? 0;

        /// <summary>Gets the number of rows with Red status (revision missing from database).</summary>
        public int MissingRevisionCount => DisplayedSheets?.Count(r => r.HasUnknownRevisions) ?? 0;

        /// <summary>Gets the number of rows with Yellow status (revision exists but not applied).</summary>
        public int UnrecordedRevisionCount => DisplayedSheets?.Count(r => r.HasUnrecordedRevisions) ?? 0;

        /// <summary>Gets the number of rows currently selected by the user.</summary>
        public int SelectedCount => DisplayedSheets?.Count(r => r.IsSelected) ?? 0;

        /// <summary>
        /// Gets whether the database is currently connected.
        /// Exposed on this ViewModel so the panel view can bind directly without
        /// reaching up to <see cref="RevitIntegrationViewModel"/>.
        /// </summary>
        public bool IsDatabaseConnected => _databaseDataModel.IsConnected;

        /// <summary>
        /// Gets the hint text shown in the execute bar.
        /// Displays a disconnected warning when the database is not connected.
        /// </summary>
        public string HintText => _databaseDataModel.IsConnected
            ? $"{TotalCount} matched sheets | {MissingRevisionCount} missing revisions | {UnrecordedRevisionCount} unrecorded | {SelectedCount} selected"
            : "Database not connected — all operations disabled";

        #endregion Derived Properties

        #region Commands

        /// <summary>
        /// Selects all displayed sheet rows that are selectable (not grey).
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanSelectAll))]
        private void SelectAll()
        {
            foreach (var row in DisplayedSheets)
                row.IsSelected = true;
        }

        private bool CanSelectAll()
        {
            if (!_databaseDataModel.IsConnected) return false;
            if (IsBusy) return false;
            return DisplayedSheets != null && DisplayedSheets.Any(r => r.IsSelectable);
        }

        /// <summary>
        /// Deselects all displayed sheet rows.
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanSelectNone))]
        private void SelectNone()
        {
            foreach (var row in DisplayedSheets)
                row.IsSelected = false;
        }

        private bool CanSelectNone()
        {
            if (!_databaseDataModel.IsConnected) return false;
            if (IsBusy) return false;
            return DisplayedSheets != null && DisplayedSheets.Any(r => r.IsSelected);
        }

        /// <summary>
        /// Pushes revision history from the selected sheets into the database.
        /// Uses the synchronous unit of work (<c>GetUnitOfWorkSync()</c>) consistent with
        /// the rest of the Revit integration layer.
        /// <para>
        /// Step 1: Creates any missing <see cref="Revision"/> records for revisions present
        /// on selected sheets but absent from the database.
        /// </para>
        /// <para>
        /// Step 2: Updates each selected document — sets <see cref="Document.Revision"/> to
        /// the latest revision indicator, <see cref="Document.RevisionId"/> to the latest
        /// revision's database ID, and populates <see cref="Document.RevisionIndicatorHistory"/>
        /// for all revisions on the sheet.
        /// </para>
        /// <para>
        /// Step 3: Maintains bidirectional consistency — adds the document ID to each affected
        /// <see cref="Revision.DocumentIds"/> collection and removes from any previous revision
        /// that is being superseded as the current revision.
        /// </para>
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanUpdate))]
        private void Update()
        {
            if (!CanUpdate()) return;

            IsBusy = true;

            try
            {
                var unitOfWork = _databaseDataModel.Api.GetUnitOfWorkSync();
                var selectedRows = DisplayedSheets.Where(r => r.IsSelected).ToList();

                // ── Step 1: Create missing revisions ──────────────────────────────────

                // Collect all distinct Revit revisions across selected sheets that have no
                // database counterpart (matched by date + description, case-sensitive).
                var dbRevisions = unitOfWork.Revisions.GetAll();
                var revisionsToCreate = new List<(string Date, string Description)>();

                foreach (var row in selectedRows)
                {
                    if (!_sheetByDocumentNumber.TryGetValue(row.DocumentNumber, out var sheet))
                        continue;

                    foreach (var revOnSheet in sheet.RevisionsOnSheet)
                    {
                        // ParsedDate is guaranteed non-null for all selected rows —
                        // grey rows (IsDateValid == false) are never selectable.
                        // Compare DateTime.Date directly against the database DateTime.Date —
                        // no string formatting, locale-format safe.
                        DateTime revitDate = revOnSheet.RevitRevision.ParsedDate!.Value.Date;

                        bool existsInDb = dbRevisions.Any(dbRev =>
                            dbRev.RevisionDate.Date == revitDate &&
                            dbRev.Description == revOnSheet.RevitRevision.RevisionDescription);

                        if (!existsInDb)
                        {
                            var key = (revOnSheet.RevitRevision.RevisionDate, revOnSheet.RevitRevision.RevisionDescription);
                            if (!revisionsToCreate.Contains(key))
                                revisionsToCreate.Add(key);
                        }
                    }
                }

                // revisionsToCreate holds the raw RevisionDate strings — look up the
                // ParsedDate from the sheet revision to create the Revision with a proper DateTime.
                // Build a lookup from raw date string + description to ParsedDate for efficiency.
                var parsedDateLookup = new Dictionary<(string, string), DateTime>();
                foreach (var row in selectedRows)
                {
                    if (!_sheetByDocumentNumber.TryGetValue(row.DocumentNumber, out var lookupSheet))
                        continue;
                    foreach (var revOnSheet in lookupSheet.RevisionsOnSheet)
                    {
                        var lookupKey = (revOnSheet.RevitRevision.RevisionDate, revOnSheet.RevitRevision.RevisionDescription);
                        if (!parsedDateLookup.ContainsKey(lookupKey) && revOnSheet.RevitRevision.ParsedDate.HasValue)
                            parsedDateLookup[lookupKey] = revOnSheet.RevitRevision.ParsedDate.Value.Date;
                    }
                }

                foreach (var (dateStr, description) in revisionsToCreate)
                {
                    var lookupKey = (dateStr, description);
                    if (!parsedDateLookup.TryGetValue(lookupKey, out DateTime revDate))
                    {
                        _messageStore.EnqueueMessage(
                            $"Could not retrieve parsed date for revision '{description}' ({dateStr}) — skipped.",
                            MessageTypes.Warning,
                            dismissAfterSeconds: 10);
                        continue;
                    }

                    var newRevision = new Revision(revDate, description);
                    unitOfWork.Revisions.Insert(newRevision);

                    _messageStore.EnqueueMessage(
                        $"Created database revision: {description} ({dateStr})",
                        MessageTypes.Information,
                        dismissAfterSeconds: 5);
                }

                // Reload revisions after creation so the new IDs are available for Step 2.
                var refreshedRevisions = unitOfWork.Revisions.GetAll();

                // ── Steps 2 & 3: Update documents ─────────────────────────────────────

                var updateErrors = new List<string>();
                int documentsUpdated = 0;

                foreach (var row in selectedRows)
                {
                    if (!_sheetByDocumentNumber.TryGetValue(row.DocumentNumber, out var sheet))
                    {
                        updateErrors.Add($"Sheet '{row.DocumentNumber}' not found in Revit data — skipped.");
                        continue;
                    }

                    // Load the document from the sync repository.
                    var dbDocuments = unitOfWork.Documents.GetDocumentsByNumber(row.DocumentNumber);
                    var document = dbDocuments.FirstOrDefault();

                    if (document == null)
                    {
                        updateErrors.Add($"Document '{row.DocumentNumber}' not found in database — skipped.");
                        continue;
                    }

                    int previousRevisionId = document.RevisionId;
                    bool documentChanged = false;
                    Revision? latestDbRevision = null;

                    // Process every revision on the sheet in order.
                    foreach (var revOnSheet in sheet.RevisionsOnSheet)
                    {
                        // ParsedDate is guaranteed non-null — grey rows never reach Update().
                        DateTime revitDate = revOnSheet.RevitRevision.ParsedDate!.Value.Date;

                        var matchedDbRevision = refreshedRevisions.FirstOrDefault(dbRev =>
                            dbRev.RevisionDate.Date == revitDate &&
                            dbRev.Description == revOnSheet.RevitRevision.RevisionDescription);

                        if (matchedDbRevision == null)
                        {
                            // Should not happen after Step 1, but guard defensively.
                            updateErrors.Add(
                                $"Revision '{revOnSheet.RevitRevision.RevisionDescription}' ({revOnSheet.RevitRevision.RevisionDate}) " +
                                $"still not found in database after creation — skipped for '{row.DocumentNumber}'.");
                            continue;
                        }

                        // Record the revision indicator in the document's history if absent.
                        if (!document.HasRevisionIndicator(matchedDbRevision.Id))
                        {
                            document.SetRevisionIndicator(matchedDbRevision.Id, revOnSheet.RevisionIndicator);
                            documentChanged = true;

                            // Bidirectional: add this document to the revision's document list.
                            unitOfWork.Revisions.AddDocumentToRevision(matchedDbRevision.Id, document.Id);
                        }

                        latestDbRevision = matchedDbRevision;
                    }

                    // Update the document's current revision to the latest sheet revision.
                    if (latestDbRevision != null)
                    {
                        var lastRevOnSheet = sheet.RevisionsOnSheet.LastOrDefault();
                        string latestIndicator = lastRevOnSheet?.RevisionIndicator ?? string.Empty;

                        if (document.Revision != latestIndicator || document.RevisionId != latestDbRevision.Id)
                        {
                            document.Revision = latestIndicator;
                            document.RevisionId = latestDbRevision.Id;
                            documentChanged = true;

                            // Bidirectional: remove document from old revision if superseded.
                            if (previousRevisionId != 0 && previousRevisionId != latestDbRevision.Id)
                            {
                                unitOfWork.Revisions.RemoveDocumentFromRevision(previousRevisionId, document.Id);
                            }

                            // Ensure the document is listed under its new current revision.
                            unitOfWork.Revisions.AddDocumentToRevision(latestDbRevision.Id, document.Id);
                        }
                    }

                    if (documentChanged)
                    {
                        unitOfWork.Documents.Update(document);
                        documentsUpdated++;
                    }
                }

                // ── Report results ────────────────────────────────────────────────────

                foreach (var error in updateErrors)
                {
                    _messageStore.EnqueueMessage(error, MessageTypes.Warning, dismissAfterSeconds: 20);
                }

                if (documentsUpdated > 0)
                {
                    _messageStore.EnqueueMessage(
                        $"Updated revision history for {documentsUpdated} document(s).",
                        MessageTypes.Information,
                        dismissAfterSeconds: 5);
                }

                OnRefreshRequested();
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Update failed: {ex.Message}",
                    MessageTypes.Error);
            }
            finally
            {
                IsBusy = false;
            }
        }

        private bool CanUpdate()
        {
            if (!_databaseDataModel.IsConnected) return false;
            if (IsBusy) return false;
            return DisplayedSheets != null && DisplayedSheets.Any(r => r.IsSelected && r.NeedsUpdate);
        }

        #endregion Commands

        #region Public Methods

        /// <summary>
        /// Called by <see cref="RevitIntegrationViewModel"/> after every
        /// <see cref="DatabaseDataModel.Reload"/> to re-evaluate each row's revision status
        /// against the refreshed database collections. Resets all selections.
        /// </summary>
        public void OnDatabaseRefreshed()
        {
            var dbRevisions = _databaseDataModel.Revisions.ToList();

            foreach (var row in DisplayedSheets)
            {
                if (!_sheetByDocumentNumber.TryGetValue(row.DocumentNumber, out var sheet))
                    continue;

                var dbDocument = _databaseDataModel.Documents
                    .FirstOrDefault(d => string.Equals(d.Number, row.DocumentNumber, StringComparison.Ordinal));

                if (dbDocument == null)
                    continue;

                row.IsSelected = false;
                row.Refresh(sheet, dbDocument, dbRevisions);
            }

            UpdateCounts();
        }

        #endregion Public Methods

        #region Private Helpers

        /// <summary>
        /// Builds the sheet lookup dictionary from built document number to <see cref="RevitSheet"/>.
        /// Sheets with an empty built document number are excluded.
        /// </summary>
        private Dictionary<string, RevitSheet> BuildSheetLookup()
        {
            var lookup = new Dictionary<string, RevitSheet>(StringComparer.Ordinal);

            foreach (var sheet in _revitDataModel.GetSheets())
            {
                sheet.BuiltDocumentProperties.TryGetValue(
                    duHastNet.UI.DocManagerSettingsUI.Utils.Constants.DocumentPropertyKeyDocumentNumber,
                    out string? docNumber);

                if (string.IsNullOrWhiteSpace(docNumber))
                    continue;

                // In the unlikely event of a duplicate built number, keep the first.
                if (!lookup.ContainsKey(docNumber))
                    lookup[docNumber] = sheet;
            }

            return lookup;
        }

        /// <summary>
        /// Builds <see cref="DisplayedSheets"/> from scratch.
        /// Only sheets whose built document number matches a document in the database are shown.
        /// </summary>
        private void BuildSheetRows()
        {
            DisplayedSheets.Clear();

            var dbDocumentsByNumber = _databaseDataModel.Documents
                .ToDictionary(d => d.Number, d => d, StringComparer.Ordinal);

            var dbRevisions = _databaseDataModel.Revisions.ToList();

            foreach (var (docNumber, sheet) in _sheetByDocumentNumber)
            {
                if (!dbDocumentsByNumber.TryGetValue(docNumber, out var dbDocument))
                    continue;

                var row = new RevitSheetRevisionRowViewModel(
                    sheet,
                    dbDocument,
                    dbRevisions,
                    onSelectionChanged: UpdateCounts);

                DisplayedSheets.Add(row);
            }

            UpdateCounts();
        }

        /// <summary>
        /// Refreshes all count-derived properties and notifies commands to re-evaluate
        /// their CanExecute state. Registered as the per-row <c>onSelectionChanged</c> callback
        /// so every manual checkbox tick triggers an immediate re-evaluation.
        /// </summary>
        private void UpdateCounts()
        {
            OnPropertyChanged(nameof(TotalCount));
            OnPropertyChanged(nameof(MissingRevisionCount));
            OnPropertyChanged(nameof(UnrecordedRevisionCount));
            OnPropertyChanged(nameof(SelectedCount));
            OnPropertyChanged(nameof(HintText));
            OnPropertyChanged(nameof(IsDatabaseConnected));
            UpdateCommand.NotifyCanExecuteChanged();
            SelectAllCommand.NotifyCanExecuteChanged();
            SelectNoneCommand.NotifyCanExecuteChanged();
        }

        #endregion Private Helpers

        #region Database Connection Change Handler

        private void OnDatabaseDataModelPropertyChanged(
            object? sender,
            System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(DatabaseDataModel.IsConnected))
            {
                UpdateCounts();
            }
        }

        #endregion Database Connection Change Handler

        #region Lifecycle

        /// <summary>
        /// Unsubscribes from <see cref="DatabaseDataModel.PropertyChanged"/> to prevent
        /// memory leaks when the window is closing.
        /// </summary>
        public override void OnClosing()
        {
            _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
            base.OnClosing();
        }

        /// <summary>
        /// Unsubscribes from <see cref="DatabaseDataModel.PropertyChanged"/> on disposal.
        /// </summary>
        public override void Dispose()
        {
            _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
            base.Dispose();
        }

        #endregion Lifecycle
    }
}
