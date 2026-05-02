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
using CsvHelper;
using CsvHelper.Configuration;
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Transmittal;

public partial class TransmittalViewModel : AppViewModelBase, IActivatable
{
    #region Constants

    private const string KeyDocumentNumber = "DocumentNumber";
    private const string KeyDocumentName = "DocumentName";
    private const string KeyCurrentRevision = "CurrentRevision";
    private const string KeyIsInactive = "IsInactive";
    private const string KeyIsHistoryRow = "IsHistoryRow";
    private const string KeyNumberActiveFrom = "NumberActiveFrom";
    private const string KeyNumberActiveTo = "NumberActiveTo";
    private const string KeyHistoryDateRangeLabel = "HistoryDateRangeLabel";

    #endregion

    #region Private Fields

    private readonly NavigationStore _navigationStore;
    private readonly Func<Merge.MergeViewModel> _createMergeViewModel;
    private readonly IDocManagerApi _docManagerApi;
    private readonly IDialogService _dialogService;

    /// <summary>
    /// Internal list of revision row view models — used to track IsChecked state and
    /// to provide RevisionId / date for column rebuilds.
    /// Not bound directly to the grid; RevisionRows is the grid source.
    /// </summary>
    private readonly List<TransmittalRevisionRowViewModel> _revisionViewModels = new();

    /// <summary>
    /// All documents loaded from the database — kept in memory so rows can be
    /// rebuilt without hitting the database again when filters change.
    /// Populated once per activation.
    /// </summary>
    private List<Document> _allDocuments = new();

    /// <summary>
    /// All revisions loaded from the database — kept in memory to pre-load
    /// revision indicator keys into every document row.
    /// Populated once per activation alongside _allDocuments.
    /// </summary>
    private List<Revision> _allRevisions = new();

    /// <summary>
    /// Lookup from RevisionId to RevisionDate — used by the document history
    /// inference algorithm to assign revisions to historical document numbers.
    /// </summary>
    private Dictionary<int, DateTime> _revisionDateLookup = new();

    #endregion

    #region Public Properties

    public GlobalMessageViewModel GlobalMessageViewModel { get; }

    // ── Revisions grid ───────────────────────────────────────────────────────

    /// <summary>Revision rows bound to the revisions DynamicDataGrid ItemsSource.</summary>
    public ObservableCollection<DynamicRowData> RevisionRows { get; } = new();

    /// <summary>Column definitions bound to the revisions DynamicDataGrid ColumnDefinitions.</summary>
    public ObservableCollection<DynamicColumnDefinition> RevisionColumnDefinitions { get; } = new();

    // ── Documents grid ───────────────────────────────────────────────────────

    /// <summary>Document rows bound to the documents DynamicDataGrid ItemsSource.</summary>
    public ObservableCollection<DynamicRowData> DocumentRows { get; } = new();

    /// <summary>Column definitions bound to the documents DynamicDataGrid ColumnDefinitions.</summary>
    public ObservableCollection<DynamicColumnDefinition> DocumentColumnDefinitions { get; } = new();

    #endregion

    #region Observable Properties

    [ObservableProperty]
    private string _revisionsStatusMessage = string.Empty;

    [ObservableProperty]
    private string _documentsStatusMessage = string.Empty;

    [ObservableProperty]
    private string _exportStatusMessage = string.Empty;

    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private DocumentDisplayMode _documentDisplayMode = DocumentDisplayMode.All;

    [ObservableProperty]
    private bool _showInactiveDocuments = false;

    [ObservableProperty]
    private bool _includeDocumentHistory = false;

    /// <summary>
    /// True when DocumentDisplayMode is All. Bound to the "Show All" RadioButton.
    /// </summary>
    public bool IsShowAllMode
    {
        get => DocumentDisplayMode == DocumentDisplayMode.All;
        set { if (value) DocumentDisplayMode = DocumentDisplayMode.All; }
    }

    /// <summary>
    /// True when DocumentDisplayMode is ByRevision. Bound to the "By Revisions Only" RadioButton.
    /// </summary>
    public bool IsByRevisionMode
    {
        get => DocumentDisplayMode == DocumentDisplayMode.ByRevision;
        set { if (value) DocumentDisplayMode = DocumentDisplayMode.ByRevision; }
    }

    #endregion

    #region Constructor

    /// <summary>
    /// Creates a new instance of TransmittalViewModel.
    /// </summary>
    /// <param name="navigationStore">Navigation store for view navigation.</param>
    /// <param name="messageStore">Message store for global messages.</param>
    /// <param name="createMergeViewModel">Factory function to create MergeViewModel for back navigation.</param>
    /// <param name="docManagerApi">API for database access.</param>
    /// <param name="dialogService">Dialog service for save file dialogs.</param>
    /// <exception cref="ArgumentNullException">Thrown when any required parameter is null.</exception>
    public TransmittalViewModel(
        NavigationStore navigationStore,
        IMessageStore messageStore,
        Func<Merge.MergeViewModel> createMergeViewModel,
        IDocManagerApi docManagerApi,
        IDialogService dialogService)
    {
        ArgumentNullException.ThrowIfNull(navigationStore);
        ArgumentNullException.ThrowIfNull(messageStore);
        ArgumentNullException.ThrowIfNull(createMergeViewModel);
        ArgumentNullException.ThrowIfNull(docManagerApi);
        ArgumentNullException.ThrowIfNull(dialogService);

        _navigationStore = navigationStore;
        _createMergeViewModel = createMergeViewModel;
        _docManagerApi = docManagerApi;
        _dialogService = dialogService;

        GlobalMessageViewModel = new GlobalMessageViewModel(messageStore);
        RegisterChild(GlobalMessageViewModel);

        BuildRevisionColumnDefinitions();
        BuildDocumentColumnDefinitions();
    }

    #endregion

    #region Property Change Handlers

    /// <summary>
    /// Called when DocumentDisplayMode changes. Notifies the two helper bool
    /// properties and rebuilds document rows to apply the new filter.
    /// </summary>
    partial void OnDocumentDisplayModeChanged(DocumentDisplayMode value)
    {
        OnPropertyChanged(nameof(IsShowAllMode));
        OnPropertyChanged(nameof(IsByRevisionMode));
        RebuildDocumentRows();
        RebuildDocumentColumns();
    }

    partial void OnShowInactiveDocumentsChanged(bool value)
    {
        RebuildDocumentRows();
    }

    partial void OnIncludeDocumentHistoryChanged(bool value)
    {
        RebuildDocumentRows();
    }

    #endregion

    #region IActivatable

    /// <summary>
    /// Called when the view is navigated to. Loads all data from the database.
    /// </summary>
    public async Task OnActivatedAsync()
    {
        IsBusy = true;
        try
        {
            await LoadRevisionsAsync();
            await LoadDocumentsAsync();
        }
        finally
        {
            IsBusy = false;
        }
    }

    #endregion

    #region Revisions — Load and Column Build

    /// <summary>
    /// Builds the static column definitions for the revisions DynamicDataGrid.
    /// Called once in the constructor.
    /// </summary>
    private void BuildRevisionColumnDefinitions()
    {
        RevisionColumnDefinitions.Clear();

        RevisionColumnDefinitions.Add(new DynamicColumnDefinition(
            propertyName: nameof(TransmittalRevisionRowViewModel.IsChecked),
            displayName: string.Empty,
            dataType: typeof(bool))
        {
            Width = 44,
            IsReadOnly = false
        });

        RevisionColumnDefinitions.Add(new DynamicColumnDefinition(
            propertyName: nameof(TransmittalRevisionRowViewModel.RevisionDate),
            displayName: "Date",
            dataType: typeof(DateTime))
        {
            Width = 110,
            IsReadOnly = true
        });

        RevisionColumnDefinitions.Add(new DynamicColumnDefinition(
            propertyName: nameof(TransmittalRevisionRowViewModel.RevisionDescription),
            displayName: "Description",
            dataType: typeof(string))
        {
            Width = 400,
            IsReadOnly = true
        });
    }

    /// <summary>
    /// Loads all revisions from the database and populates RevisionRows.
    /// </summary>
    private async Task LoadRevisionsAsync()
    {
        RevisionRows.Clear();
        _revisionViewModels.Clear();
        RevisionsStatusMessage = string.Empty;

        if (!_docManagerApi.IsDatabaseReady())
        {
            RevisionsStatusMessage = "No database connected.";
            return;
        }

        try
        {
            var revisions = await _docManagerApi.GetAllRevisionsAsync();

            var sorted = revisions
                .OrderByDescending(r => r.RevisionDate)
                .ThenByDescending(r => r.Id)
                .ToList();

            _allRevisions = sorted;
            _revisionDateLookup = sorted.ToDictionary(r => r.Id, r => r.RevisionDate);

            if (sorted.Count == 0)
            {
                RevisionsStatusMessage = "No revisions in database.";
                return;
            }

            foreach (var revision in sorted)
            {
                var rowVm = new TransmittalRevisionRowViewModel(
                    revisionId: revision.Id,
                    revisionDate: revision.RevisionDate,
                    revisionDescription: revision.Description ?? string.Empty,
                    documentIds: revision.DocumentIds,
                    onCheckedChanged: OnRevisionCheckedChanged);

                _revisionViewModels.Add(rowVm);

                var row = new DynamicRowData();
                row[nameof(TransmittalRevisionRowViewModel.IsChecked)] = rowVm.IsChecked;
                row[nameof(TransmittalRevisionRowViewModel.RevisionDate)] = rowVm.RevisionDate;
                row[nameof(TransmittalRevisionRowViewModel.RevisionDescription)] = rowVm.RevisionDescription;

                // Keep row data in sync when IsChecked changes
                rowVm.PropertyChanged += (_, e) =>
                {
                    if (e.PropertyName == nameof(TransmittalRevisionRowViewModel.IsChecked))
                        row[nameof(TransmittalRevisionRowViewModel.IsChecked)] = rowVm.IsChecked;
                };

                RevisionRows.Add(row);
            }
        }
        catch (Exception ex)
        {
            RevisionsStatusMessage = $"Error loading revisions: {ex.Message}";
        }
    }

    /// <summary>
    /// Called by each TransmittalRevisionRowViewModel when its IsChecked property changes.
    /// Always rebuilds document columns. Also rebuilds rows when in ByRevision mode.
    /// </summary>
    private void OnRevisionCheckedChanged()
    {
        if (DocumentDisplayMode == DocumentDisplayMode.ByRevision)
            RebuildDocumentRows();

        RebuildDocumentColumns();
    }

    #endregion

    #region Documents — Load and Column Build

    /// <summary>
    /// Builds the static column definitions for the documents DynamicDataGrid.
    /// Called once in the constructor. Dynamic revision columns are managed
    /// by RebuildDocumentColumns() as the user checks/unchecks revisions.
    /// </summary>
    private void BuildDocumentColumnDefinitions()
    {
        DocumentColumnDefinitions.Clear();

        DocumentColumnDefinitions.Add(new DynamicColumnDefinition(
            propertyName: KeyDocumentNumber,
            displayName: "Doc Number",
            dataType: typeof(string))
        {
            Width = 160,
            IsReadOnly = true
        });

        DocumentColumnDefinitions.Add(new DynamicColumnDefinition(
            propertyName: KeyDocumentName,
            displayName: "Doc Name",
            dataType: typeof(string))
        {
            Width = 0,      // star-sized — DynamicDataGrid treats 0 as DataGridLength.Star
            IsReadOnly = true
        });

        DocumentColumnDefinitions.Add(new DynamicColumnDefinition(
            propertyName: KeyCurrentRevision,
            displayName: "Current Rev.",
            dataType: typeof(string))
        {
            Width = 90,
            IsReadOnly = true
        });
    }

    /// <summary>
    /// Rebuilds the dynamic revision columns on the documents grid.
    /// Preserves the three static columns and replaces all dynamic entries
    /// (PropertyName starting with "Rev_") with one column per checked revision.
    /// Called whenever a revision IsChecked state changes.
    /// </summary>
    private void RebuildDocumentColumns()
    {
        // Remove all existing dynamic columns — preserve only the 3 static ones
        var toRemove = DocumentColumnDefinitions
            .Where(c => c.PropertyName.StartsWith("Rev_", StringComparison.Ordinal))
            .ToList();

        foreach (var col in toRemove)
            DocumentColumnDefinitions.Remove(col);

        // Append one column per checked revision, ordered newest-first
        var checkedRevisions = _revisionViewModels
            .Where(r => r.IsChecked)
            .ToList();

        foreach (var revVm in checkedRevisions)
        {
            var header = $"{revVm.RevisionDate:d} — {revVm.RevisionDescription}";
            if (header.Length > 40)
                header = header[..40] + "…";

            DocumentColumnDefinitions.Add(new DynamicColumnDefinition(
                propertyName: $"Rev_{revVm.RevisionId}",
                displayName: header,
                dataType: typeof(string))
            {
                Width = 100,
                IsReadOnly = true
            });
        }
    }

    /// <summary>
    /// Loads all documents from the database into _allDocuments, then rebuilds DocumentRows.
    /// Called once on activation. Subsequent filter/mode changes only call RebuildDocumentRows().
    /// </summary>
    private async Task LoadDocumentsAsync()
    {
        DocumentRows.Clear();
        _allDocuments.Clear();
        DocumentsStatusMessage = string.Empty;

        if (!_docManagerApi.IsDatabaseReady())
        {
            DocumentsStatusMessage = "No database connected.";
            return;
        }

        try
        {
            var unitOfWork = _docManagerApi.GetUnitOfWork();
            if (unitOfWork == null)
            {
                DocumentsStatusMessage = "No database connected.";
                return;
            }

            _allDocuments = await unitOfWork.Documents.GetAllAsync();

            RebuildDocumentRows();
        }
        catch (Exception ex)
        {
            DocumentsStatusMessage = $"Error loading documents: {ex.Message}";
        }
    }

    /// <summary>
    /// Rebuilds DocumentRows from _allDocuments applying the current mode and filters.
    /// Called on initial load and whenever mode or filter options change.
    /// </summary>
    private void RebuildDocumentRows()
    {
        DocumentRows.Clear();
        DocumentsStatusMessage = string.Empty;

        if (_allDocuments.Count == 0)
        {
            DocumentsStatusMessage = "No documents in database.";
            return;
        }

        if (DocumentDisplayMode == DocumentDisplayMode.ByRevision)
        {
            RebuildDocumentRowsByRevision();
            return;
        }

        // Show All mode — apply inactive filter then order by number
        var documents = _allDocuments
            .Where(d => ShowInactiveDocuments || d.IsActive)
            .OrderBy(d => d.Number);

        foreach (var document in documents)
        {
            DocumentRows.Add(BuildDocumentRow(document));

            if (IncludeDocumentHistory)
            {
                foreach (var historyRow in BuildHistoryRows(document))
                    DocumentRows.Add(historyRow);
            }
        }
    }

    /// <summary>
    /// Handles RebuildDocumentRows for ByRevision mode.
    /// Shows only documents whose ID appears in at least one checked revision's DocumentIds.
    /// </summary>
    private void RebuildDocumentRowsByRevision()
    {
        var checkedRevisions = _revisionViewModels.Where(r => r.IsChecked).ToList();

        if (checkedRevisions.Count == 0)
        {
            if (_revisionViewModels.Count == 0)
                DocumentsStatusMessage = "No revisions available. Use 'Show All Documents' instead.";
            else
                DocumentsStatusMessage = "No revisions selected. Switch to 'Show All Documents' or select a revision above.";
            return;
        }

        // Collect all document IDs belonging to any checked revision
        var includedDocumentIds = checkedRevisions
            .SelectMany(r => r.DocumentIds)
            .ToHashSet();

        if (includedDocumentIds.Count == 0)
        {
            DocumentsStatusMessage = "The selected revision(s) have no documents assigned.";
            return;
        }

        var documents = _allDocuments
            .Where(d => includedDocumentIds.Contains(d.Id) && (ShowInactiveDocuments || d.IsActive))
            .OrderBy(d => d.Number)
            .ToList();

        if (documents.Count == 0)
        {
            DocumentsStatusMessage = "The selected revision(s) have no documents assigned.";
            return;
        }

        foreach (var document in documents)
        {
            DocumentRows.Add(BuildDocumentRow(document));

            if (IncludeDocumentHistory)
            {
                foreach (var historyRow in BuildHistoryRows(document))
                    DocumentRows.Add(historyRow);
            }
        }
    }

    /// <summary>
    /// Creates a DynamicRowData for a single document with all keys populated —
    /// static fields plus a Rev_{id} entry for every revision in the database.
    /// Pre-loading all revisions means column toggling never requires row rebuilds.
    /// </summary>
    private DynamicRowData BuildDocumentRow(Document document)
    {
        var row = new DynamicRowData();
        row[KeyDocumentNumber] = document.Number;
        row[KeyDocumentName] = document.Name;
        row[KeyCurrentRevision] = document.Revision;
        row[KeyIsInactive] = !document.IsActive;
        row[KeyIsHistoryRow] = false;

        foreach (var revision in _allRevisions)
        {
            var key = $"Rev_{revision.Id}";
            var indicator = document.GetRevisionIndicator(revision.Id) ?? string.Empty;
            row[key] = indicator;
        }

        return row;
    }

    /// <summary>
    /// Builds zero or more history rows for a document that has had document number changes.
    /// Uses the revision date inference algorithm to assign revision indicators to each
    /// historical number based on when the number was active.
    /// Returns an empty enumerable when the document has no history or history is empty.
    /// </summary>
    private IEnumerable<DynamicRowData> BuildHistoryRows(Document document)
    {
        var history = document.DocumentNumberHistory;
        if (history == null || history.Count == 0)
            yield break;

        // Step 1: order historical entries by change date ascending
        var orderedHistory = history
            .OrderBy(kvp => kvp.Value)
            .ThenBy(kvp => kvp.Key)   // stable fallback for same-date entries
            .ToList();

        // Step 2: reconstruct active date ranges
        // Each entry: (historicalNumber, activeFrom, activeTo)
        DateOnly? previousChangedDate = null;

        foreach (var (historicalNumber, changedToNewDate) in orderedHistory)
        {
            var activeFrom = previousChangedDate;   // null = beginning of time
            var activeTo = changedToNewDate;

            var row = BuildHistoryRow(
                document,
                historicalNumber,
                activeFrom,
                activeTo);

            previousChangedDate = changedToNewDate;
            yield return row;
        }
    }

    /// <summary>
    /// Builds a single history row for a document's historical number,
    /// populating only the revision indicators that were active during the given date range.
    /// </summary>
    private DynamicRowData BuildHistoryRow(
        Document document,
        string historicalNumber,
        DateOnly? activeFrom,
        DateOnly activeTo)
    {
        var row = new DynamicRowData();
        row[KeyDocumentNumber] = historicalNumber;
        row[KeyDocumentName] = document.Name;
        row[KeyCurrentRevision] = string.Empty;     // historical rows have no current revision
        row[KeyIsInactive] = true;                  // always shown grey — history is inherently inactive
        row[KeyIsHistoryRow] = true;
        row[KeyNumberActiveFrom] = activeFrom?.ToString("yyyy-MM-dd") ?? string.Empty;
        row[KeyNumberActiveTo] = activeTo.ToString("yyyy-MM-dd");
        row[KeyHistoryDateRangeLabel] = FormatDateRangeLabel(activeFrom, activeTo);

        // Step 3–5 of inference algorithm:
        // For each revision, check if its date falls within the active date range.
        // Only populate the indicator if the revision date falls within (activeFrom, activeTo].
        foreach (var revision in _allRevisions)
        {
            var key = $"Rev_{revision.Id}";
            var revisionDateOnly = DateOnly.FromDateTime(revision.RevisionDate);

            bool withinRange =
                (activeFrom == null || revisionDateOnly >= activeFrom) &&
                revisionDateOnly <= activeTo;

            if (withinRange)
            {
                var indicator = document.GetRevisionIndicator(revision.Id) ?? string.Empty;
                row[key] = indicator;
            }
            else
            {
                row[key] = string.Empty;
            }
        }

        return row;
    }

    /// <summary>
    /// Formats a human-readable date range label for a history row.
    /// </summary>
    private static string FormatDateRangeLabel(DateOnly? activeFrom, DateOnly activeTo)
    {
        return activeFrom.HasValue
            ? $"{activeFrom.Value:yyyy-MM-dd} – {activeTo:yyyy-MM-dd}"
            : $"until {activeTo:yyyy-MM-dd}";
    }

    #endregion

    #region Commands

    /// <summary>
    /// Navigates back to the Merge view.
    /// </summary>
    [RelayCommand]
    private void Close()
    {
        _navigationStore.NavigateTo(_createMergeViewModel);
    }

    /// <summary>
    /// Exports the documents grid to CSV — all rows currently shown,
    /// respecting active mode, filters, and history setting.
    /// </summary>
    [RelayCommand]
    private void ExportToCsv()
    {
        ExportStatusMessage = string.Empty;

        if (DocumentRows.Count == 0)
        {
            ExportStatusMessage = "Nothing to export — documents grid is empty.";
            return;
        }

        var filePath = _dialogService.ShowSaveFileDialog(
            title: "Export Documents to CSV",
            filter: "CSV files (*.csv)|*.csv",
            defaultExtension: ".csv");

        if (string.IsNullOrWhiteSpace(filePath))
            return;

        try
        {
            using var writer = new StreamWriter(filePath);
            using var csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true
            });

            // Write header — static columns first, then one per visible dynamic column
            csv.WriteField("Doc Number");
            csv.WriteField("Doc Name");
            csv.WriteField("Current Rev.");

            var dynamicColumns = DocumentColumnDefinitions
                .Where(c => c.PropertyName.StartsWith("Rev_", StringComparison.Ordinal))
                .ToList();

            foreach (var col in dynamicColumns)
                csv.WriteField(col.DisplayName);

            if (IncludeDocumentHistory)
            {
                csv.WriteField("History");
                csv.WriteField("Active From");
                csv.WriteField("Active To");
            }

            csv.NextRecord();

            // Write data rows
            foreach (var row in DocumentRows)
            {
                csv.WriteField(row[KeyDocumentNumber]?.ToString() ?? string.Empty);
                csv.WriteField(row[KeyDocumentName]?.ToString() ?? string.Empty);
                csv.WriteField(row[KeyCurrentRevision]?.ToString() ?? string.Empty);

                foreach (var col in dynamicColumns)
                    csv.WriteField(row[col.PropertyName]?.ToString() ?? string.Empty);

                if (IncludeDocumentHistory)
                {
                    var isHistory = row[KeyIsHistoryRow] is true;
                    csv.WriteField(isHistory ? "Yes" : string.Empty);
                    csv.WriteField(row[KeyNumberActiveFrom]?.ToString() ?? string.Empty);
                    csv.WriteField(row[KeyNumberActiveTo]?.ToString() ?? string.Empty);
                }

                csv.NextRecord();
            }

            ExportStatusMessage = $"Exported {DocumentRows.Count} row(s) successfully.";
        }
        catch (Exception ex)
        {
            ExportStatusMessage = $"Export failed: {ex.Message}";
        }
    }

    #endregion

    #region Lifecycle

    public override void OnClosing()
    {
        base.OnClosing();
    }

    public override void Dispose()
    {
        base.Dispose();
    }

    #endregion
}
