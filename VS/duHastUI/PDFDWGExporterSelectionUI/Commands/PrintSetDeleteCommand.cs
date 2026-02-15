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
    /// Command to delete a print set from the model
    /// </summary>
    public partial class PrintSetDeleteCommand : ICloseable, IDisposable
    {
        private readonly ViewModels.DocumentSelectionViewModel _documentSelectionViewModel;
        private readonly Models.SheetsDataModel _revitSheetsDataModel;

        public PrintSetDeleteCommand(
            ViewModels.DocumentSelectionViewModel documentSelectionViewModel,
            Models.SheetsDataModel revitSheetsDataModel)
        {
            _documentSelectionViewModel = documentSelectionViewModel;
            _revitSheetsDataModel = revitSheetsDataModel;

            // Subscribe to property changes to update CanExecute
            _documentSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }

        /// <summary>
        /// Deletes the selected print set by marking it for deletion
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanDelete))]
        private void Delete()
        {
            try
            {
                // Get the print set to delete
                string printSetToDelete = _documentSelectionViewModel.SelectedPrintSet;

                // Mark the print set for deletion
                foreach (var printSet in _revitSheetsDataModel.PrintSets)
                {
                    if (printSet.Name == printSetToDelete)
                    {
                        printSet.UpdateAction = PrintSetUpdateType.Delete;
                        break;
                    }
                }

                // Notify that the model has been updated
                _revitSheetsDataModel.RaisePropertyChanged(Utils.PropertyChangedEventNames.DATA_MODEL_PRINTSETS_UPDATED);

                // Reset selection to default
                _documentSelectionViewModel.SelectedPrintSet = Constants.DefaultPrintSetName;

                // Inform user
                _documentSelectionViewModel.AddMessage(
                    $"Print set '{printSetToDelete}' marked for deletion.",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Information
                );
            }
            catch (Exception ex)
            {
                _documentSelectionViewModel.AddMessage(
                    $"Error during print set deletion: {ex.Message}",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Error
                );
            }
        }

        /// <summary>
        /// Determines if the delete command can execute
        /// Command is enabled when a print set (other than default) is selected
        /// </summary>
        private bool CanDelete()
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
                DeleteCommand.NotifyCanExecuteChanged();
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