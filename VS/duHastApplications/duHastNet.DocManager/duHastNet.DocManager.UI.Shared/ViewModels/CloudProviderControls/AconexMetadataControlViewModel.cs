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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;
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
        private readonly IMetaDataTemplateService _templateService;
        private readonly Manager _manager;

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
        /// Controls whether the refresh button is enabled
        /// Disabled during refresh operations or when no template file is selected
        /// </summary>
        [ObservableProperty]
        private bool _isRefreshTemplateEnabled = false;

        /// <summary>
        /// Collection of metadata field mappings
        /// Will be populated and displayed in ListView
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<MetaDataMapViewModel> _metaDataMappings;


        //public ObservableCollection<MetaDataMapViewModel> MetaDataMappings { get => _metaDataMappings; }

        #endregion Observable Properties

        #region Property Changed Handlers

        /// <summary>
        /// Called when TemplateMetaDataFilePath property changes
        /// Triggers validation, updates the underlying model, and loads template headers
        /// </summary>
        partial void OnTemplateMetaDataFilePathChanged(string value)
        {
            ValidateProperty(value, nameof(TemplateMetaDataFilePath));

            // Update the underlying mapper
            if (_aconexMapper != null)
            {
                _aconexMapper.MetadataTemplateFilePath = value;
            }

            // Enable/disable refresh button based on whether a valid file is selected
            IsRefreshTemplateEnabled = !string.IsNullOrWhiteSpace(value) && File.Exists(value);

            // Automatically load template headers when file path is set
            if (IsRefreshTemplateEnabled)
            {
                _ = LoadTemplateHeadersAsync();
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
        /// <param name="templateService">Service for reading metadata template files</param>
        public AconexMetadataControlViewModel(
            MessageStore messageStore,
            IDialogService dialogService,
            MetaDataMapperAconex aconexMapper,
            IMetaDataTemplateService templateService,
            Manager manager)
        {
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
            _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));
            _aconexMapper = aconexMapper ?? throw new ArgumentNullException(nameof(aconexMapper));
            _templateService = templateService ?? throw new ArgumentNullException(nameof(templateService));
            _manager = manager ?? throw new ArgumentNullException(nameof(manager));

            // Initialize metadata mappings collection
            _metaDataMappings = [];

            // Subscribe to MappingsChanged event from CloudDocumentManager
            // This event is raised when mappings are modified externally (e.g., custom field deactivation)
            _manager.CloudDocumentManager.MappingsChanged += OnMappingsChanged;

            // Load existing values from the mapper
            LoadFromMapper();

            // Validate immediately to show any initial validation state
            ValidateAllProperties();
        }

        #endregion Constructor

        #region Commands

        /// <summary>
        /// Command to browse for template file
        /// Opens file dialog for selecting CSV template files
        /// </summary>
        [RelayCommand]
        private void BrowseTemplateFile()
        {
            try
            {
                IsBrowseTemplateFileEnabled = false;

                // Use dialog service to show file dialog (CSV only as per requirements)
                var selectedPath = _dialogService.ShowOpenFileDialog(
                    "Select Meta Data Template File",
                    "CSV files (*.csv)|*.csv|All files (*.*)|*.*");

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

        /// <summary>
        /// Command to refresh the template headers from the current template file
        /// Re-reads the CSV file and updates available fields, cleaning up invalid mappings
        /// </summary>
        [RelayCommand]
        private async Task RefreshTemplateAsync()
        {
            if (string.IsNullOrWhiteSpace(TemplateMetaDataFilePath))
            {
                _messageStore.EnqueueMessage(
                    "No template file selected. Please select a template file first.", MessageTypes.Warning, dismissAfterSeconds: 20);
                return;
            }

            try
            {
                IsRefreshTemplateEnabled = false;

                // Re-read the template file
                var result = await _templateService.ReadColumnHeadersAsync(TemplateMetaDataFilePath);

                if (result.IsReadSuccessful)
                {
                    // Update available fields in the mapper
                    _aconexMapper.UpdateAvailableFields(result.ColumnHeaders);

                    // Clean up invalid mappings (fields that no longer exist in template)
                    var removedFields = _aconexMapper.CleanupInvalidMappings();

                    // Show success message
                    _messageStore.EnqueueMessage(
                        
                        $"Template refreshed: {result.ColumnHeaders.Count} column headers loaded.", MessageTypes.Information, dismissAfterSeconds: 3);

                    // Show warnings if any (e.g., duplicate headers)
                    foreach (var warning in result.Warnings)
                    {
                        _messageStore.EnqueueMessage(warning, MessageTypes.Warning, dismissAfterSeconds: 20);
                    }

                    // Notify about removed mappings
                    if (removedFields.Count > 0)
                    {
                        _messageStore.EnqueueMessage(
                            $"Removed {removedFields.Count} mapping(s) for fields no longer in template: {string.Join(", ", removedFields)}", MessageTypes.Warning, dismissAfterSeconds: 20);
                    }

                    // Phase 2: Reload the mappings display
                    // LoadFromMapper();
                }
                else
                {
                    // Show error message
                    _messageStore.EnqueueMessage(
                        $"Failed to refresh template: {result.Message}", MessageTypes.Error);

                    // Show detailed errors if available
                    foreach (var error in result.Errors)
                    {
                        _messageStore.EnqueueMessage(error, MessageTypes.Error);
                    }
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Unexpected error refreshing template: {ex.Message}", MessageTypes.Error);
            }
            finally
            {
                IsRefreshTemplateEnabled = !string.IsNullOrWhiteSpace(TemplateMetaDataFilePath) &&
                                          File.Exists(TemplateMetaDataFilePath);
            }
        }

        #endregion Commands

        #region Validation

        /// <summary>
        /// Validates the template file path
        /// Checks if file exists and has valid extension (CSV only)
        /// </summary>
        public static ValidationResult? ValidateTemplateFilePath(string? value, ValidationContext context)
        {
            var viewModel = context.ObjectInstance as AconexMetadataControlViewModel;
            if (viewModel == null)
                return ValidationResult.Success;

            // Can not be empty
            if (string.IsNullOrWhiteSpace(value))
                return new ValidationResult("Template file path is empty (null)");

            // Check if file exists
            if (!File.Exists(value))
                return new ValidationResult("Template file does not exist");

            // Check file extension (CSV only as per requirements)
            var extension = Path.GetExtension(value).ToLowerInvariant();
            if (extension != ".csv")
                return new ValidationResult("Template file must be a CSV (.csv) file");

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

            // load the metadata mappings
            LoadMappingsFromModel();
        }

        /// <summary>
        /// Loads template headers from the current template file
        /// Called automatically when template file path is set
        /// </summary>
        private async Task LoadTemplateHeadersAsync()
        {
            if (string.IsNullOrWhiteSpace(TemplateMetaDataFilePath))
                return;

            try
            {
                // Read the CSV headers
                var result = await _templateService.ReadColumnHeadersAsync(TemplateMetaDataFilePath);

                if (result.IsReadSuccessful)
                {
                    // Update available fields in the mapper
                    _aconexMapper.UpdateAvailableFields(result.ColumnHeaders);

                    // Show success message
                    _messageStore.EnqueueMessage(
                        $"Loaded {result.ColumnHeaders.Count} column headers from template", MessageTypes.Information, dismissAfterSeconds: 3);

                    // Show warnings if any (e.g., duplicate headers)
                    foreach (var warning in result.Warnings)
                    {
                        _messageStore.EnqueueMessage(warning, MessageTypes.Warning, dismissAfterSeconds: 20);
                    }
                }
                else
                {
                    // Show error message
                    _messageStore.EnqueueMessage(
                        $"Failed to read template: {result.Message}", MessageTypes.Error);

                    // Show detailed errors if available
                    foreach (var error in result.Errors)
                    {
                        _messageStore.EnqueueMessage(error, MessageTypes.Error);
                    }
                }
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Unexpected error reading template: {ex.Message}", MessageTypes.Error);
            }
        }

        ///// <summary>
        ///// Saves values back to the Aconex mapper instance
        ///// Called when configuration is saved
        ///// </summary>
        //public void SaveToMapper()
        //{
        //    if (_aconexMapper == null)
        //        return;

        //    // Template file path is already updated in property changed handler
        //    // Available fields are already updated in the mapper
        //    // No additional save logic needed for Phase 1

        //    // Phase 2: Save metadata mappings
        //    // _aconexMapper.ClearMappers();
        //    // foreach (var mapping in MetaDataMappings)
        //    // {
        //    //     _aconexMapper.AddMapper(mapping);
        //    // }
        //}

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