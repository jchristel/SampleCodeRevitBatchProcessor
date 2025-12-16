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


using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    /// <summary>
    /// Partial class for CurrentFolderViewModel containing all supported file types functionality
    /// </summary>
    public partial class CurrentFolderViewModel
    {
        #region Supported File Types - Observable Properties

        /// <summary>
        /// Observable collection of supported file types for display in ListView
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<SupportedFileTypeViewModel> _supportedFileTypes = new();

        /// <summary>
        /// Currently selected file type in the ListView
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(EditFileTypeCommand))]
        [NotifyCanExecuteChangedFor(nameof(RemoveFileTypeCommand))]
        private SupportedFileTypeViewModel? _selectedFileType;

        #endregion Supported File Types - Observable Properties

        #region Supported File Types - Initialization

        /// <summary>
        /// Initializes the supported file types collection from CurrentFolderManager settings
        /// Called during ViewModel construction
        /// Ensures PDF file type always exists
        /// </summary>
        private void InitializeSupportedFileTypes()
        {
            // Ensure PDF file type exists (required)
            EnsurePdfFileTypeExists();

            // Load existing file types from settings into display collection
            LoadSupportedFileTypesFromSettings();
        }

        /// <summary>
        /// Ensures that a PDF file type exists in the settings
        /// PDF is required and always present with no modifier (null)
        /// </summary>
        private void EnsurePdfFileTypeExists()
        {
            // Check if PDF already exists (case-insensitive)
            var pdfExists = _currentFolderManager.Settings.SupportedFileTypes.Any(
                ft => ft.FileExtension.Equals(".pdf", StringComparison.OrdinalIgnoreCase));

            if (!pdfExists)
            {
                // Create default PDF file type with no modifier
                var pdfFileType = new SupportedFileType(
                    fileExtension: ".pdf",
                    description: "PDF Document",
                    documentNumberModifier: null
                );

                _currentFolderManager.Settings.SupportedFileTypes.Add(pdfFileType);
            }
        }

        /// <summary>
        /// Loads supported file types from CurrentFolderManager.Settings into the SupportedFileTypes observable collection
        /// </summary>
        private void LoadSupportedFileTypesFromSettings()
        {
            SupportedFileTypes.Clear();

            foreach (var fileType in _currentFolderManager.Settings.SupportedFileTypes)
            {
                var displayModel = new SupportedFileTypeViewModel(fileType);
                SupportedFileTypes.Add(displayModel);
            }
        }

        #endregion Supported File Types - Initialization

        #region Supported File Types - Commands

        /// <summary>
        /// Command to add a new supported file type
        /// Opens the Add File Type dialog
        /// </summary>
        [RelayCommand]
        private void AddFileType()
        {
            try
            {
                // Create ViewModel for Add mode
                var dialogViewModel = new SupportedFileTypeDialogViewModel(this, _dialogService);

                // Create and show dialog
                var dialog = new Views.SupportedFileTypeDialog(dialogViewModel);
                dialog.Owner = System.Windows.Application.Current.MainWindow;

                var result = dialog.ShowDialog();

                if (result == true && dialogViewModel.CreatedFileType != null)
                {
                    AddFileTypeToCollections(dialogViewModel.CreatedFileType);

                    _messageStore.EnqueueMessage(
                        "File type added successfully",
                        MessageTypes.Information,dismissAfterSeconds: 3);
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error adding file type: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if a file type can be edited
        /// </summary>
        private bool CanEditFileType()
        {
            return SelectedFileType != null;
        }

        /// <summary>
        /// Command to edit the selected supported file type
        /// Opens the Edit File Type dialog with existing values
        /// For PDF: file extension field is disabled (cannot change)
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanEditFileType))]
        private void EditFileType()
        {
            if (SelectedFileType == null)
                return;

            try
            {
                var selectedIndex = SupportedFileTypes.IndexOf(SelectedFileType);

                // Create ViewModel for Edit mode
                var dialogViewModel = new SupportedFileTypeDialogViewModel(
                    this,
                    _dialogService,
                    SelectedFileType.UnderlyingFileType,
                    selectedIndex);

                // Create and show dialog
                var dialog = new Views.SupportedFileTypeDialog(dialogViewModel);
                dialog.Owner = System.Windows.Application.Current.MainWindow;

                var result = dialog.ShowDialog();

                if (result == true && dialogViewModel.CreatedFileType != null)
                {
                    ReplaceFileTypeAtIndex(selectedIndex, dialogViewModel.CreatedFileType);

                    _messageStore.EnqueueMessage(
                        "File type updated successfully",
                        MessageTypes.Information,dismissAfterSeconds: 3);
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error editing file type: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if a file type can be removed
        /// PDF file type cannot be removed (it's required)
        /// </summary>
        private bool CanRemoveFileType()
        {
            if (SelectedFileType == null)
                return false;

            // Cannot remove PDF file type (required)
            return !SelectedFileType.IsPdf;
        }

        /// <summary>
        /// Command to remove the selected supported file type
        /// PDF file type cannot be removed
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanRemoveFileType))]
        private void RemoveFileType()
        {
            if (SelectedFileType == null)
                return;

            try
            {
                // Double-check: prevent removal of PDF
                if (SelectedFileType.IsPdf)
                {
                    _messageStore.EnqueueMessage(
                        "The PDF file type is required and cannot be removed.",
                        MessageTypes.Warning, dismissAfterSeconds: 20);
                    return;
                }

                // Remove from settings
                _currentFolderManager.Settings.SupportedFileTypes.Remove(SelectedFileType.UnderlyingFileType);

                // Remove from display collection
                SupportedFileTypes.Remove(SelectedFileType);

                _messageStore.EnqueueMessage(
                    "File type removed successfully",
                    MessageTypes.Information,dismissAfterSeconds: 3);
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error removing file type: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        #endregion Supported File Types - Commands

        #region Supported File Types - Helper Methods

        /// <summary>
        /// Adds a newly created file type to both the settings and display collections
        /// </summary>
        /// <param name="fileType">The file type to add</param>
        private void AddFileTypeToCollections(SupportedFileType fileType)
        {
            // Add to settings
            _currentFolderManager.Settings.SupportedFileTypes.Add(fileType);

            // Add to display collection
            var displayModel = new SupportedFileTypeViewModel(fileType);
            SupportedFileTypes.Add(displayModel);
        }

        /// <summary>
        /// Replaces a file type at a specific index with an edited version
        /// </summary>
        /// <param name="index">Index of the file type to replace</param>
        /// <param name="editedFileType">The new file type to replace with</param>
        private void ReplaceFileTypeAtIndex(int index, SupportedFileType editedFileType)
        {
            // Replace in settings
            _currentFolderManager.Settings.SupportedFileTypes[index] = editedFileType;

            // Replace in display collection
            var displayModel = new SupportedFileTypeViewModel(editedFileType);
            SupportedFileTypes[index] = displayModel;
        }

        /// <summary>
        /// Checks if a file type with the given extension already exists
        /// Used for duplicate prevention
        /// </summary>
        /// <param name="extension">The file extension to check (case-insensitive)</param>
        /// <param name="excludeIndex">Optional index to exclude from check (for edit mode)</param>
        /// <returns>True if a duplicate exists, false otherwise</returns>
        public bool IsDuplicateFileExtension(string extension, int? excludeIndex = null)
        {
            for (int i = 0; i < SupportedFileTypes.Count; i++)
            {
                // Skip self when editing
                if (excludeIndex.HasValue && i == excludeIndex.Value)
                    continue;

                var fileType = SupportedFileTypes[i];

                // Check extension (case-insensitive)
                if (fileType.FileExtension.Equals(extension, StringComparison.OrdinalIgnoreCase))
                {
                    return true; // Duplicate found
                }
            }
            return false;
        }

        /// <summary>
        /// Checks if the file type at the given index is PDF
        /// Used for protection logic (PDF cannot be removed, extension cannot change)
        /// </summary>
        /// <param name="index">The index to check</param>
        /// <returns>True if the file type is PDF, false otherwise</returns>
        public bool IsPdfFileType(int index)
        {
            if (index < 0 || index >= SupportedFileTypes.Count)
                return false;

            return SupportedFileTypes[index].IsPdf;
        }

        #endregion Supported File Types - Helper Methods
    }
}