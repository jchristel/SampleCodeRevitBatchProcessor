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
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Revit.Models.Database;
using duHastNet.DocManager.Revit.Models.Revit;
using duHastNet.Utils.WPF.Stores;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// ViewModel for the Sheets panel.
    /// <para>
    /// Shows all Revit sheets in a single DataGrid. Colour coding communicates status:
    /// red = not in database, yellow = in database but name differs, green = up to date.
    /// The user selects any combination of red and yellow rows and clicks "Update" to process
    /// them in a single pass — red rows are imported, yellow rows have their names updated.
    /// </para>
    /// <para>
    /// When custom field definitions are present, importing red rows first opens
    /// <see cref="duHastNet.DocManager.Revit.Views.SheetCustomPropertiesWindow"/> as a modal
    /// dialog so the user can supply per-sheet custom property values before the write.
    /// Name updates (yellow rows) never require the custom properties window.
    /// </para>
    /// <para>
    /// After a successful write the panel raises <see cref="RefreshRequested"/> so
    /// <see cref="RevitIntegrationViewModel"/> reloads the database collections in place.
    /// The panel then re-evaluates every row's status from the refreshed data.
    /// </para>
    /// </summary>
    public partial class SheetsPanelViewModel : AppViewModelBase
    {
        #region Private Fields

        private readonly RevitDataModel _revitDataModel;
        private readonly DatabaseDataModel _databaseDataModel;
        private readonly MessageStore _messageStore;
        /// <summary>
        /// Active custom field definitions sourced from <see cref="DatabaseDataModel.CustomFieldDefinitions"/>.
        /// Loaded once before the window opens in <c>Main.LoadDatabaseData()</c>.
        /// Empty when the database has no active custom field definitions.
        /// </summary>
        private readonly IReadOnlyList<CustomFieldDefinition> _customFieldDefinitions;

        #endregion Private Fields

        #region Constructor

        /// <summary>
        /// Initializes a new instance of <see cref="SheetsPanelViewModel"/>.
        /// </summary>
        /// <param name="revitDataModel">Revit data collected before the window opened. Must not be null.</param>
        /// <param name="databaseDataModel">Shared database data model. Must not be null.</param>
        /// <param name="messageStore">Message store for surfacing status to the UI banner. Must not be null.</param>
        /// <exception cref="ArgumentNullException">Thrown when any parameter is null.</exception>
        public SheetsPanelViewModel(
            RevitDataModel revitDataModel,
            DatabaseDataModel databaseDataModel,
            MessageStore messageStore)
        {
            _revitDataModel = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));
            _databaseDataModel = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));

            _displayedSheets = new ObservableCollection<RevitSheetRowViewModel>();
            _customFieldDefinitions = _databaseDataModel.CustomFieldDefinitions;

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
        /// All Revit sheet rows, always showing the complete set regardless of status.
        /// Colour coding on each row communicates whether a sheet needs importing,
        /// updating, or is already up to date.
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<RevitSheetRowViewModel> _displayedSheets;

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

        /// <summary>Gets the total number of sheets from Revit.</summary>
        public int TotalCount => DisplayedSheets?.Count ?? 0;

        /// <summary>Gets the number of sheets not yet in the database (red rows).</summary>
        public int ToImportCount => DisplayedSheets?.Count(r => r.CanImport) ?? 0;

        /// <summary>Gets the number of sheets in the database whose name differs (yellow rows).</summary>
        public int ToUpdateCount => DisplayedSheets?.Count(r => r.CanUpdate) ?? 0;

        /// <summary>Gets the number of sheets currently selected by the user.</summary>
        public int SelectedCount => DisplayedSheets?.Count(r => r.IsSelected) ?? 0;

        /// <summary>
        /// Gets whether the database is currently connected.
        /// Exposed on this ViewModel so the panel view can bind to it directly.
        /// </summary>
        public bool IsDatabaseConnected => _databaseDataModel.IsConnected;

        /// <summary>
        /// Gets the hint text shown in the execute bar.
        /// Switches to a warning when the database is not connected.
        /// </summary>
        public string HintText => _databaseDataModel.IsConnected
            ? "Select sheets to import (red) or update (yellow), then click Update."
            : "No database connection. Cannot import or update any sheets.";

        #endregion Derived Properties

        #region Commands

        /// <summary>
        /// Selects all rows currently in the DataGrid.
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanSelectAll))]
        private void SelectAll()
        {
            foreach (var row in DisplayedSheets)
                row.IsSelected = true;

            UpdateCounts();
        }

        private bool CanSelectAll() => _databaseDataModel.IsConnected && !IsBusy && DisplayedSheets != null && DisplayedSheets.Any();

        /// <summary>
        /// Deselects all rows in the DataGrid.
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanSelectNone))]
        private void SelectNone()
        {
            foreach (var row in DisplayedSheets)
                row.IsSelected = false;

            UpdateCounts();
        }

        private bool CanSelectNone() => _databaseDataModel.IsConnected && !IsBusy && DisplayedSheets != null && DisplayedSheets.Any();

        /// <summary>
        /// Processes all selected rows in a single pass:
        /// selected red rows are imported, selected yellow rows have their names updated.
        /// If the database has custom field definitions, a modal window is shown before
        /// the import step so the user can enter per-sheet custom property values.
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanUpdate))]
        private void Update()
        {
            var selectedRows = DisplayedSheets.Where(r => r.IsSelected).ToList();
            if (!selectedRows.Any()) return;

            var rowsToImport = selectedRows.Where(r => r.CanImport).ToList();
            var rowsToUpdate = selectedRows.Where(r => r.CanUpdate).ToList();

            // ── Import step ──────────────────────────────────────────────────────
            if (rowsToImport.Any())
            {
                SheetCustomPropertiesViewModel? customPropertiesVm = null;

                if (_customFieldDefinitions.Any())
                {
                    customPropertiesVm = new SheetCustomPropertiesViewModel(
                        rowsToImport, _customFieldDefinitions);

                    var window = new duHastNet.DocManager.Revit.Views.SheetCustomPropertiesWindow(
                        customPropertiesVm);

                    window.Owner = System.Windows.Application.Current?.Windows
                        .OfType<System.Windows.Window>()
                        .FirstOrDefault(w => w.IsActive)
                        ?? System.Windows.Application.Current?.MainWindow;

                    bool? result = window.ShowDialog();

                    if (result != true || !customPropertiesVm.DialogConfirmed)
                    {
                        // User cancelled the custom properties window — abort entirely.
                        return;
                    }
                }

                CommitImport(rowsToImport, customPropertiesVm);
            }

            // ── Update step ───────────────────────────────────────────────────────
            if (rowsToUpdate.Any())
            {
                CommitNameUpdates(rowsToUpdate);
            }

            // Single refresh after all operations complete.
            OnRefreshRequested();
        }

        private bool CanUpdate()
        {
            if (!_databaseDataModel.IsConnected) return false;
            if (IsBusy) return false;
            if (DisplayedSheets == null) return false;
            return DisplayedSheets.Any(r => r.IsSelected && (r.CanImport || r.CanUpdate));
        }

        #endregion Commands

        #region Public Methods

        /// <summary>
        /// Called by <see cref="RevitIntegrationViewModel"/> after the database collections
        /// have been reloaded in place. Re-evaluates every row's database-status flags and
        /// resets selections.
        /// </summary>
        public void OnDatabaseRefreshed()
        {
            var documents = _databaseDataModel.Documents.ToList();
            foreach (var row in DisplayedSheets)
            {
                row.UpdateDatabaseStatus(documents);
                row.IsSelected = false;
            }
            UpdateCounts();
        }

        #endregion Public Methods

        #region Private Methods — Row Building

        /// <summary>
        /// Populates <see cref="DisplayedSheets"/> with one row per Revit sheet.
        /// Called once at construction; the collection is not rebuilt on refresh —
        /// only the status flags on each existing row are updated.
        /// </summary>
        private void BuildSheetRows()
        {
            DisplayedSheets.Clear();

            var documents = _databaseDataModel.Documents.ToList();
            var rows = _revitDataModel.GetSheets()
                .Select(sheet =>
                {
                    var row = new RevitSheetRowViewModel(sheet, onSelectionChanged: UpdateCounts);
                    row.UpdateDatabaseStatus(documents);
                    return row;
                })
                .OrderBy(r => r.SheetNumber, StringComparer.OrdinalIgnoreCase);

            foreach (var row in rows)
                DisplayedSheets.Add(row);

            UpdateCounts();
        }

        /// <summary>
        /// Notifies all count-derived properties and re-evaluates command can-execute states.
        /// Also registered as the per-row <c>onSelectionChanged</c> callback so every
        /// manual checkbox tick triggers a re-evaluation of <c>UpdateCommand</c>.
        /// </summary>
        private void UpdateCounts()
        {
            OnPropertyChanged(nameof(TotalCount));
            OnPropertyChanged(nameof(ToImportCount));
            OnPropertyChanged(nameof(ToUpdateCount));
            OnPropertyChanged(nameof(SelectedCount));
            UpdateCommand.NotifyCanExecuteChanged();
            SelectAllCommand.NotifyCanExecuteChanged();
            SelectNoneCommand.NotifyCanExecuteChanged();
        }

        #endregion Private Methods — Row Building

        #region Private Methods — Import

        /// <summary>
        /// Inserts the selected import rows as new <see cref="Document"/> records and,
        /// when <paramref name="customPropertiesVm"/> is provided, also inserts the
        /// custom property values entered by the user.
        /// </summary>
        private void CommitImport(
            List<RevitSheetRowViewModel> rowsToImport,
            SheetCustomPropertiesViewModel? customPropertiesVm)
        {
            IsBusy = true;
            try
            {
                var unitOfWork = _databaseDataModel.Api.GetUnitOfWorkSync();
                var documentsToInsert = rowsToImport
                    .Select(r => new Document(
                        r.BuiltDocumentNumber.Trim(),
                        r.BuiltDocumentName.Trim()))
                    .ToList();

                int inserted = unitOfWork.Documents.InsertAll(documentsToInsert);

                if (inserted <= 0)
                {
                    _messageStore.EnqueueMessage(
                        "No sheets were imported into the database.",
                        MessageTypes.Warning,
                        dismissAfterSeconds: 10);
                    return;
                }

                if (customPropertiesVm != null && _customFieldDefinitions.Any())
                {
                    var customPropertiesToInsert = new List<CustomProperty>();

                    foreach (var sheetRow in customPropertiesVm.SheetRows)
                    {
                        var insertedDocument = documentsToInsert.FirstOrDefault(d =>
                            string.Equals(d.Number, sheetRow.DocumentNumber,
                                StringComparison.OrdinalIgnoreCase));

                        if (insertedDocument == null) continue;

                        foreach (var fieldValue in sheetRow.CustomFieldValues)
                        {
                            customPropertiesToInsert.Add(new CustomProperty(
                                insertedDocument.Id,
                                fieldValue.CustomFieldDefinitionId,
                                fieldValue.Value ?? string.Empty));
                        }
                    }

                    if (customPropertiesToInsert.Any())
                        unitOfWork.CustomProperties.InsertAll(customPropertiesToInsert);
                }

                _messageStore.EnqueueMessage(
                    $"Successfully imported {inserted} sheet(s) into the database.",
                    MessageTypes.Information,
                    dismissAfterSeconds: 5);
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error importing sheets: {ex.Message}",
                    MessageTypes.Error);
            }
            finally
            {
                IsBusy = false;
            }
        }

        #endregion Private Methods — Import

        #region Private Methods — Name Update

        /// <summary>
        /// Updates the stored document name for each row where the built document name
        /// differs from the name currently in the database.
        /// </summary>
        private void CommitNameUpdates(List<RevitSheetRowViewModel> rowsToUpdate)
        {
            IsBusy = true;
            try
            {
                var unitOfWork = _databaseDataModel.Api.GetUnitOfWorkSync();
                int updatedCount = 0;

                foreach (var row in rowsToUpdate)
                {
                    var existingDocuments = unitOfWork.Documents.GetDocumentsByNumber(
                        row.BuiltDocumentNumber);
                    var document = existingDocuments.FirstOrDefault();

                    if (document == null)
                    {
                        _messageStore.EnqueueMessage(
                            $"Document '{row.BuiltDocumentNumber}' not found in database — skipped.",
                            MessageTypes.Warning,
                            dismissAfterSeconds: 15);
                        continue;
                    }

                    document.Name = row.BuiltDocumentName.Trim();
                    int rowsAffected = unitOfWork.Documents.Update(document);

                    if (rowsAffected > 0)
                    {
                        updatedCount++;
                    }
                    else
                    {
                        _messageStore.EnqueueMessage(
                            $"Failed to update document '{row.BuiltDocumentNumber}'.",
                            MessageTypes.Warning,
                            dismissAfterSeconds: 15);
                    }
                }

                if (updatedCount > 0)
                {
                    _messageStore.EnqueueMessage(
                        $"Successfully updated {updatedCount} document name(s).",
                        MessageTypes.Information,
                        dismissAfterSeconds: 5);
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error updating document names: {ex.Message}",
                    MessageTypes.Error);
            }
            finally
            {
                IsBusy = false;
            }
        }

        #endregion Private Methods — Name Update

        #region Lifecycle

        /// <summary>
        /// Handles <see cref="DatabaseDataModel.PropertyChanged"/> to re-evaluate command
        /// can-execute states whenever <see cref="DatabaseDataModel.IsConnected"/> changes.
        /// </summary>
        private void OnDatabaseDataModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(DatabaseDataModel.IsConnected))
            {
                UpdateCounts();
                OnPropertyChanged(nameof(IsDatabaseConnected));
                OnPropertyChanged(nameof(HintText));
            }
        }

        /// <inheritdoc/>
        public override void OnClosing()
        {
            _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
            base.OnClosing();
        }

        /// <inheritdoc/>
        public override void Dispose()
        {
            _databaseDataModel.PropertyChanged -= OnDatabaseDataModelPropertyChanged;
            base.Dispose();
        }

        #endregion Lifecycle
    }
}
