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
using System.ComponentModel.DataAnnotations;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings.Database
{
    /// <summary>
    /// ViewModel for the Add Custom Field dialog
    /// Handles custom field name input with validation
    /// </summary>
    public partial class CustomFieldDialogViewModel : ObservableValidator
    {
        #region Private Fields

        private readonly DatabaseConnectionViewModel _parentViewModel;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// The custom field name being added
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Field name is required")]
        [CustomValidation(typeof(CustomFieldDialogViewModel), nameof(ValidateFieldName))]
        [NotifyCanExecuteChangedFor(nameof(OkCommand))]
        private string _fieldName = string.Empty;

        /// <summary>
        /// Dialog title
        /// </summary>
        public string DialogTitle => "Add Custom Field";

        /// <summary>
        /// The created field name (set when OK is clicked)
        /// </summary>
        [ObservableProperty]
        private string? _createdFieldName;

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
        /// <param name="parentViewModel">Parent ViewModel for duplicate checking</param>
        public CustomFieldDialogViewModel(DatabaseConnectionViewModel parentViewModel)
        {
            _parentViewModel = parentViewModel;
        }

        #endregion Constructor

        #region Property Changed Handlers

        /// <summary>
        /// Called when FieldName changes
        /// Triggers validation
        /// </summary>
        partial void OnFieldNameChanged(string value)
        {
            ValidateProperty(value, nameof(FieldName));
        }

        #endregion Property Changed Handlers

        #region Validation

        /// <summary>
        /// Custom validation for field name
        /// Validates format and checks for duplicates
        /// </summary>
        public static ValidationResult? ValidateFieldName(string? value, ValidationContext context)
        {
            var viewModel = (CustomFieldDialogViewModel)context.ObjectInstance;

            if (string.IsNullOrWhiteSpace(value))
                return new ValidationResult("Field name is required");

            // Trim the value for validation
            value = value.Trim();

            // Check length (max 100 characters as per DocManagerApi validation)
            if (value.Length > 100)
                return new ValidationResult("Field name cannot exceed 100 characters");

            // Check for problematic characters (as per DocManagerApi validation)
            if (value.Contains("\"") || value.Contains("'") || value.Contains(";"))
                return new ValidationResult("Field name cannot contain quotes or semicolons");

            // Check for duplicates (case-insensitive)
            if (viewModel._parentViewModel.IsDuplicateCustomField(value))
                return new ValidationResult($"Custom field '{value}' already exists");

            return ValidationResult.Success;
        }

        #endregion Validation

        #region Commands

        /// <summary>
        /// Determines if OK button should be enabled
        /// </summary>
        private bool CanExecuteOk()
        {
            // Must have no validation errors
            if (HasErrors)
                return false;

            // Field name is required
            if (string.IsNullOrWhiteSpace(FieldName))
                return false;

            return true;
        }

        /// <summary>
        /// Command to accept dialog (OK button)
        /// Creates the custom field name and sets CreatedFieldName
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanExecuteOk))]
        private void Ok()
        {
            // Final validation
            ValidateAllProperties();

            if (HasErrors)
                return;

            // Trim the field name before creating
            CreatedFieldName = FieldName.Trim();

            // Close the dialog with DialogResult = true
            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        /// <summary>
        /// Command to cancel dialog (Cancel button)
        /// </summary>
        [RelayCommand]
        private void Cancel()
        {
            // Close the dialog with DialogResult = false
            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        #endregion Commands
    }
}
