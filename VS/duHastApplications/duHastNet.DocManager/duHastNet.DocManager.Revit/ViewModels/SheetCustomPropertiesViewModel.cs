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
using duHastNet.DocManager.Core.Models.Database;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// ViewModel for <see cref="duHastNet.DocManager.Revit.Views.SheetCustomPropertiesWindow"/>.
    /// <para>
    /// Shown as a modal dialog when the user clicks Import and the database has active custom
    /// field definitions. The user fills in per-sheet custom property values, then clicks
    /// Confirm or Cancel.
    /// </para>
    /// <para>
    /// Follows the same pattern as <c>AddNewDocumentsDialogViewModel</c>: raises
    /// <see cref="RequestClose"/> when either command is invoked, and the caller inspects
    /// <see cref="DialogConfirmed"/> to determine whether to proceed.
    /// </para>
    /// </summary>
    public partial class SheetCustomPropertiesViewModel : ObservableObject
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
        /// Gets the per-sheet rows containing the custom field values the user must populate.
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<SheetImportRowViewModel> _sheetRows;

        /// <summary>
        /// Gets whether the user confirmed the dialog (Confirm clicked).
        /// <c>false</c> when the dialog is cancelled.
        /// </summary>
        [ObservableProperty]
        private bool _dialogConfirmed;

        #endregion Observable Properties

        #region Computed Properties

        /// <summary>
        /// Gets the active custom field definitions, used by the window code-behind to
        /// generate dynamic DataGrid columns.
        /// </summary>
        public IReadOnlyList<CustomFieldDefinition> CustomFieldDefinitions { get; }

        /// <summary>
        /// Gets a summary label displayed above the DataGrid.
        /// </summary>
        public string SummaryLabel =>
            $"Showing {SheetRows?.Count ?? 0} sheet(s) to import";

        #endregion Computed Properties

        #region Constructor

        /// <summary>
        /// Initialises a new instance of <see cref="SheetCustomPropertiesViewModel"/>.
        /// </summary>
        /// <param name="selectedRows">
        /// The sheet rows selected for import. Must not be null or empty.
        /// </param>
        /// <param name="customFieldDefinitions">
        /// The active custom field definitions for which the user must supply values.
        /// Must not be null.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="selectedRows"/> or
        /// <paramref name="customFieldDefinitions"/> is null.
        /// </exception>
        /// <exception cref="ArgumentException">
        /// Thrown when <paramref name="selectedRows"/> is empty.
        /// </exception>
        public SheetCustomPropertiesViewModel(
            IList<RevitSheetRowViewModel> selectedRows,
            IReadOnlyList<CustomFieldDefinition> customFieldDefinitions)
        {
            _ = selectedRows ?? throw new ArgumentNullException(nameof(selectedRows));
            _ = customFieldDefinitions ?? throw new ArgumentNullException(nameof(customFieldDefinitions));

            if (!selectedRows.Any())
                throw new ArgumentException(
                    "At least one sheet row must be provided.", nameof(selectedRows));

            CustomFieldDefinitions = customFieldDefinitions;

            _sheetRows = new ObservableCollection<SheetImportRowViewModel>(
                selectedRows.Select(r => new SheetImportRowViewModel(
                    r.BuiltDocumentNumber,
                    r.BuiltDocumentName,
                    r.CurrentRevision,
                    customFieldDefinitions)));
        }

        #endregion Constructor

        #region Commands

        /// <summary>
        /// Confirms the custom property values and closes the window with
        /// <see cref="DialogConfirmed"/> set to <c>true</c>.
        /// </summary>
        [RelayCommand]
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
    }
}
