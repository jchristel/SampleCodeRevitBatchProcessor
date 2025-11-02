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
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;
using System.ComponentModel.DataAnnotations;

namespace duHastNet.DocManager.UI.Shared.ViewModels.CloudProviderControls
{
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
        /// Currently selected metadata field name from template
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Please select a metadata field")]
        private string? _selectedMetaFieldName;

        /// <summary>
        /// Indicates whether this mapping uses a static value (true) or document property (false)
        /// </summary>
        [ObservableProperty]
        private bool _isStaticValue = false;

        /// <summary>
        /// The static value to use (only if IsStaticValue is true)
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(MetaDataMappingDialogViewModel), nameof(ValidateStaticValue))]
        private string _staticValue = string.Empty;

        /// <summary>
        /// The selected document property name (only if IsStaticValue is false)
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(MetaDataMappingDialogViewModel), nameof(ValidateDocumentProperty))]
        private string? _selectedDocumentProperty;

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

            // Select first items as defaults
            if (AvailableMetaFields.Count > 0)
            {
                SelectedMetaFieldName = AvailableMetaFields[0];
            }

            if (AvailableDocumentProperties.Count > 0)
            {
                SelectedDocumentProperty = AvailableDocumentProperties[0];
            }
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

            // Determine if it's a static value or document property
            if (!string.IsNullOrWhiteSpace(_existingMapping.MetaFieldValue))
            {
                // Static value
                IsStaticValue = true;
                StaticValue = _existingMapping.MetaFieldValue;
            }
            else if (!string.IsNullOrWhiteSpace(_existingMapping.DocumentPropertyName))
            {
                // Document property
                IsStaticValue = false;
                SelectedDocumentProperty = _existingMapping.DocumentPropertyName;
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
        /// Called when IsStaticValue changes
        /// Triggers validation of relevant fields
        /// </summary>
        partial void OnIsStaticValueChanged(bool value)
        {
            // Clear validation for the field that's no longer relevant
            if (value)
            {
                // Using static value, clear document property validation
                ClearErrors(nameof(SelectedDocumentProperty));
            }
            else
            {
                // Using document property, clear static value validation
                ClearErrors(nameof(StaticValue));
            }

            // Trigger validation for the active field
            if (value)
            {
                ValidateProperty(StaticValue, nameof(StaticValue));
            }
            else
            {
                ValidateProperty(SelectedDocumentProperty, nameof(SelectedDocumentProperty));
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
                _messageStore.SetCurrentMessage(
                    "Please fix validation errors before continuing.", 
                    MessageTypes.Warning);
                return;
            }

            try
            {
                // Create the mapping
                var mapping = new MetaDataMap
                {
                    MetaFieldName = SelectedMetaFieldName,
                    MetaFieldValue = IsStaticValue ? StaticValue : null,
                    DocumentPropertyName = IsStaticValue ? null : SelectedDocumentProperty,
                    CloudServiceProviderName = "Aconex" // This is for Aconex integration
                };

                // Set the created mapping (this will trigger the view to close)
                CreatedMapping = mapping;
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
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

            // Must have either a static value or document property selected
            if (IsStaticValue)
            {
                return !string.IsNullOrWhiteSpace(StaticValue);
            }
            else
            {
                return !string.IsNullOrWhiteSpace(SelectedDocumentProperty);
            }
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
        /// Only required if IsStaticValue is true
        /// </summary>
        public static ValidationResult? ValidateStaticValue(string? value, ValidationContext context)
        {
            var viewModel = context.ObjectInstance as MetaDataMappingDialogViewModel;
            if (viewModel == null)
                return ValidationResult.Success;

            // Only validate if using static value mode
            if (viewModel.IsStaticValue && string.IsNullOrWhiteSpace(value))
            {
                return new ValidationResult("Static value is required");
            }

            return ValidationResult.Success;
        }

        /// <summary>
        /// Validates the document property selection
        /// Only required if IsStaticValue is false
        /// </summary>
        public static ValidationResult? ValidateDocumentProperty(string? value, ValidationContext context)
        {
            var viewModel = context.ObjectInstance as MetaDataMappingDialogViewModel;
            if (viewModel == null)
                return ValidationResult.Success;

            // Only validate if using document property mode
            if (!viewModel.IsStaticValue && string.IsNullOrWhiteSpace(value))
            {
                return new ValidationResult("Please select a document property");
            }

            return ValidationResult.Success;
        }

        #endregion Validation
    }
}
