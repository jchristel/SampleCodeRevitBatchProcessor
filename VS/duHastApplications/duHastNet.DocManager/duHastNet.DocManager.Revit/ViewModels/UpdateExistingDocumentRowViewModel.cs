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
using duHastNet.DocManager.UI.Shared.ViewModels;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// Represents a single row in the Update Existing Document assignment dialog.
    /// <para>
    /// Exposes the Revit sheet's read-only display properties and an observable
    /// <see cref="SelectedDocument"/> that the user sets via a ComboBox.  The parent
    /// <see cref="UpdateExistingDocumentViewModel"/> sets <see cref="IsDuplicateAssignment"/>
    /// after each selection change to reflect cross-row validation state.
    /// </para>
    /// </summary>
    public partial class UpdateExistingDocumentRowViewModel : AppViewModelBase
    {
        #region Private Fields

        private readonly Action _onSelectionChanged;

        #endregion Private Fields

        #region Read-Only Display Properties

        /// <summary>Gets the Revit sheet number. Display-only.</summary>
        public string SheetNumber { get; }

        /// <summary>Gets the Revit sheet name. Display-only.</summary>
        public string SheetName { get; }

        /// <summary>
        /// Gets the built document number that will be written to the selected database
        /// document on confirmation. Display-only.
        /// </summary>
        public string BuiltDocumentNumber { get; }

        /// <summary>
        /// Gets the built document name that will be written to the selected database
        /// document on confirmation. Display-only.
        /// </summary>
        public string BuiltDocumentName { get; }

        /// <summary>Gets the most recent revision indicator for this sheet. Display-only.</summary>
        public string CurrentRevision { get; }

        /// <summary>
        /// Gets all database documents available for selection, used to populate the ComboBox.
        /// </summary>
        public IReadOnlyList<Document> AvailableDocuments { get; }

        #endregion Read-Only Display Properties

        #region Observable Properties

        /// <summary>
        /// Gets or sets the database document that the user has assigned to this sheet.
        /// <c>null</c> until the user makes a selection.
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(HasSelection))]
        [NotifyPropertyChangedFor(nameof(StatusMessage))]
        private Document? _selectedDocument;


        /// <summary>
        /// Gets or sets whether this row's assignment conflicts with another row's assignment.
        /// Set externally by <see cref="UpdateExistingDocumentViewModel"/> after each selection change.
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(StatusMessage))]
        private bool _isDuplicateAssignment;

        #endregion Observable Properties

        #region Computed Properties

        /// <summary>Gets whether the user has selected a database document for this row.</summary>
        public bool HasSelection => SelectedDocument != null;

        /// <summary>
        /// Gets a per-row validation message shown in the Status column.
        /// Empty when the row is validly assigned.
        /// </summary>
        public string StatusMessage
        {
            get
            {
                if (!HasSelection)
                    return "Not assigned";
                if (IsDuplicateAssignment)
                    return "Duplicate assignment";
                return string.Empty;
            }
        }

        #endregion Computed Properties

        #region Constructor

        /// <summary>
        /// Initialises a new instance of <see cref="UpdateExistingDocumentRowViewModel"/>.
        /// </summary>
        /// <param name="sourceRow">The Revit sheet row being assigned. Must not be null.</param>
        /// <param name="availableDocuments">
        /// All database documents available for selection. Must not be null.
        /// </param>
        /// <param name="onSelectionChanged">
        /// Callback invoked whenever <see cref="SelectedDocument"/> changes so the parent
        /// ViewModel can re-run cross-row validation. Must not be null.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when any parameter is null.
        /// </exception>
        public UpdateExistingDocumentRowViewModel(
            RevitSheetRowViewModel sourceRow,
            IReadOnlyList<Document> availableDocuments,
            Action onSelectionChanged)
        {
            _ = sourceRow ?? throw new ArgumentNullException(nameof(sourceRow));
            _ = availableDocuments ?? throw new ArgumentNullException(nameof(availableDocuments));
            _onSelectionChanged = onSelectionChanged ?? throw new ArgumentNullException(nameof(onSelectionChanged));

            SheetNumber = sourceRow.SheetNumber;
            SheetName = sourceRow.SheetName;
            BuiltDocumentNumber = sourceRow.BuiltDocumentNumber;
            BuiltDocumentName = sourceRow.BuiltDocumentName;
            CurrentRevision = sourceRow.CurrentRevision;
            AvailableDocuments = availableDocuments;
        }

        #endregion Constructor

        #region Property Change Handlers

        partial void OnSelectedDocumentChanged(Document? value)
        {
            _onSelectionChanged.Invoke();
        }

        #endregion Property Change Handlers
    }
}
