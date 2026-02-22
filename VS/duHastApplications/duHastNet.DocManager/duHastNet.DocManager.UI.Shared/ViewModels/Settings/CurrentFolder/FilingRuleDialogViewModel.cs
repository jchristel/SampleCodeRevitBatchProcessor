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
using duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.DocManager.UI.Shared.Validators;
using System.Collections.ObjectModel;
using System.ComponentModel.DataAnnotations;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder
{
    /// <summary>
    /// ViewModel for the Add/Edit Filing Rule dialog
    /// Handles both adding new rules and editing existing rules
    /// </summary>
    public partial class FilingRuleDialogViewModel : ObservableValidator
    {
        #region Private Fields

        private readonly IDialogService _dialogService;
        private readonly Settings.CurrentFolder.CurrentFolderViewModel _parentViewModel;
        private readonly int? _editIndex;
        private readonly bool _isEditMode;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// Available filing rule types for the dropdown
        /// </summary>
        public ObservableCollection<FilingRuleType> AvailableRuleTypes { get; }

        /// <summary>
        /// Currently selected rule type
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(IsFilterValueEnabled))]
        [NotifyCanExecuteChangedFor(nameof(OkCommand))]
        private FilingRuleType _selectedRuleType;

        /// <summary>
        /// Filter value for the rule (disabled for CatchAll)
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(FilingRuleDialogViewModel), nameof(ValidateFilterValue))]
        [NotifyCanExecuteChangedFor(nameof(OkCommand))]
        private string _filterValue = string.Empty;

        /// <summary>
        /// Target directory path where matched files will be moved
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(FolderPathValidator), nameof(FolderPathValidator.ValidateFolderExists))]
        [Required(ErrorMessage = "Target path is required")]
        [NotifyCanExecuteChangedFor(nameof(OkCommand))]
        private string _targetPath = string.Empty;

        /// <summary>
        /// Whether the filter value textbox should be enabled
        /// Disabled for CatchAll/Default rule type
        /// </summary>
        public bool IsFilterValueEnabled => SelectedRuleType != FilingRuleType.Default;

        /// <summary>
        /// Dialog title (changes based on Add/Edit mode)
        /// </summary>
        public string DialogTitle => _isEditMode ? "Edit Filing Rule" : "Add Filing Rule";

        /// <summary>
        /// The created or edited rule (set when OK is clicked)
        /// </summary>
        [ObservableProperty]
        private IFilingRule? _createdRule;

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
        public FilingRuleDialogViewModel(
            IDialogService dialogService,
            Settings.CurrentFolder.CurrentFolderViewModel parentViewModel)
        {
            _dialogService = dialogService;
            _parentViewModel = parentViewModel;
            _isEditMode = false;
            _editIndex = null;

            // Initialize available rule types
            AvailableRuleTypes =
            [
                FilingRuleType.BeginsWith,
                FilingRuleType.Contains,
                FilingRuleType.NotBeginsWith,
                FilingRuleType.NotContains,
                FilingRuleType.Default
            ];

            // Default selection
            SelectedRuleType = FilingRuleType.BeginsWith;
        }

        /// <summary>
        /// Constructor for Edit mode
        /// </summary>
        public FilingRuleDialogViewModel(
            IDialogService dialogService,
            Settings.CurrentFolder.CurrentFolderViewModel parentViewModel,
            IFilingRule existingRule,
            int editIndex)
            : this(dialogService, parentViewModel)
        {
            _isEditMode = true;
            _editIndex = editIndex;

            // Pre-populate fields from existing rule
            LoadExistingRule(existingRule);
        }

        #endregion Constructor

        #region Initialization

        /// <summary>
        /// Loads an existing rule's values into the dialog fields
        /// </summary>
        private void LoadExistingRule(IFilingRule rule)
        {
            // Determine rule type
            SelectedRuleType = rule switch
            {
                BeginsWith => FilingRuleType.BeginsWith,
                Contains => FilingRuleType.Contains,
                NotBeginsWith => FilingRuleType.NotBeginsWith,
                NotContains => FilingRuleType.NotContains,
                CatchAll => FilingRuleType.Default,
                _ => FilingRuleType.BeginsWith
            };

            // Load values
            FilterValue = rule.ComparisonValue ?? string.Empty;
            TargetPath = rule.TargetDirectory ?? string.Empty;

            // Validate loaded values
            ValidateAllProperties();
        }

        #endregion Initialization

        #region Property Changed Handlers

        /// <summary>
        /// Called when SelectedRuleType changes
        /// Clears filter value when switching to CatchAll
        /// </summary>
        partial void OnSelectedRuleTypeChanged(FilingRuleType value)
        {
            if (value == FilingRuleType.Default)
            {
                // CatchAll doesn't use filter value
                FilterValue = string.Empty;
            }

            // Re-validate filter value with new rule type
            ValidateProperty(FilterValue, nameof(FilterValue));
        }

        /// <summary>
        /// Called when FilterValue changes
        /// Triggers validation
        /// </summary>
        partial void OnFilterValueChanged(string value)
        {
            ValidateProperty(value, nameof(FilterValue));
        }

        /// <summary>
        /// Called when TargetPath changes
        /// Triggers validation
        /// </summary>
        partial void OnTargetPathChanged(string value)
        {
            ValidateProperty(value, nameof(TargetPath));
        }

        #endregion Property Changed Handlers

        #region Validation

        /// <summary>
        /// Custom validation for filter value
        /// Required for non-CatchAll rules, validates duplicates
        /// </summary>
        public static ValidationResult? ValidateFilterValue(string? value, ValidationContext context)
        {
            if (context.ObjectInstance is not FilingRuleDialogViewModel viewModel)
                return ValidationResult.Success;

            // CatchAll doesn't need filter value
            if (viewModel.SelectedRuleType == FilingRuleType.Default)
                return ValidationResult.Success;

            // Filter value is required for non-CatchAll rules
            if (string.IsNullOrWhiteSpace(value))
                return new ValidationResult("Filter value is required");

            // Check for duplicate (same type + same value)
            if (viewModel._parentViewModel.IsDuplicateRule(
                viewModel.SelectedRuleType,
                value,
                viewModel._editIndex))
            {
                return new ValidationResult($"A rule with type '{viewModel.GetRuleTypeDisplayName()}' and value '{value}' already exists");
            }

            return ValidationResult.Success;
        }

        /// <summary>
        /// Additional validation for CatchAll uniqueness
        /// </summary>
        private bool ValidateCatchAllUniqueness()
        {
            if (SelectedRuleType == FilingRuleType.Default)
            {
                // Check if another CatchAll already exists (excluding self in edit mode)
                if (_parentViewModel.CatchAllRuleExists(_editIndex))
                {
                    return false;
                }
            }
            return true;
        }

        /// <summary>
        /// Gets display name for current rule type
        /// </summary>
        private string GetRuleTypeDisplayName()
        {
            return SelectedRuleType switch
            {
                FilingRuleType.BeginsWith => "Begins With",
                FilingRuleType.Contains => "Contains",
                FilingRuleType.NotBeginsWith => "Not Begins With",
                FilingRuleType.NotContains => "Not Contains",
                FilingRuleType.Default => "Default",
                _ => SelectedRuleType.ToString()
            };
        }

        #endregion Validation

        #region Commands

        /// <summary>
        /// Command to browse for target folder
        /// </summary>
        [RelayCommand]
        private void BrowseTargetPath()
        {
            try
            {
                var selectedPath = _dialogService.ShowFolderBrowserDialog(
                    "Select Target Folder",
                    TargetPath);

                if (!string.IsNullOrEmpty(selectedPath))
                {
                    TargetPath = selectedPath;
                }
            }
            catch (Exception ex)
            {
                // Could show error in a message box or status
                System.Diagnostics.Debug.WriteLine($"Error browsing for folder: {ex.Message}");
            }
        }

        /// <summary>
        /// Determines if OK button should be enabled
        /// </summary>
        private bool CanExecuteOk()
        {
            // Must have no validation errors
            if (HasErrors)
                return false;

            // For CatchAll, check uniqueness
            if (SelectedRuleType == FilingRuleType.Default)
            {
                if (!ValidateCatchAllUniqueness())
                    return false;
            }

            // Target path is required
            if (string.IsNullOrWhiteSpace(TargetPath))
                return false;

            // Filter value required for non-CatchAll
            if (SelectedRuleType != FilingRuleType.Default && string.IsNullOrWhiteSpace(FilterValue))
                return false;

            return true;
        }

        /// <summary>
        /// Command to accept dialog (OK button)
        /// Creates the rule and sets DialogResult to true
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanExecuteOk))]
        private void Ok()
        {
            // Final validation
            ValidateAllProperties();

            if (HasErrors)
                return;

            // Check CatchAll uniqueness one more time
            if (!ValidateCatchAllUniqueness())
            {
                // This shouldn't happen if CanExecute is working, but be safe
                return;
            }

            // Create the appropriate rule based on type
            CreatedRule = CreateRule();

            // Dialog will close with DialogResult = true
            // This is handled in code-behind
        }

        /// <summary>
        /// Command to cancel dialog (Cancel button)
        /// Requests the view to close with DialogResult = false
        /// </summary>
        [RelayCommand]
        private void Cancel()
        {
            // Raise event to request window close
            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        #endregion Commands

        #region Helper Methods

        /// <summary>
        /// Creates the concrete IFilingRule instance based on selected type and values
        /// </summary>
        private IFilingRule CreateRule()
        {
            return SelectedRuleType switch
            {
                FilingRuleType.BeginsWith => new BeginsWith(FilterValue, TargetPath),
                FilingRuleType.Contains => new Contains(FilterValue, TargetPath),
                FilingRuleType.NotBeginsWith => new NotBeginsWith(FilterValue, TargetPath),
                FilingRuleType.NotContains => new NotContains(FilterValue, TargetPath),
                FilingRuleType.Default => new CatchAll(string.Empty, TargetPath),
                _ => throw new InvalidOperationException($"Unknown rule type: {SelectedRuleType}")
            };
        }

        #endregion Helper Methods
    }
}