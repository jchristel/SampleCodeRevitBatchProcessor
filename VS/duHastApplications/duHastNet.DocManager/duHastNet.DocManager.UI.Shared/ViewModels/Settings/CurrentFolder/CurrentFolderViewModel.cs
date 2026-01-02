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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.Validators;
using System.ComponentModel.DataAnnotations;


namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder
{
    /// <summary>
    /// ViewModel for the Current Folder configuration view
    /// Implements hybrid validation: INotifyDataErrorInfo for field-level validation + MessageStore for operation-level feedback
    /// </summary>
    public partial class CurrentFolderViewModel : ObservableValidator
    {
        #region Private Fields

        private readonly MessageStore _messageStore;
        private readonly Manager _manager;
        private readonly Core.Models.CurrentFolder.CurrentFolderManager _currentFolderManager;
        private readonly IDialogService _dialogService;

        #endregion Private Fields

        #region Constructor

        public CurrentFolderViewModel(
            MessageStore messageStore,
            Manager manager,
            Core.Models.CurrentFolder.CurrentFolderManager currentFolderManager,
            IDialogService dialogService
        )
        {
            _manager = manager;
            _messageStore = messageStore;
            _currentFolderManager = currentFolderManager;
            _dialogService = dialogService;

            // Initialize ViewModel properties from CurrentFolderManager.Settings
            LoadSettingsIntoViewModel();

            // Initialize filing rules collection
            InitializeFilingRules();

            //initialise supported file types
            InitializeSupportedFileTypes();
        }

        #endregion Constructor

        #region Observable Properties

        /// <summary>
        /// Path to the folder containing incoming documents
        /// Validates that folder exists if specified
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(FolderPathValidator), nameof(FolderPathValidator.ValidateFolderExists))]
        private string _incomingFolderPath = string.Empty;

        [ObservableProperty]
        private bool _isBrowseIncomingFolderEnabled = true;

        /// <summary>
        /// Path to the folder where superseded/archived documents are stored
        /// Validates that folder exists if specified
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(FolderPathValidator), nameof(FolderPathValidator.ValidateFolderExists))]
        private string _archiveFolderPath = string.Empty;

        [ObservableProperty]
        private bool _isBrowseArchiveFolderEnabled = true;

        /// <summary>
        /// Character(s) that mark the beginning of a revision in a filename
        /// Example: '[' in "Document_Rev[A].pdf"
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(RevisionSeparatorValidator), nameof(RevisionSeparatorValidator.ValidateRevisionMarker))]
        private string _revisionPrefix = string.Empty;

        /// <summary>
        /// Character(s) that mark the end of a revision in a filename
        /// Example: ']' in "Document_Rev[A].pdf"
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(RevisionSeparatorValidator), nameof(RevisionSeparatorValidator.ValidateRevisionMarker))]
        private string _revisionSuffix = string.Empty;

        #endregion Observable Properties

        #region Property Changed Handlers

        /// <summary>
        /// Called when IncomingFolderPath property changes
        /// Syncs the value to CurrentFolderManager.Settings and triggers validation
        /// </summary>
        partial void OnIncomingFolderPathChanged(string value)
        {
            // Sync to settings
            _currentFolderManager.Settings.IncomingFolderPath = value;

            // Trigger immediate validation for field-level feedback
            ValidateProperty(value, nameof(IncomingFolderPath));
        }

        /// <summary>
        /// Called when ArchiveFolderPath property changes
        /// Syncs the value to CurrentFolderManager.Settings.SupersededFolderPath and triggers validation
        /// </summary>
        partial void OnArchiveFolderPathChanged(string value)
        {
            // Sync to settings (ArchiveFolderPath maps to SupersededFolderPath in settings)
            _currentFolderManager.Settings.SupersededFolderPath = value;

            // Trigger immediate validation for field-level feedback
            ValidateProperty(value, nameof(ArchiveFolderPath));
        }

        /// <summary>
        /// Called when RevisionPrefix property changes
        /// Syncs the value to CurrentFolderManager.Settings and triggers validation
        /// </summary>
        partial void OnRevisionPrefixChanged(string value)
        {
            // Sync to settings
            _currentFolderManager.Settings.RevisionPrefix = value;

            // Trigger immediate validation for field-level feedback
            ValidateProperty(value, nameof(RevisionPrefix));
        }

        /// <summary>
        /// Called when RevisionSuffix property changes
        /// Syncs the value to CurrentFolderManager.Settings and triggers validation
        /// </summary>
        partial void OnRevisionSuffixChanged(string value)
        {
            // Sync to settings
            _currentFolderManager.Settings.RevisionSuffix = value;

            // Trigger immediate validation for field-level feedback
            ValidateProperty(value, nameof(RevisionSuffix));
        }

        #endregion Property Changed Handlers

        #region Private Helper Methods

        /// <summary>
        /// Loads settings from CurrentFolderManager.Settings into ViewModel properties
        /// This is called on initialization to populate the UI with existing settings
        /// </summary>
        private void LoadSettingsIntoViewModel()
        {
            // Load properties from settings (use null-coalescing to handle nulls)
            IncomingFolderPath = _currentFolderManager.Settings.IncomingFolderPath ?? string.Empty;
            ArchiveFolderPath = _currentFolderManager.Settings.SupersededFolderPath ?? string.Empty;
            RevisionPrefix = _currentFolderManager.Settings.RevisionPrefix ?? string.Empty;
            RevisionSuffix = _currentFolderManager.Settings.RevisionSuffix ?? string.Empty;

            // Validate all properties to show any errors in loaded settings
            ValidateAllProperties();
        }

        #endregion Private Helper Methods

        #region Commands 

        /// <summary>
        /// Command to browse for incoming folder
        /// </summary>
        [RelayCommand]
        private void BrowseIncomingFolder()
        {
            try
            {
                var selectedPath = _dialogService.ShowFolderBrowserDialog(
                    "Select Incoming Folder",
                    IncomingFolderPath);

                if (!string.IsNullOrEmpty(selectedPath))
                {
                    IncomingFolderPath = selectedPath;
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error selecting incoming folder: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Command to browse for archive folder
        /// </summary>
        [RelayCommand]
        private void BrowseArchiveFolder()
        {
            try
            {
                var selectedPath = _dialogService.ShowFolderBrowserDialog(
                    "Select Archive Folder",
                    ArchiveFolderPath);

                if (!string.IsNullOrEmpty(selectedPath))
                {
                    ArchiveFolderPath = selectedPath;
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error selecting archive folder: {ex.Message}",
                    MessageTypes.Error);
            }
        }


        #endregion Commands 

    }
}