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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CloudDocManager;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings.CloudDocManager
{
    /// <summary>
    /// ViewModel for Cloud Document Manager configuration
    /// Handles provider selection and dynamic control switching
    /// Follows the same pattern as SupportedFileTypeDialogViewModel for modifier controls
    /// Implements validation and error propagation from nested child ViewModels
    /// </summary>
    public partial class CloudDocumentManagerViewModel : ObservableValidator
    {
        #region Private Fields

        private readonly MessageStore _messageStore;
        private readonly Manager _manager;
        private readonly IDialogService _dialogService;
        private readonly CloudDocumentManager _cloudDocumentManager;

        #endregion Private Fields

        #region Observable Properties

        /// <summary>
        /// Indicates whether cloud document manager integration is enabled
        /// When false, all provider controls are disabled/collapsed
        /// </summary>
        [ObservableProperty]
        private bool _cloudDocumentManagerEnabled = false;

        /// <summary>
        /// Currently selected cloud provider type from dropdown
        /// </summary>
        [ObservableProperty]
        private CloudProviderType _selectedProviderType = CloudProviderType.None;

        /// <summary>
        /// The current provider control ViewModel (dynamically switched based on SelectedProviderType)
        /// </summary>
        [ObservableProperty]
        private ObservableObject? _currentProviderControl;

        /// <summary>
        /// Available provider types for the dropdown
        /// </summary>
        public ObservableCollection<CloudProviderType> AvailableProviderTypes { get; }

        #endregion Observable Properties

        #region Computed Properties for Error Aggregation

        /// <summary>
        /// Gets whether this ViewModel has validation errors
        /// This includes both own validation rules and child control validation
        /// Overrides the base HasErrors to include child validation state
        /// </summary>
        public bool HasValidationErrors
        {
            get
            {
                // If disabled, no errors
                if (!CloudDocumentManagerEnabled)
                    return false;

                // Check if enabled but no provider selected
                if (SelectedProviderType == CloudProviderType.None)
                    return true;

                // Check if control should exist but doesn't
                if (CurrentProviderControl == null)
                    return true;

                // Check if child control has errors
                if (CurrentProviderControl is ObservableValidator childValidator)
                {
                    return childValidator.HasErrors;
                }

                return false;
            }
        }

        /// <summary>
        /// Gets the count of validation errors for display purposes
        /// </summary>
        public int ErrorCount
        {
            get
            {
                int count = 0;

                if (!CloudDocumentManagerEnabled)
                    return 0;

                if (SelectedProviderType == CloudProviderType.None)
                    count++;

                if (CurrentProviderControl == null)
                    count++;

                if (CurrentProviderControl is ObservableValidator childValidator && childValidator.HasErrors)
                {
                    // Add 1 to indicate child has errors
                    count++;
                }

                return count;
            }
        }

        #endregion Computed Properties for Error Aggregation

        #region Constructor

        public CloudDocumentManagerViewModel(
            MessageStore messageStore,
            Manager manager,
            CloudDocumentManager cloudDocumentManager,
            IDialogService dialogService)
        {
            _manager = manager;
            _messageStore = messageStore;
            _cloudDocumentManager = cloudDocumentManager;
            _dialogService = dialogService;

            // Initialize available provider types
            AvailableProviderTypes =
            [
                CloudProviderType.None,
                CloudProviderType.Aconex
                // Future providers will be added here
            ];

            // Load initial state from model
            LoadFromModel();
        }

        #endregion Constructor

        #region Property Changed Handlers

        /// <summary>
        /// Handles when SelectedProviderType changes
        /// Swaps out the current provider control ViewModel and warns about data loss
        /// </summary>
        partial void OnSelectedProviderTypeChanged(CloudProviderType value)
        {
            // Check if we're switching providers and have existing data
            if (CurrentProviderControl != null && HasExistingProviderData())
            {
                // Warn user about data loss
                var result = _dialogService.ShowMessageBox(
                    "Switching providers will lose current configuration. Continue?",
                    "Warning",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Warning);

                if (result != MessageBoxResult.Yes)
                {
                    // User cancelled - revert to previous selection
                    // Note: This will trigger this handler again, but HasExistingProviderData 
                    // will return false for the same provider
                    return;
                }
            }

            // Unsubscribe from old control if it exists
            if (CurrentProviderControl != null)
            {
                if (CurrentProviderControl is INotifyPropertyChanged oldPropertyControl)
                {
                    oldPropertyControl.PropertyChanged -= OnProviderControlPropertyChanged;
                }
                
                if (CurrentProviderControl is INotifyDataErrorInfo oldErrorControl)
                {
                    oldErrorControl.ErrorsChanged -= OnProviderControlErrorsChanged;
                }
            }

            // Create appropriate control ViewModel based on selected type
            CurrentProviderControl = value switch
            {
                CloudProviderType.None => null, // No control for None
                CloudProviderType.Aconex => CreateAconexControl(),
                _ => throw new ArgumentException($"Unknown provider type: {value}")
            };

            // Subscribe to new control property changes and error changes for validation propagation
            if (CurrentProviderControl != null)
            {
                if (CurrentProviderControl is INotifyPropertyChanged newPropertyControl)
                {
                    newPropertyControl.PropertyChanged += OnProviderControlPropertyChanged;
                }
                
                if (CurrentProviderControl is INotifyDataErrorInfo newErrorControl)
                {
                    newErrorControl.ErrorsChanged += OnProviderControlErrorsChanged;
                }
            }

            // Notify that validation state has changed
            OnPropertyChanged(nameof(HasValidationErrors));
            OnPropertyChanged(nameof(ErrorCount));

            // Note: UpdateModelProvider is not called here because CreateAconexControl (and future provider methods)
            // already handle creating/setting the MetaDataMapper instance correctly.
            // Calling UpdateModelProvider here would create a new mapper instance and break the binding.
        }

        /// <summary>
        /// Handles when CloudDocumentManagerEnabled changes
        /// Controls visibility/enabled state of provider selection and controls
        /// Triggers validation as enabled state affects validation rules
        /// </summary>
        partial void OnCloudDocumentManagerEnabledChanged(bool value)
        {
            _cloudDocumentManager.CloudDocumentManagerEnabled = value;
            
            // Notify that validation state has changed
            OnPropertyChanged(nameof(HasValidationErrors));
            OnPropertyChanged(nameof(ErrorCount));
        }

        /// <summary>
        /// Handles property changes from child provider controls
        /// Used for validation propagation
        /// </summary>
        private void OnProviderControlPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            // Propagate validation state changes up to parent
            // This allows the parent ViewModel to react to child validation errors
            // Property name is intentionally empty to trigger all dependent properties
            OnPropertyChanged(string.Empty);
        }

        /// <summary>
        /// Handles error changes from child provider controls
        /// When child validation state changes, re-evaluate parent HasValidationErrors property
        /// </summary>
        private void OnProviderControlErrorsChanged(object? sender, DataErrorsChangedEventArgs e)
        {
            // When child errors change, notify that our validation properties have changed
            // This propagates the validation state up to the parent ViewModel
            OnPropertyChanged(nameof(HasValidationErrors));
            OnPropertyChanged(nameof(ErrorCount));
        }

        #endregion Property Changed Handlers

        #region Helper Methods

        /// <summary>
        /// Loads the current state from the CloudDocumentManager model
        /// </summary>
        private void LoadFromModel()
        {
            CloudDocumentManagerEnabled = _cloudDocumentManager.CloudDocumentManagerEnabled;

            // Determine provider type from existing MetaDataMapper
            if (_cloudDocumentManager.MetaDataMapper != null)
            {
                SelectedProviderType = _cloudDocumentManager.MetaDataMapper switch
                {
                    MetaDataMapperAconex => CloudProviderType.Aconex,
                    _ => CloudProviderType.None // Unknown mapper type defaults to None
                };
            }
            else
            {
                // No mapper set - keep default of None
                // This forces user to explicitly select a provider
                SelectedProviderType = CloudProviderType.None;
            }

            // Note: We don't need to explicitly create the control here anymore
            // because setting SelectedProviderType will trigger OnSelectedProviderTypeChanged
            // which will create the appropriate control (or set it to null for None)
        }

        /// <summary>
        /// Checks if the current provider has existing data that would be lost on switch
        /// </summary>
        private bool HasExistingProviderData()
        {
            if (_cloudDocumentManager.MetaDataMapper == null)
                return false;

            // Check if there's any meaningful configuration
            // For Aconex: check if template path is set or mappings exist
            if (_cloudDocumentManager.MetaDataMapper is MetaDataMapperAconex aconexMapper)
            {
                return !string.IsNullOrWhiteSpace(aconexMapper.MetadataTemplateFilePath)
                       || aconexMapper.MetaDataMap.Count > 0;
            }

            return false;
        }

        /// <summary>
        /// Creates an Aconex provider control ViewModel
        /// </summary>
        private ObservableObject CreateAconexControl()
        {
            // Get or create an Aconex mapper in the model
            MetaDataMapperAconex aconexMapper;

            if (_cloudDocumentManager.MetaDataMapper is MetaDataMapperAconex existingMapper)
            {
                // Use existing mapper
                aconexMapper = existingMapper;
            }
            else
            {
                // Create new mapper
                aconexMapper = new MetaDataMapperAconex();
                _cloudDocumentManager.MetaDataMapper = aconexMapper;
            }

            // Create and return the Aconex control ViewModel
            return new ViewModels.CloudProviderControls.AconexMetadataControlViewModel(
                _messageStore,
                _dialogService,
                aconexMapper,
                new duHastNet.DocManager.Core.Services.MetaDataTemplateService(),
                _manager);
        }


        /// <summary>
        /// Saves the current configuration from the provider control back to the model
        /// Called by parent SettingsViewModel when Save is clicked
        /// </summary>
        public void SaveToModel()
        {
            // Update enabled state
            _cloudDocumentManager.CloudDocumentManagerEnabled = CloudDocumentManagerEnabled;

            // If disabled, we're done
            if (!CloudDocumentManagerEnabled)
                return;

            // Provider-specific save logic will be handled by the control ViewModel
            // For now, the control directly modifies the MetaDataMapper instance
            // so no additional save logic is needed here

            // Future: If we add validation at this level, implement it here
        }

        /// <summary>
        /// Validates the current configuration
        /// Returns true if valid, false otherwise
        /// DEPRECATED: Use HasValidationErrors property instead
        /// Kept for backward compatibility
        /// </summary>
        public bool ValidateConfiguration()
        {
            return !HasValidationErrors;
        }

        #endregion Helper Methods
    }
}
