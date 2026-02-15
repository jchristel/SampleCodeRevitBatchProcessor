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

using CommunityToolkit.Mvvm.Input;
using duHastNet.UI.PDFDWGExporterSelectionUI.Models;
using duHastNet.Utils.WPF.Interfaces;
using System;
using System.ComponentModel;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Commands
{
    /// <summary>
    /// Command to duplicate an existing print set
    /// </summary>
    public partial class PrintSetDuplicateCommand : ICloseable, IDisposable
    {
        private readonly ViewModels.DocumentSelectionViewModel _documentSelectionViewModel;
        private readonly Models.SheetsDataModel _revitSheetsDataModel;

        public PrintSetDuplicateCommand(
            ViewModels.DocumentSelectionViewModel documentSelectionViewModel,
            Models.SheetsDataModel revitSheetsDataModel)
        {
            _documentSelectionViewModel = documentSelectionViewModel;
            _revitSheetsDataModel = revitSheetsDataModel;

            // Subscribe to property changes to update CanExecute
            _documentSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }

        /// <summary>
        /// Duplicates the selected print set with a new name
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanDuplicate))]
        private void Duplicate()
        {
            try
            {
                // Get the name of the print set to duplicate
                string printSetToDuplicate = _documentSelectionViewModel.SelectedPrintSet;

                // Generate default new name
                string defaultNewPrintSetName = printSetToDuplicate + "_Copy";

                // Get all existing print set names
                var allPrintSetNames = _revitSheetsDataModel.GetAllPrintSetNames();

                // Show dialog to get new name from user
                var inputDialog = new Views.PrintSetNameDialog(defaultNewPrintSetName, allPrintSetNames);
                if (inputDialog.ShowDialog() != true)
                {
                    // User cancelled
                    return;
                }

                // Get the new name from the dialog
                string newPrintSetName = inputDialog.PrintSetName;

                // Create the new print set
                Models.RevitPrintSet newPrintSet = new Models.RevitPrintSet(
                    name: newPrintSetName,
                    updateAction: PrintSetUpdateType.New
                );

                // Get the original print set
                var originalPrintSet = _revitSheetsDataModel.GetPrintSetByName(printSetToDuplicate);

                // Validate that original print set was found
                if (originalPrintSet == null)
                {
                    _documentSelectionViewModel.AddMessage(
                        $"Error: Original print set '{printSetToDuplicate}' not found.",
                        duHastNet.Utils.WPF.Stores.MessageTypes.Error
                    );
                    return;
                }

                // Copy sheets from original to new print set
                foreach (var sheet in originalPrintSet.RevitSheets)
                {
                    newPrintSet.AddRevitSheet(sheet);
                }

                // Add the new print set to the model
                _revitSheetsDataModel.PrintSets.Add(newPrintSet);

                // Notify that the model has been updated
                _revitSheetsDataModel.RaisePropertyChanged(Utils.PropertyChangedEventNames.DATA_MODEL_PRINTSETS_UPDATED);

                // Select the new print set
                _documentSelectionViewModel.SelectedPrintSet = newPrintSetName;

                // Inform user
                _documentSelectionViewModel.AddMessage(
                    $"New print set '{newPrintSetName}' created.",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Information
                );
            }
            catch (Exception ex)
            {
                _documentSelectionViewModel.AddMessage(
                    $"Error during print set duplication: {ex.Message}",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Error
                );
            }
        }

        /// <summary>
        /// Determines if the duplicate command can execute
        /// Command is enabled when a print set (other than default) is selected
        /// </summary>
        private bool CanDuplicate()
        {
            return _documentSelectionViewModel.SelectedPrintSet != Constants.DefaultPrintSetName;
        }

        /// <summary>
        /// Handles property changes from the ViewModel to update command state
        /// </summary>
        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(ViewModels.DocumentSelectionViewModel.SelectedPrintSet))
            {
                // Notify that CanExecute state may have changed
                DuplicateCommand.NotifyCanExecuteChanged();
            }
        }

        #region ICloseable Implementation

        public void OnClosing()
        {
            // No UI-specific cleanup needed for commands
        }

        #endregion

        #region IDisposable Implementation

        private bool _disposed = false;

        public void Dispose()
        {
            if (_disposed)
                return;

            // Unsubscribe from events to prevent memory leaks
            if (_documentSelectionViewModel != null)
            {
                _documentSelectionViewModel.PropertyChanged -= OnViewModelPropertyChanged;
            }

            _disposed = true;
        }

        #endregion
    }
}