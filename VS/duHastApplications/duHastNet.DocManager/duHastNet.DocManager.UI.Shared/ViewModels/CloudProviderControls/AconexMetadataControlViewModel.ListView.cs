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
    /// </summary>
    public partial class AconexMetadataControlViewModel : ObservableValidator
    {

        #region Observable Properties

        /// <summary>
        /// Currently selected mapping in the ListView
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(EditMetadataMappingCommand))]
        private MetaDataMapViewModel? _selectedMapping;

        #endregion Observable Properties

        #region Property Changed Handlers


        #endregion Property Changed Handlers

        #region Commands

        /// <summary>
        /// Command to add a new metadata mapping
        /// Opens dialog for user to configure the mapping
        /// </summary>
        [RelayCommand]
        private void AddMetadataMapping()
        {
            // Check if template is loaded
            if (_aconexMapper.AvailableFields.Count == 0)
            {
                _messageStore.SetCurrentMessage(
                    "Please select and load a template file before adding mappings.", MessageTypes.Warning);
                return;
            }

            // Get list of unmapped fields
            var mappedFields = _aconexMapper.MetaDataMap
                .Select(m => m.MetaFieldName)
                .Where(f => !string.IsNullOrEmpty(f))
                .ToList();

            var unmappedFields = _aconexMapper.AvailableFields
                .Where(f => !mappedFields.Contains(f))
                .ToList();

            if (unmappedFields.Count == 0)
            {
                _messageStore.SetCurrentMessage(
                    "All template fields are already mapped.", MessageTypes.Information);
                return;
            }

            try
            {
                // Create ViewModel for Add mode
                var dialogViewModel = new ViewModels.CloudProviderControls.MetaDataMappingDialogViewModel(
                    unmappedFields,
                    GetAvailableDocumentProperties(),
                    _messageStore);

                // Create and show dialog
                var dialog = new Views.MetaDataMappingDialog();
                dialog.Owner = System.Windows.Application.Current.MainWindow;

                var result = dialog.ShowDialog();

                if (result == true && dialogViewModel.CreatedMapping != null)
                {
                    // Add the mapping to the model
                    _aconexMapper.AddMapper(dialogViewModel.CreatedMapping);

                    // Reload the display collection
                    LoadMappingsFromModel();

                    _messageStore.SetCurrentMessage(
                        $"Mapping for '{dialogViewModel.CreatedMapping.MetaFieldName}' added successfully.",
                        MessageTypes.Information);
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error adding mapping: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Command to remove the selected metadata mapping
        /// </summary>
        [RelayCommand]
        private void RemoveMetadataMapping()
        {
            if (SelectedMapping == null)
            {
                _messageStore.SetCurrentMessage(
                    "Please select a mapping to remove.", MessageTypes.Warning);
                return;
            }

            try
            {
                // Store field name for message
                string fieldName = SelectedMapping.MetaFieldName;

                // Remove from the model
                _aconexMapper.RemoveMapper(SelectedMapping.Model);

                // Remove from the display collection
                MetaDataMappings.Remove(SelectedMapping);

                _messageStore.SetCurrentMessage(
                    $"Mapping for '{fieldName}' removed successfully.", MessageTypes.Information);

                // Clear selection
                SelectedMapping = null;
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Failed to remove mapping: {ex.Message}", MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if a mapping can be edited
        /// </summary>
        private bool CanEditMetadataMapping()
        {
            return SelectedMapping != null;
        }

        /// <summary>
        /// Command to edit the selected metadata mapping
        /// Opens dialog with existing values pre-populated
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanEditMetadataMapping))]
        private void EditMetadataMapping()
        {
            if (SelectedMapping == null)
                return;

            // Check if template is loaded
            if (_aconexMapper.AvailableFields.Count == 0)
            {
                _messageStore.SetCurrentMessage(
                    "Please select and load a template file before editing mappings.", MessageTypes.Warning);
                return;
            }

            try
            {
                // Create ViewModel for Edit mode with existing mapping
                var dialogViewModel = new ViewModels.CloudProviderControls.MetaDataMappingDialogViewModel(
                    _aconexMapper.AvailableFields.ToList(),  // All fields (not just unmapped) for Edit mode
                    GetAvailableDocumentProperties(),
                    SelectedMapping.Model,  // Pass existing mapping
                    _messageStore);

                // Create and show dialog
                var dialog = new Views.MetaDataMappingDialog();
                dialog.Owner = System.Windows.Application.Current.MainWindow;

                var result = dialog.ShowDialog();

                if (result == true && dialogViewModel.CreatedMapping != null)
                {
                    // Remove the old mapping
                    _aconexMapper.RemoveMapper(SelectedMapping.Model);

                    // Add the updated mapping
                    _aconexMapper.AddMapper(dialogViewModel.CreatedMapping);

                    // Reload the display collection
                    LoadMappingsFromModel();

                    _messageStore.SetCurrentMessage(
                        $"Mapping for '{dialogViewModel.CreatedMapping.MetaFieldName}' updated successfully.",
                        MessageTypes.Information);

                    // Clear selection since we reloaded
                    SelectedMapping = null;
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error editing mapping: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        #endregion Commands


        #region Helper Methods

        /// <summary>
        /// Loads mappings from the model into the display collection
        /// </summary>
        private void LoadMappingsFromModel()
        {
            MetaDataMappings.Clear();

            foreach (var mapping in _aconexMapper.MetaDataMap)
            {
                MetaDataMappings.Add(new MetaDataMapViewModel(mapping));
            }
        }

        /// <summary>
        /// Gets available document properties for mapping
        /// Includes standard properties and active custom fields
        /// </summary>
        private List<string> GetAvailableDocumentProperties()
        {
            var properties = new List<string>
            {
                // Standard document properties (excluding IDs and histories as per requirements)
                "Number",
                "Name",
                "Revision"
                // Note: Revision Date and Description will be added when we access Revision data
            };

            // Add active custom field definitions
            var customFields = _manager.GetActiveCustomFieldDefinitions()
                .Select(cfd => cfd.PropertyName)
                .OrderBy(name => name);

            properties.AddRange(customFields);

            return properties;
        }

        #endregion Helper Methods
    }
}
