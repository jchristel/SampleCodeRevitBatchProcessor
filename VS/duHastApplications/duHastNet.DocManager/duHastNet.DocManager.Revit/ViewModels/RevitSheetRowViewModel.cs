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
using duHastNet.DocManager.Revit.Utilities.RevitData;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// ViewModel representing a single Revit sheet row displayed in the Sheets panel.
    /// <para>
    /// Wraps a <see cref="RevitSheet"/> and computes status by comparing the sheet's built
    /// document number and name against the documents currently in the database.
    /// </para>
    /// <para>
    /// Colour coding:
    /// <list type="bullet">
    ///   <item>Red — not in database; available for import.</item>
    ///   <item>Yellow — in database but name differs; available for name update.</item>
    ///   <item>Green — in database and name matches; no action required.</item>
    /// </list>
    /// </para>
    /// <para>
    /// The optional <see cref="Action"/> callback passed at construction is invoked whenever
    /// <see cref="IsSelected"/> changes so the parent <see cref="SheetsPanelViewModel"/> can
    /// refresh command can-execute states without subscribing to <c>PropertyChanged</c> on
    /// every row.
    /// </para>
    /// </summary>
    public partial class RevitSheetRowViewModel : ObservableObject
    {
        #region Private Fields

        private readonly Action? _onSelectionChanged;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// Gets or sets whether this row is selected by the user for the Update operation.
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
        private string _builtDocumentNumber = string.Empty;

        /// <summary>
        /// Gets the built document name derived from the sheet name builder rules.
        /// Falls back to the raw sheet name when no builder rule is configured.
        /// </summary>
        [ObservableProperty]
        private string _builtDocumentName = string.Empty;

        /// <summary>
        /// Gets the most recent revision indicator on this sheet, or an empty string when the
        /// sheet carries no revision-on-sheet entries.
        /// </summary>
        [ObservableProperty]
        private string _currentRevision = string.Empty;

        /// <summary>Gets whether a document with the same built document number exists in the database.</summary>
        [ObservableProperty]
        private bool _isAlreadyInDatabase;

        /// <summary>Gets whether the document is in the database but its stored name differs from the built name.</summary>
        [ObservableProperty]
        private bool _needsNameUpdate;

        /// <summary>Gets the document name currently stored in the database, or empty when not in database.</summary>
        [ObservableProperty]
        private string _databaseDocumentName = string.Empty;

        #endregion Observable Properties

        #region Computed Properties

        /// <summary>
        /// Gets a WPF colour name for the status dot.
        /// <list type="bullet">
        ///   <item><c>"Red"</c> — not in database.</item>
        ///   <item><c>"Yellow"</c> — in database, name differs.</item>
        ///   <item><c>"Green"</c> — in database, name matches.</item>
        /// </list>
        /// </summary>
        public string StatusColor
        {
            get
            {
                if (!IsAlreadyInDatabase) return "Red";
                if (NeedsNameUpdate) return "Yellow";
                return "Green";
            }
        }

        /// <summary>Gets a human-readable status description for the DataGrid.</summary>
        public string StatusMessage
        {
            get
            {
                if (!IsAlreadyInDatabase) return "Not in database — can be imported";
                if (NeedsNameUpdate) return "Name differs — can be updated";
                return "Up to date";
            }
        }

        /// <summary>Gets whether this sheet can be imported (not yet in the database).</summary>
        public bool CanImport => !IsAlreadyInDatabase;

        /// <summary>Gets whether this sheet's name can be updated (in database, name differs).</summary>
        public bool CanUpdate => IsAlreadyInDatabase && NeedsNameUpdate;

        #endregion Computed Properties

        #region Constructor

        /// <summary>
        /// Creates a new <see cref="RevitSheetRowViewModel"/> from a Revit sheet.
        /// </summary>
        /// <param name="sheet">The Revit sheet to wrap. Must not be null.</param>
        /// <param name="onSelectionChanged">
        /// Optional callback invoked whenever <see cref="IsSelected"/> changes.
        /// Pass the parent panel's <c>UpdateCounts</c> so commands re-evaluate on every tick.
        /// </param>
        /// <exception cref="ArgumentNullException">Thrown when <paramref name="sheet"/> is null.</exception>
        public RevitSheetRowViewModel(RevitSheet sheet, Action? onSelectionChanged = null)
        {
            _ = sheet ?? throw new ArgumentNullException(nameof(sheet));

            _onSelectionChanged = onSelectionChanged;

            SheetNumber = sheet.SheetNumber?.Value ?? string.Empty;
            SheetName = sheet.SheetName?.Value ?? string.Empty;

            sheet.BuiltDocumentProperties.TryGetValue(
                duHastNet.UI.DocManagerSettingsUI.Utils.Constants.DocumentPropertyKeyDocumentNumber,
                out string? builtNumber);
            BuiltDocumentNumber = builtNumber ?? SheetNumber;

            sheet.BuiltDocumentProperties.TryGetValue(
                duHastNet.UI.DocManagerSettingsUI.Utils.Constants.DocumentPropertyKeyDocumentName,
                out string? builtName);
            BuiltDocumentName = builtName ?? SheetName;

            var lastRevisionOnSheet = sheet.RevisionsOnSheet.LastOrDefault();
            CurrentRevision = lastRevisionOnSheet?.RevisionIndicator ?? string.Empty;
        }

        #endregion Constructor

        #region Public Methods

        /// <summary>
        /// Updates database-status fields by matching <see cref="BuiltDocumentNumber"/> against
        /// the provided active database documents.
        /// </summary>
        /// <param name="databaseDocuments">Active documents from the database. Must not be null.</param>
        /// <exception cref="ArgumentNullException">Thrown when <paramref name="databaseDocuments"/> is null.</exception>
        public void UpdateDatabaseStatus(
            IEnumerable<duHastNet.DocManager.Core.Models.Document> databaseDocuments)
        {
            _ = databaseDocuments ?? throw new ArgumentNullException(nameof(databaseDocuments));

            var match = databaseDocuments.FirstOrDefault(d =>
                string.Equals(d.Number, BuiltDocumentNumber, StringComparison.OrdinalIgnoreCase));

            if (match != null)
            {
                IsAlreadyInDatabase = true;
                DatabaseDocumentName = match.Name;
                NeedsNameUpdate = !string.Equals(
                    match.Name, BuiltDocumentName, StringComparison.OrdinalIgnoreCase);
            }
            else
            {
                IsAlreadyInDatabase = false;
                DatabaseDocumentName = string.Empty;
                NeedsNameUpdate = false;
            }

            OnPropertyChanged(nameof(StatusColor));
            OnPropertyChanged(nameof(StatusMessage));
            OnPropertyChanged(nameof(CanImport));
            OnPropertyChanged(nameof(CanUpdate));
        }

        #endregion Public Methods

        #region Property Change Handlers

        partial void OnIsSelectedChanged(bool value)
        {
            _onSelectionChanged?.Invoke();
        }

        partial void OnIsAlreadyInDatabaseChanged(bool value)
        {
            OnPropertyChanged(nameof(StatusColor));
            OnPropertyChanged(nameof(StatusMessage));
            OnPropertyChanged(nameof(CanImport));
            OnPropertyChanged(nameof(CanUpdate));
        }

        partial void OnNeedsNameUpdateChanged(bool value)
        {
            OnPropertyChanged(nameof(StatusColor));
            OnPropertyChanged(nameof(StatusMessage));
            OnPropertyChanged(nameof(CanImport));
            OnPropertyChanged(nameof(CanUpdate));
        }

        #endregion Property Change Handlers
    }
}
