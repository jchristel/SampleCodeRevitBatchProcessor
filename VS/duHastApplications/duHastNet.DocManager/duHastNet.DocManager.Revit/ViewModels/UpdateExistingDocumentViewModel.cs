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
using duHastNet.DocManager.UI.Shared.ViewModels;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// ViewModel for <see cref="duHastNet.DocManager.Revit.Views.UpdateExistingDocumentWindow"/>.
    /// <para>
    /// Shown as a modal dialog when the user selects one or more red (not-in-database) sheet
    /// rows and clicks "Update Existing Document". The user assigns each sheet to an existing
    /// database document whose number has changed, then confirms.
    /// </para>
    /// <para>
    /// Two safety checks are enforced before confirmation is permitted:
    /// <list type="bullet">
    ///   <item>Every row must have a <see cref="UpdateExistingDocumentRowViewModel.SelectedDocument"/> assigned.</item>
    ///   <item>No two rows may be assigned the same database document.</item>
    /// </list>
    /// Both checks are re-evaluated after every ComboBox selection change via
    /// <see cref="RevalidateAssignments"/>.
    /// </para>
    /// <para>
    /// Follows the same pattern as <see cref="SheetCustomPropertiesViewModel"/>: raises
    /// <see cref="RequestClose"/> when either command is invoked, and the caller inspects
    /// <see cref="DialogConfirmed"/> to determine whether to proceed.
    /// </para>
    /// </summary>
    public partial class UpdateExistingDocumentViewModel : AppViewModelBase
    {
        #region Events

        /// <summary>
        /// Raised when the ViewModel requests the window to close.
        /// The window code-behind sets <see cref="System.Windows.Window.DialogResult"/>
        /// to <see cref="DialogConfirmed"/> before calling <c>Close()</c>.
        /// </summary>
        public event EventHandler? RequestClose;

        #endregion Events

        #region Observable Properties

        /// <summary>
        /// One row per selected red sheet, each requiring the user to assign an existing
        /// database document number.
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<UpdateExistingDocumentRowViewModel> _rows;

        /// <summary>
        /// Gets whether the user confirmed the dialog (Confirm button clicked).
        /// <c>false</c> when the dialog is cancelled.
        /// </summary>
        [ObservableProperty]
        private bool _dialogConfirmed;

        #endregion Observable Properties

        #region Computed Properties

        /// <summary>
        /// Gets whether confirmation is permitted.
        /// <c>true</c> only when every row has a selection AND no duplicate assignments exist.
        /// </summary>
        public bool CanConfirm
        {
            get
            {
                if (Rows == null || !Rows.Any())
                    return false;

                // All rows must have a selection.
                if (!Rows.All(r => r.HasSelection))
                    return false;

                // No two rows may share the same document Id.
                bool hasDuplicates = Rows
                    .GroupBy(r => r.SelectedDocument!.Id)
                    .Any(g => g.Count() > 1);

                return !hasDuplicates;
            }
        }

        /// <summary>
        /// Gets a human-readable validation summary displayed above the button bar.
        /// </summary>
        public string ValidationSummary
        {
            get
            {
                if (Rows == null || !Rows.Any())
                    return string.Empty;

                int total = Rows.Count;
                int assigned = Rows.Count(r => r.HasSelection);

                bool hasDuplicates = Rows
                    .Where(r => r.HasSelection)
                    .GroupBy(r => r.SelectedDocument!.Id)
                    .Any(g => g.Count() > 1);

                if (hasDuplicates)
                    return "Duplicate document assigned — each existing document can only be assigned once.";

                if (assigned < total)
                    return $"{assigned} of {total} sheet(s) assigned. Assign all sheets to continue.";

                return $"All {total} sheet(s) assigned — ready to confirm.";
            }
        }

        #endregion Computed Properties

        #region Constructor

        /// <summary>
        /// Initialises a new instance of <see cref="UpdateExistingDocumentViewModel"/>.
        /// </summary>
        /// <param name="selectedRows">
        /// The red sheet rows selected for assignment. Must not be null or empty.
        /// </param>
        /// <param name="databaseDataModel">
        /// Shared database data model supplying the available documents list. Must not be null.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="selectedRows"/> or <paramref name="databaseDataModel"/> is null.
        /// </exception>
        /// <exception cref="ArgumentException">
        /// Thrown when <paramref name="selectedRows"/> is empty.
        /// </exception>
        public UpdateExistingDocumentViewModel(
            IList<RevitSheetRowViewModel> selectedRows,
            DatabaseDataModel databaseDataModel)
        {
            _ = selectedRows ?? throw new ArgumentNullException(nameof(selectedRows));
            _ = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));

            if (!selectedRows.Any())
                throw new ArgumentException(
                    "At least one sheet row must be provided.", nameof(selectedRows));

            // Snapshot the available documents as a read-only list once so every row
            // shares the same reference and the list is stable for the dialog lifetime.
            IReadOnlyList<Document> availableDocuments =
                databaseDataModel.Documents.OrderBy(d => d.Number, StringComparer.OrdinalIgnoreCase).ToList();

            _rows = new ObservableCollection<UpdateExistingDocumentRowViewModel>(
                selectedRows.Select(r => new UpdateExistingDocumentRowViewModel(
                    r,
                    availableDocuments,
                    RevalidateAssignments)));
        }

        #endregion Constructor

        #region Commands

        /// <summary>
        /// Confirms the assignments and closes the window with <see cref="DialogConfirmed"/>
        /// set to <c>true</c>.
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanConfirm))]
        private void Confirm()
        {
            DialogConfirmed = true;
            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        /// <summary>
        /// Cancels the dialog and closes the window with <see cref="DialogConfirmed"/>
        /// left as <c>false</c>.
        /// </summary>
        [RelayCommand]
        private void Cancel()
        {
            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        #endregion Commands

        #region Private Methods

        /// <summary>
        /// Re-evaluates cross-row duplicate detection after any ComboBox selection changes.
        /// <para>
        /// Sets <see cref="UpdateExistingDocumentRowViewModel.IsDuplicateAssignment"/> on
        /// every row, then notifies <see cref="CanConfirm"/>, <see cref="ValidationSummary"/>,
        /// and the <see cref="ConfirmCommand"/> can-execute state.
        /// </para>
        /// </summary>
        private void RevalidateAssignments()
        {
            // Identify document Ids that appear more than once across assigned rows.
            var duplicateIds = Rows
                .Where(r => r.HasSelection)
                .GroupBy(r => r.SelectedDocument!.Id)
                .Where(g => g.Count() > 1)
                .Select(g => g.Key)
                .ToHashSet();

            foreach (var row in Rows)
            {
                row.IsDuplicateAssignment =
                    row.HasSelection && duplicateIds.Contains(row.SelectedDocument!.Id);
            }

            OnPropertyChanged(nameof(CanConfirm));
            OnPropertyChanged(nameof(ValidationSummary));
            ConfirmCommand.NotifyCanExecuteChanged();
        }

        #endregion Private Methods
    }
}
