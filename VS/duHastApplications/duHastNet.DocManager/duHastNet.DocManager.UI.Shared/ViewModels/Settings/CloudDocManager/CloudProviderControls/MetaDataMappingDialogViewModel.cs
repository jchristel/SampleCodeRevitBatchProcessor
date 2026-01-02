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
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;
using System.ComponentModel.DataAnnotations;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;

namespace duHastNet.DocManager.UI.Shared.ViewModels.CloudProviderControls
{
    /// <summary>
    /// Enumeration for mapping source types
    /// </summary>
    public enum MappingSourceType
    {
        /// <summary>
        /// Map to a document property (Number, Name, Revision, or custom field)
        /// </summary>
        DocumentProperty,

        /// <summary>
        /// Use a static/fixed value
        /// </summary>
        StaticValue,

        /// <summary>
        /// Map to a file property (e.g., FileName)
        /// </summary>
        FileProperty
    }

    /// <summary>
    /// ViewModel for the MetaDataMapping dialog
    /// Handles adding and editing metadata field mappings
    /// </summary>
    public partial class MetaDataMappingDialogViewModel : ObservableValidator
    {
        #region Private Fields

        private readonly MessageStore _messageStore;
        private readonly bool _isEditMode;
        private readonly MetaDataMap? _existingMapping;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// Available metadata fields from the template (unmapped fields for Add mode, all fields for Edit mode)
        /// </summary>
        public ObservableCollection<string> AvailableMetaFields { get; }

        /// <summary>
        /// Available document properties for mapping
        /// Includes standard properties (Number, Name, Revision) and custom fields
        /// </summary>
        public ObservableCollection<string> AvailableDocumentProperties { get; }

        /// <summary>
        /// Available file properties for mapping
        /// </summary>
        public ObservableCollection<string> AvailableFileProperties { get; }

        /// <summary>
        /// Currently selected metadata field name from template
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Please select a metadata field")]
        private string? _selectedMetaFieldName;

        /// <summary>
        /// The selected mapping source type (DocumentProperty, StaticValue, or FileProperty)
        /// </summary>
        [ObservableProperty]
        private MappingSourceType _selectedMappingSource = MappingSourceType.DocumentProperty;

        /// <summary>
        /// The static value to use (only if SelectedMappingSource is StaticValue)
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(MetaDataMappingDialogViewModel), nameof(ValidateStaticValue))]
        private string _staticValue = string.Empty;

        /// <summary>
        /// The selected document property name (only if SelectedMappingSource is DocumentProperty)
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(MetaDataMappingDialogViewModel), nameof(ValidateDocumentProperty))]
        private string? _selectedDocumentProperty;

        /// <summary>
        /// The selected file property name (only if SelectedMappingSource is FileProperty)
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(MetaDataMappingDialogViewModel), nameof(ValidateFileProperty))]
        private string? _selectedFileProperty;

        /// <summary>
        /// Dialog title (Add or Edit)
        /// </summary>
        public string DialogTitle => _isEditMode ? "Edit Metadata Mapping" : "Add Metadata Mapping";

        /// <summary>
        /// The created or edited mapping (set when OK is clicked)
        /// </summary>
        [ObservableProperty]
        private MetaDataMap? _createdMapping;

        #endregion Observable Properties

        #region Events

        /// <summary>
        /// Event raised when the ViewModel requests the view to close
        /// </summary>
        public event EventHandler? RequestClose;

        #endregion Events

        #region Constructor

        /// <summary>
        /// Constructor for Add mode
        /// </summary>
        /// <param name="availableMetaFields">List of unmapped metadata fields from template</param>
        /// <param name="availableDocumentProperties">List of available document properties</param>
        /// <param name="messageStore">Message store for displaying messages</param>
        public MetaDataMappingDialogViewModel(
            List<string> availableMetaFields,
            List<string> availableDocumentProperties,
            MessageStore messageStore)
        {
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
            _isEditMode = false;
            _existingMapping = null;

            // Initialize collections
            AvailableMetaFields = new ObservableCollection<string>(availableMetaFields ?? throw new ArgumentNullException(nameof(availableMetaFields)));
            AvailableDocumentProperties = new ObservableCollection<string>(availableDocumentProperties ?? throw new ArgumentNullException(nameof(availableDocumentProperties)));
            
            // Initialize file properties collection
            AvailableFileProperties = new ObservableCollection<string>(
                FilePropertyProvider.GetAvailableFileProperties()
            );

            // Select first items as defaults
            if (AvailableMetaFields.Count > 0)
            {
                SelectedMetaFieldName = AvailableMetaFields[0];
            }

            if (AvailableDocumentProperties.Count > 0)
            {
                SelectedDocumentProperty = AvailableDocumentProperties[0];
            }

            if (AvailableFileProperties.Count > 0)
            {
                SelectedFileProperty = AvailableFileProperties[0];
            }

            // Explicitly set default selection and force UI update
            SelectedMappingSource = MappingSourceType.DocumentProperty;
            OnPropertyChanged(nameof(SelectedMappingSource));
        }

        /// <summary>
        /// Constructor for Edit mode
        /// </summary>
        /// <param name="availableMetaFields">List of all metadata fields from template</param>
        /// <param name="availableDocumentProperties">List of available document properties</param>
        /// <param name="existingMapping">The existing mapping to edit</param>
        /// <param name="messageStore">Message store for displaying messages</param>
        public MetaDataMappingDialogViewModel(
            List<string> availableMetaFields,
            List<string> availableDocumentProperties,
            MetaDataMap existingMapping,
            MessageStore messageStore)
            : this(availableMetaFields, availableDocumentProperties, messageStore)
        {
            _isEditMode = true;
            _existingMapping = existingMapping ?? throw new ArgumentNullException(nameof(existingMapping));

            // Load existing values
            LoadExistingMapping();
        }

        #endregion Constructor

        #region Initialization

        /// <summary>
        /// Loads an existing mapping's values into the dialog fields
        /// </summary>
        private void LoadExistingMapping()
        {
            if (_existingMapping == null)
                return;

            // Set the metadata field name
            SelectedMetaFieldName = _existingMapping.MetaFieldName;

            // Determine mapping source type and set appropriate values
            if (!string.IsNullOrWhiteSpace(_existingMapping.MetaFieldValue))
            {
                // Static value
                SelectedMappingSource = MappingSourceType.StaticValue;
                StaticValue = _existingMapping.MetaFieldValue;
            }
            else if (!string.IsNullOrWhiteSpace(_existingMapping.DocumentPropertyName))
            {
                // Document property
                SelectedMappingSource = MappingSourceType.DocumentProperty;
                SelectedDocumentProperty = _existingMapping.DocumentPropertyName;
            }
            else if (!string.IsNullOrWhiteSpace(_existingMapping.FilePropertyName))
            {
                // File property
                SelectedMappingSource = MappingSourceType.FileProperty;
                SelectedFileProperty = _existingMapping.FilePropertyName;
            }
        }

        #endregion Initialization

        #region Property Changed Handlers

        /// <summary>
        /// Called when SelectedMetaFieldName changes
        /// Triggers validation
        /// </summary>
        partial void OnSelectedMetaFieldNameChanged(string? value)
        {
            ValidateProperty(value, nameof(SelectedMetaFieldName));
            OkCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Called when SelectedMappingSource changes
        /// Triggers validation of relevant fields
        /// </summary>
        partial void OnSelectedMappingSourceChanged(MappingSourceType value)
        {
            // Clear validation for fields that are no longer relevant
            ClearErrors(nameof(StaticValue));
            ClearErrors(nameof(SelectedDocumentProperty));
            ClearErrors(nameof(SelectedFileProperty));

            // Trigger validation for the active field
            switch (value)
            {
                case MappingSourceType.StaticValue:
                    ValidateProperty(StaticValue, nameof(StaticValue));
                    break;
                case MappingSourceType.DocumentProperty:
                    ValidateProperty(SelectedDocumentProperty, nameof(SelectedDocumentProperty));
                    break;
                case MappingSourceType.FileProperty:
                    ValidateProperty(SelectedFileProperty, nameof(SelectedFileProperty));
                    break;
            }

            OkCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Called when StaticValue changes
        /// Triggers validation
        /// </summary>
        partial void OnStaticValueChanged(string value)
        {
            ValidateProperty(value, nameof(StaticValue));
            OkCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Called when SelectedDocumentProperty changes
        /// Triggers validation
        /// </summary>
        partial void OnSelectedDocumentPropertyChanged(string? value)
        {
            ValidateProperty(value, nameof(SelectedDocumentProperty));
            OkCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Called when SelectedFileProperty changes
        /// Triggers validation
        /// </summary>
        partial void OnSelectedFilePropertyChanged(string? value)
        {
            ValidateProperty(value, nameof(SelectedFileProperty));
            OkCommand.NotifyCanExecuteChanged();
        }

        #endregion Property Changed Handlers

        #region Commands

        /// <summary>
        /// Command to confirm and create/update the mapping
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanExecuteOk))]
        private void Ok()
        {
            // Validate all properties
            ValidateAllProperties();

            if (HasErrors)
            {
                _messageStore.EnqueueMessage(
                    "Please fix validation errors before continuing.", 
                    MessageTypes.Warning, dismissAfterSeconds: 20);
                return;
            }

            try
            {
                // Create the mapping based on selected source type
                var mapping = new MetaDataMap
                {
                    MetaFieldName = SelectedMetaFieldName,
                    MetaFieldValue = SelectedMappingSource == MappingSourceType.StaticValue ? StaticValue : null,
                    DocumentPropertyName = SelectedMappingSource == MappingSourceType.DocumentProperty ? SelectedDocumentProperty : null,
                    FilePropertyName = SelectedMappingSource == MappingSourceType.FileProperty ? SelectedFileProperty : null,
                    CloudServiceProviderName = "Aconex" // This is for Aconex integration
                };

                // Set the created mapping (this will trigger the view to close)
                CreatedMapping = mapping;
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Failed to create mapping: {ex.Message}", 
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if the OK command can execute
        /// </summary>
        private bool CanExecuteOk()
        {
            // Must have a selected metadata field
            if (string.IsNullOrWhiteSpace(SelectedMetaFieldName))
                return false;

            // Must have appropriate value based on selected source type
            return SelectedMappingSource switch
            {
                MappingSourceType.StaticValue => !string.IsNullOrWhiteSpace(StaticValue),
                MappingSourceType.DocumentProperty => !string.IsNullOrWhiteSpace(SelectedDocumentProperty),
                MappingSourceType.FileProperty => !string.IsNullOrWhiteSpace(SelectedFileProperty),
                _ => false,
            };
        }

        /// <summary>
        /// Command to cancel the dialog
        /// </summary>
        [RelayCommand]
        private void Cancel()
        {
            CreatedMapping = null;
            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        #endregion Commands

        #region Validation

        /// <summary>
        /// Validates the static value
        /// Only required if SelectedMappingSource is StaticValue
        /// </summary>
        public static ValidationResult? ValidateStaticValue(string? value, ValidationContext context)
        {
            if (context.ObjectInstance is not MetaDataMappingDialogViewModel viewModel)
            {
                return ValidationResult.Success;
            }

            // Only validate if using static value mode
            if (viewModel.SelectedMappingSource == MappingSourceType.StaticValue && string.IsNullOrWhiteSpace(value))
            {
                return new ValidationResult("Static value is required");
            }

            return ValidationResult.Success;
        }

        /// <summary>
        /// Validates the document property selection
        /// Only required if SelectedMappingSource is DocumentProperty
        /// </summary>
        public static ValidationResult? ValidateDocumentProperty(string? value, ValidationContext context)
        {
            if (context.ObjectInstance is not MetaDataMappingDialogViewModel viewModel)
            {
                return ValidationResult.Success;
            }

            // Only validate if using document property mode
            if (viewModel.SelectedMappingSource == MappingSourceType.DocumentProperty && string.IsNullOrWhiteSpace(value))
            {
                return new ValidationResult("Please select a document property");
            }

            return ValidationResult.Success;
        }

        /// <summary>
        /// Validates the file property selection
        /// Only required if SelectedMappingSource is FileProperty
        /// </summary>
        public static ValidationResult? ValidateFileProperty(string? value, ValidationContext context)
        {
            if (context.ObjectInstance is not MetaDataMappingDialogViewModel viewModel)
            {
                return ValidationResult.Success;
            }

            // Only validate if using file property mode
            if (viewModel.SelectedMappingSource == MappingSourceType.FileProperty && string.IsNullOrWhiteSpace(value))
            {
                return new ValidationResult("Please select a file property");
            }

            return ValidationResult.Success;
        }

        #endregion Validation
    }
}
