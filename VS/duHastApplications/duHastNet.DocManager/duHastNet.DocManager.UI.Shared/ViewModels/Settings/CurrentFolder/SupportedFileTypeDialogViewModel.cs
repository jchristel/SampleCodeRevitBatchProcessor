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
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder.ModifierControls;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder
{
    /// <summary>
    /// Enumeration of modifier types for dropdown selection
    /// </summary>
    public enum ModifierType
    {
        None,
        AddSuffix,
        AddPrefix,
        AddAtIndex,
        Replace
    }

    /// <summary>
    /// ViewModel for the Add/Edit Supported File Type dialog
    /// Handles file extension, description, and dynamic modifier control selection
    /// </summary>
    public partial class SupportedFileTypeDialogViewModel : ObservableValidator
    {
        #region Private Fields

        private readonly IDialogService _dialogService;
        private readonly Settings.CurrentFolder.CurrentFolderViewModel _parentViewModel;
        private readonly bool _isEditMode;
        private readonly int? _editIndex;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// File extension (e.g., ".pdf", ".dwg")
        /// Validated for format, uniqueness, and required
        /// </summary>
        [ObservableProperty]
        [CustomValidation(typeof(SupportedFileTypeDialogViewModel), nameof(ValidateFileExtension))]
        [NotifyCanExecuteChangedFor(nameof(OkCommand))]
        private string _fileExtension = string.Empty;

        /// <summary>
        /// Description of the file type (e.g., "PDF Document")
        /// </summary>
        [ObservableProperty]
        [Required(ErrorMessage = "Description is required")]
        [NotifyCanExecuteChangedFor(nameof(OkCommand))]
        private string _description = string.Empty;

        /// <summary>
        /// Currently selected modifier type from dropdown
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(OkCommand))]
        private ModifierType _selectedModifierType = ModifierType.None;

        /// <summary>
        /// The current modifier control ViewModel (dynamically switched based on SelectedModifierType)
        /// </summary>
        [ObservableProperty]
        private ObservableObject? _currentModifierControl;

        /// <summary>
        /// The created or edited file type (set when OK is clicked)
        /// </summary>
        [ObservableProperty]
        private SupportedFileType? _createdFileType;

        /// <summary>
        /// Available modifier types for the dropdown
        /// </summary>
        public ObservableCollection<ModifierType> AvailableModifierTypes { get; }

        /// <summary>
        /// Dialog title (changes based on Add/Edit mode)
        /// </summary>
        public string DialogTitle => _isEditMode ? "Edit File Type" : "Add File Type";

        /// <summary>
        /// Indicates if file extension field should be enabled
        /// Disabled in edit mode for PDF (protected)
        /// </summary>
        public bool IsFileExtensionEnabled => !(_isEditMode && IsPdfEditMode);

        /// <summary>
        /// Indicates if we're editing the PDF file type
        /// </summary>
        private bool IsPdfEditMode => _isEditMode && _editIndex.HasValue && _parentViewModel.IsPdfFileType(_editIndex.Value);

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
        public SupportedFileTypeDialogViewModel(
            Settings.CurrentFolder.CurrentFolderViewModel parentViewModel,
            IDialogService dialogService)
        {
            _parentViewModel = parentViewModel ?? throw new ArgumentNullException(nameof(parentViewModel));
            _dialogService = dialogService ?? throw new ArgumentNullException(nameof(dialogService));
            _isEditMode = false;
            _editIndex = null;

            // Initialize available modifier types
            AvailableModifierTypes =
            [
                ModifierType.None,
                ModifierType.AddSuffix,
                ModifierType.AddPrefix,
                ModifierType.AddAtIndex,
                ModifierType.Replace
            ];

            // Default to None
            SelectedModifierType = ModifierType.None;
        }

        /// <summary>
        /// Constructor for Edit mode
        /// </summary>
        public SupportedFileTypeDialogViewModel(
            Settings.CurrentFolder.CurrentFolderViewModel parentViewModel,
            IDialogService dialogService,
            SupportedFileType existingFileType,
            int editIndex)
            : this(parentViewModel, dialogService)
        {
            _isEditMode = true;
            _editIndex = editIndex;

            // Load existing values
            LoadExistingFileType(existingFileType);
        }

        #endregion Constructor

        #region Property Changed Handlers

        /// <summary>
        /// Handles when SelectedModifierType changes
        /// Swaps out the current modifier control ViewModel
        /// </summary>
        partial void OnSelectedModifierTypeChanged(ModifierType value)
        {
            // Unsubscribe from old control if it exists
            if (CurrentModifierControl is INotifyPropertyChanged oldControl)
            {
                oldControl.PropertyChanged -= OnModifierControlPropertyChanged;
            }

            // Create appropriate control ViewModel based on selected type
            CurrentModifierControl = value switch
            {
                ModifierType.None => null,
                ModifierType.AddSuffix => new AddSuffixControlViewModel(),
                ModifierType.AddPrefix => new AddPrefixControlViewModel(),
                ModifierType.AddAtIndex => new AddAtIndexControlViewModel(),
                ModifierType.Replace => new ReplaceControlViewModel(),
                _ => null
            };

            // Subscribe to new control's PropertyChanged to monitor validation state
            if (CurrentModifierControl is INotifyPropertyChanged newControl)
            {
                newControl.PropertyChanged += OnModifierControlPropertyChanged;
            }

            // Notify that OK command's CanExecute state may have changed
            OkCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Handles when the nested modifier control's properties change
        /// Notifies the OK command that its CanExecute state should be re-evaluated
        /// </summary>
        private void OnModifierControlPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            // When any property changes in the nested control (including validation state),
            // notify that OK command should re-check if it can execute
            OkCommand.NotifyCanExecuteChanged();
        }

        /// <summary>
        /// Handles when FileExtension changes
        /// Auto-formats: trim, lowercase, add period if missing
        /// </summary>
        partial void OnFileExtensionChanged(string value)
        {
            if (!string.IsNullOrWhiteSpace(value))
            {
                var formatted = value.Trim().ToLowerInvariant();

                // Auto-add period if missing
                if (!formatted.StartsWith("."))
                    formatted = "." + formatted;

                // Update if different (avoid infinite loop)
                if (formatted != value)
                {
                    FileExtension = formatted;
                    return; // Don't validate yet, will validate after update
                }
            }

            // Validate
            ValidateProperty(value, nameof(FileExtension));
        }

        #endregion Property Changed Handlers

        #region Validation

        /// <summary>
        /// Custom validation for file extension
        /// Checks format, uniqueness, and required
        /// </summary>
        public static ValidationResult? ValidateFileExtension(string? value, ValidationContext context)
        {
            if (context.ObjectInstance is not SupportedFileTypeDialogViewModel viewModel)
                return ValidationResult.Success;

            // Required
            if (string.IsNullOrWhiteSpace(value))
                return new ValidationResult("File extension is required");

            // Must start with period
            if (!value.StartsWith("."))
                return new ValidationResult("File extension must start with a period (e.g., .pdf)");

            // Must have characters after period
            if (value.Length <= 1)
                return new ValidationResult("File extension must have characters after the period");

            // Valid characters only (alphanumeric + period)
            if (!Regex.IsMatch(value, @"^\.[a-zA-Z0-9]+$"))
                return new ValidationResult("File extension contains invalid characters. Use only letters and numbers.");

            // Check for duplicates (case-insensitive)
            if (viewModel._parentViewModel.IsDuplicateFileExtension(value, viewModel._editIndex))
                return new ValidationResult($"File type '{value}' already exists");

            return ValidationResult.Success;
        }

        #endregion Validation

        #region Commands

        /// <summary>
        /// Determines if OK button should be enabled
        /// This method must be read-only and not trigger any validation
        /// </summary>
        private bool CanExecuteOk()
        {
            // Must have no validation errors in main properties
            if (HasErrors)
                return false;

            // File extension required
            if (string.IsNullOrWhiteSpace(FileExtension))
                return false;

            // Description required
            if (string.IsNullOrWhiteSpace(Description))
                return false;

            // If a modifier is selected, check if the control has validation errors
            if (SelectedModifierType != ModifierType.None && CurrentModifierControl != null)
            {
                // Check HasErrors property directly (read-only, no side effects)
                // All modifier controls inherit from ObservableValidator which has HasErrors
                var hasErrors = CurrentModifierControl switch
                {
                    ObservableValidator validator => validator.HasErrors,
                    _ => false
                };

                if (hasErrors)
                    return false;
            }

            return true;
        }

        /// <summary>
        /// Command to accept dialog (OK button)
        /// Creates the file type and sets CreatedFileType
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanExecuteOk))]
        private void Ok()
        {
            // Final validation of main properties
            ValidateAllProperties();

            if (HasErrors)
                return;

            // Check modifier control validation state if present
            if (CurrentModifierControl != null)
            {
                var hasErrors = CurrentModifierControl switch
                {
                    ObservableValidator validator => validator.HasErrors,
                    _ => false
                };

                if (hasErrors)
                    return;
            }

            // Create the modifier (null if None selected)
            IDocumentNumberModifier? modifier = CreateModifier();

            // Create the file type
            CreatedFileType = new SupportedFileType(
                fileExtension: FileExtension,
                description: Description,
                documentNumberModifier: modifier
            );

            // Dialog will close with DialogResult = true via PropertyChanged event
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
        /// Loads values from an existing file type (Edit mode)
        /// </summary>
        private void LoadExistingFileType(SupportedFileType fileType)
        {
            FileExtension = fileType.FileExtension;
            Description = fileType.Description;

            // Load modifier
            var modifier = fileType.DocumentNumberModifier;

            if (modifier == null)
            {
                SelectedModifierType = ModifierType.None;
            }
            else
            {
                // Determine type and load appropriate control
                switch (modifier)
                {
                    case AddToEnd addToEnd:
                        SelectedModifierType = ModifierType.AddSuffix;
                        CurrentModifierControl = new AddSuffixControlViewModel(addToEnd);
                        break;

                    case AddAtIndex addAtIndex:
                        // Check if it's a prefix (index 0) or custom index
                        var indexField = typeof(AddAtIndex).GetField(
                            "_index",
                            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                        var index = indexField != null ? (int)(indexField.GetValue(addAtIndex) ?? 0) : 0;

                        if (index == 0)
                        {
                            SelectedModifierType = ModifierType.AddPrefix;
                            CurrentModifierControl = new AddPrefixControlViewModel(addAtIndex);
                        }
                        else
                        {
                            SelectedModifierType = ModifierType.AddAtIndex;
                            CurrentModifierControl = new AddAtIndexControlViewModel(addAtIndex);
                        }
                        break;

                    case Replace replace:
                        SelectedModifierType = ModifierType.Replace;
                        CurrentModifierControl = new ReplaceControlViewModel(replace);
                        break;

                    default:
                        SelectedModifierType = ModifierType.None;
                        break;
                }
            }
        }

        /// <summary>
        /// Creates a modifier from the current control ViewModel
        /// Returns null if None is selected
        /// </summary>
        private IDocumentNumberModifier? CreateModifier()
        {
            if (SelectedModifierType == ModifierType.None || CurrentModifierControl == null)
                return null;

            return SelectedModifierType switch
            {
                ModifierType.AddSuffix => ((AddSuffixControlViewModel)CurrentModifierControl).CreateModifier(),
                ModifierType.AddPrefix => ((AddPrefixControlViewModel)CurrentModifierControl).CreateModifier(),
                ModifierType.AddAtIndex => ((AddAtIndexControlViewModel)CurrentModifierControl).CreateModifier(),
                ModifierType.Replace => ((ReplaceControlViewModel)CurrentModifierControl).CreateModifier(),
                _ => null
            };
        }

        #endregion Helper Methods
    }
}