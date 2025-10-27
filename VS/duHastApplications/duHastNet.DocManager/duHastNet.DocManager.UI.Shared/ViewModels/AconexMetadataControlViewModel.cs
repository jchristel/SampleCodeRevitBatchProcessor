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
using duHastNet.DocManager.Core.Models.MetaData;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;
using System.ComponentModel.DataAnnotations;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels.CloudProviderControls
{
    /// <summary>
    /// ViewModel for Aconex metadata control
    /// Handles template file path and metadata field mappings for Aconex integration
    /// Phase 1: Template file path only
    /// Phase 2: Will add metadata mapping ListView with Add/Edit/Remove functionality
    /// </summary>
    public partial class AconexMetadataControlViewModel : ObservableValidator
    {
        #region Private Fields

        private readonly MessageStore _messageStore;
        private readonly IDialogService _dialogService;
        private readonly MetaDataMapperAconex _aconexMapper;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// The template metadata file path
        /// Validated to ensure file exists and has correct extension
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(AconexMetadataControlViewModel), nameof(ValidateTemplateFilePath))]
        private string _templateMetaDataFilePath = string.Empty;

        /// <summary>
        /// Controls whether the browse button is enabled
        /// Disabled during file dialog operations
        /// </summary>
        [ObservableProperty]
        private bool _isBrowseTemplateFileEnabled = true;

        /// <summary>
        /// Collection of metadata field mappings
        /// Phase 2: Will be populated and displayed in ListView
        /// </summary>
        public ObservableCollection<MetaDataMap> MetaDataMappings { get; }

        #endregion Observable Properties

        #region Property Changed Handlers

        /// <summary>
        /// Called when TemplateMetaDataFilePath property changes
        /// Triggers validation and updates the underlying model
        /// </summary>
        partial void OnTemplateMetaDataFilePathChanged(string value)
        {
            ValidateProperty(value, nameof(TemplateMetaDataFilePath));
            
            // Update the underlying mapper
            if (_aconexMapper != null)
            {
                _aconexMapper.MetadataTemplateFilePath = value;
            }
        }

        #endregion Property Changed Handlers

        #region Constructor

        /// <summary>
        /// Constructor for Aconex metadata control
        /// </summary>
        /// <param name="messageStore">Message store for displaying messages</param>
        /// <param name="dialogService">Dialog service for file selection</param>
        /// <param name="aconexMapper">The Aconex mapper instance to bind to</param>
        public AconexMetadataControlViewModel(
            MessageStore messageStore, 
            IDialogService dialogService, 
            MetaDataMapperAconex aconexMapper)
        {
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
            _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));
            _aconexMapper = aconexMapper ?? throw new ArgumentNullException(nameof(aconexMapper));

            // Initialize metadata mappings collection
            MetaDataMappings = new ObservableCollection<MetaDataMap>();

            // Load existing values from the mapper
            LoadFromMapper();

            // Validate immediately to show any initial validation state
            ValidateAllProperties();
        }

        #endregion Constructor

        #region Commands

        /// <summary>
        /// Command to browse for template file
        /// Opens file dialog for selecting Excel template files
        /// </summary>
        [RelayCommand]
        private void BrowseTemplateFile()
        {
            try
            {
                IsBrowseTemplateFileEnabled = false;
                
                // Use dialog service to show file dialog
                var selectedPath = _dialogService.ShowOpenFileDialog(
                    "Select Meta Data Template File",
                    "Excel files (*.xlsx;*.xls)|*.xlsx;*.xls|CSV files (*.csv)|*.csv|All files (*.*)|*.*");

                // Check for cancellation
                if (selectedPath == null || selectedPath.Length == 0)
                {
                    // User cancelled
                    return;
                }

                TemplateMetaDataFilePath = selectedPath[0];
            }
            finally
            {
                IsBrowseTemplateFileEnabled = true;
            }
        }

        // Phase 2: Commands for metadata mappings
        // [RelayCommand]
        // private void AddMetadataMapping() { }
        
        // [RelayCommand]
        // private void EditMetadataMapping() { }
        
        // [RelayCommand]
        // private void RemoveMetadataMapping() { }

        #endregion Commands

        #region Validation

        /// <summary>
        /// Validates the template file path
        /// Checks if file exists and has valid extension
        /// </summary>
        public static ValidationResult? ValidateTemplateFilePath(string? value, ValidationContext context)
        {
            var viewModel = context.ObjectInstance as AconexMetadataControlViewModel;
            if (viewModel == null)
                return ValidationResult.Success;

            // Not required - can be empty
            if (string.IsNullOrWhiteSpace(value))
                return ValidationResult.Success;

            // Check if file exists
            if (!File.Exists(value))
                return new ValidationResult("Template file does not exist");

            // Check file extension (Excel or CSV)
            var extension = Path.GetExtension(value).ToLowerInvariant();
            if (extension != ".xlsx" && extension != ".xls" && extension != ".csv")
                return new ValidationResult("Template file must be an Excel (.xlsx, .xls) or CSV (.csv) file");

            return ValidationResult.Success;
        }

        #endregion Validation

        #region Helper Methods

        /// <summary>
        /// Loads values from the Aconex mapper instance
        /// </summary>
        private void LoadFromMapper()
        {
            if (_aconexMapper == null)
                return;

            // Load template file path
            TemplateMetaDataFilePath = _aconexMapper.MetadataTemplateFilePath ?? string.Empty;

            // Phase 2: Load metadata mappings
            // MetaDataMappings.Clear();
            // foreach (var mapping in _aconexMapper.MetaDataMap)
            // {
            //     MetaDataMappings.Add(mapping);
            // }
        }

        /// <summary>
        /// Saves values back to the Aconex mapper instance
        /// Called when configuration is saved
        /// </summary>
        public void SaveToMapper()
        {
            if (_aconexMapper == null)
                return;

            // Template file path is already updated in property changed handler
            // No additional save logic needed for Phase 1

            // Phase 2: Save metadata mappings
            // _aconexMapper.ClearMappers();
            // foreach (var mapping in MetaDataMappings)
            // {
            //     _aconexMapper.AddMapper(mapping);
            // }
        }

        /// <summary>
        /// Validates all properties
        /// Returns true if valid, false otherwise
        /// </summary>
        public bool IsValid()
        {
            ValidateAllProperties();
            return !HasErrors;
        }

        #endregion Helper Methods
    }
}
