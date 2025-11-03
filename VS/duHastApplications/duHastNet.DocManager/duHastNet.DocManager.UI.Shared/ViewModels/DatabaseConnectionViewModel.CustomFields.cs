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
using duHastNet.DocManager.UI.Shared.Stores;
using System.Collections.ObjectModel;
using System.Text;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    /// <summary>
    /// Partial class for DatabaseConnectionViewModel containing all custom fields functionality
    /// </summary>
    public partial class DatabaseConnectionViewModel
    {
        #region Custom Fields - Observable Properties

        /// <summary>
        /// Observable collection of custom fields for display in ListView (working copy)
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<CustomFieldViewModel> _customFields = new();

        /// <summary>
        /// Original custom fields loaded from database (for change tracking)
        /// </summary>
        private List<CustomFieldViewModel> _originalCustomFields = new();

        /// <summary>
        /// Currently selected custom field in the ListView
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(RemoveCustomFieldCommand))]
        [NotifyCanExecuteChangedFor(nameof(ToggleCustomFieldActiveCommand))]
        private CustomFieldViewModel? _selectedCustomField;

        /// <summary>
        /// Controls whether the custom fields expander is expanded
        /// Bound to database connection state
        /// </summary>
        public bool IsCustomFieldsExpanded => IsConnected;

        /// <summary>
        /// Indicates whether there are unsaved changes to custom fields
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(UpdateDatabaseSchemaCommand))]
        private bool _hasPendingCustomFieldChanges = false;

        #endregion Custom Fields - Observable Properties

        #region Custom Fields - Initialization

        /// <summary>
        /// Initializes the custom fields collection from Manager
        /// Called after database connection
        /// </summary>
        private void InitializeCustomFields()
        {
            LoadCustomFieldsFromManager();
        }

        /// <summary>
        /// Loads custom field definitions from Manager into the CustomFields observable collection
        /// </summary>
        private void LoadCustomFieldsFromManager()
        {
            CustomFields.Clear();
            _originalCustomFields.Clear();

            var definitions = _manager.GetAllCustomFieldDefinitions();

            foreach (var definition in definitions)
            {
                var displayModel = new CustomFieldViewModel(definition);
                CustomFields.Add(displayModel);
                _originalCustomFields.Add(displayModel.Clone());
            }

            HasPendingCustomFieldChanges = false;
        }

        #endregion Custom Fields - Initialization

        #region Custom Fields - Commands

        /// <summary>
        /// Determines if a custom field can be added
        /// Requires database connection
        /// </summary>
        private bool CanAddCustomField()
        {
            return IsConnected;
        }

        /// <summary>
        /// Command to add a new custom field
        /// Opens the Add Custom Field dialog
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanAddCustomField))]
        private void AddCustomField()
        {
            try
            {
                // Create ViewModel for Add mode
                var dialogViewModel = new CustomFieldDialogViewModel(this);

                // Create and show dialog
                var dialog = new Views.CustomFieldDialog(dialogViewModel);
                dialog.Owner = System.Windows.Application.Current.MainWindow;

                var result = dialog.ShowDialog();

                if (result == true && !string.IsNullOrEmpty(dialogViewModel.CreatedFieldName))
                {
                    // Add to display collection (not saved yet)
                    var newField = new CustomFieldViewModel(dialogViewModel.CreatedFieldName);
                    CustomFields.Add(newField);

                    // Mark as having pending changes
                    HasPendingCustomFieldChanges = true;

                    _messageStore.SetCurrentMessage(
                        $"Custom field '{dialogViewModel.CreatedFieldName}' added. Click 'Update Database' to save changes.",
                        MessageTypes.Information,
                        10);
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error adding custom field: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if a custom field can be removed
        /// Only unsaved fields (Id == 0) can be removed
        /// </summary>
        private bool CanRemoveCustomField()
        {
            return IsConnected && SelectedCustomField != null && SelectedCustomField.Id == 0;
        }

        /// <summary>
        /// Command to remove a custom field that hasn't been saved to the database yet
        /// Only works for fields with Id == 0 (not yet persisted)
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanRemoveCustomField))]
        private void RemoveCustomField()
        {
            if (SelectedCustomField == null || SelectedCustomField.Id != 0)
                return;

            try
            {
                var fieldName = SelectedCustomField.PropertyName;

                // Remove from collection
                CustomFields.Remove(SelectedCustomField);

                // Update pending changes flag
                HasPendingCustomFieldChanges = GetCustomFieldChanges().Any();

                _messageStore.SetCurrentMessage(
                    $"Custom field '{fieldName}' removed.",
                    MessageTypes.Information,
                    10);
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error removing custom field: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if a custom field active status can be toggled
        /// Requires database connection and a selected field
        /// </summary>
        private bool CanToggleCustomFieldActive()
        {
            return IsConnected && SelectedCustomField != null;
        }

        /// <summary>
        /// Command to toggle the active/inactive status of the selected custom field
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanToggleCustomFieldActive))]
        private void ToggleCustomFieldActive()
        {
            if (SelectedCustomField == null)
                return;

            try
            {
                // Toggle the IsActive status
                SelectedCustomField.IsActive = !SelectedCustomField.IsActive;

                // Mark as having pending changes
                HasPendingCustomFieldChanges = true;

                var status = SelectedCustomField.IsActive ? "activated" : "deactivated";
                _messageStore.SetCurrentMessage(
                    $"Custom field '{SelectedCustomField.PropertyName}' {status}. Click 'Update Database' to save changes.",
                    MessageTypes.Information,
                    10);
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error toggling custom field: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Determines if database can be updated
        /// Requires connection and pending changes
        /// </summary>
        private bool CanUpdateDatabaseSchema()
        {
            return IsConnected && HasPendingCustomFieldChanges;
        }

        /// <summary>
        /// Command to update database with custom field changes
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanUpdateDatabaseSchema))]
        private async Task UpdateDatabaseSchemaAsync()
        {
            try
            {
                IsBusy = true;

                // Get the changes
                var changes = GetCustomFieldChanges();

                if (!changes.Any())
                {
                    _messageStore.SetCurrentMessage(
                        "No changes to apply",
                        MessageTypes.Information);
                    return;
                }

                // Show confirmation dialog
                if (!ShowConfirmationDialog(changes))
                {
                    return;
                }

                // Apply changes
                await ApplyCustomFieldChangesAsync(changes);

                // Reload from manager
                var reloadResult = await _docManagerApi.ReloadDataIntoManagerAsync(_manager);

                if (reloadResult.Success)
                {
                    LoadCustomFieldsFromManager();
                    UpdateStatistics();

                    // Clean up metadata mappings that reference deactivated custom fields
                    CleanupInactiveMappings(changes);

                    _messageStore.SetCurrentMessage(
                        "Custom field changes applied successfully",
                        MessageTypes.Information,
                        10);
                }
                else
                {
                    _messageStore.SetCurrentMessage(
                        $"Changes applied but reload failed: {string.Join("; ", reloadResult.Errors)}",
                        MessageTypes.Warning);
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error updating database: {ex.Message}",
                    MessageTypes.Error);
            }
            finally
            {
                IsBusy = false;
            }
        }

        #endregion Custom Fields - Commands

        #region Custom Fields - Helper Methods

        /// <summary>
        /// Checks if a custom field with the given name already exists
        /// Used for duplicate prevention
        /// </summary>
        public bool IsDuplicateCustomField(string fieldName)
        {
            return CustomFields.Any(cf =>
                cf.PropertyName.Equals(fieldName, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Gets the list of changes between current and original custom fields
        /// </summary>
        private List<CustomFieldChange> GetCustomFieldChanges()
        {
            var changes = new List<CustomFieldChange>();

            // Find new fields (Id == 0)
            foreach (var field in CustomFields.Where(f => f.Id == 0))
            {
                changes.Add(new CustomFieldChange
                {
                    ChangeType = CustomFieldChangeType.Add,
                    PropertyName = field.PropertyName,
                    IsActive = field.IsActive
                });
            }

            // Find modified fields (IsActive changed)
            foreach (var field in CustomFields.Where(f => f.Id > 0))
            {
                var original = _originalCustomFields.FirstOrDefault(o => o.Id == field.Id);
                if (original != null && original.IsActive != field.IsActive)
                {
                    changes.Add(new CustomFieldChange
                    {
                        ChangeType = field.IsActive ? CustomFieldChangeType.Activate : CustomFieldChangeType.Deactivate,
                        Id = field.Id,
                        PropertyName = field.PropertyName,
                        IsActive = field.IsActive
                    });
                }
            }

            return changes;
        }

        /// <summary>
        /// Shows confirmation dialog with summary of changes
        /// </summary>
        private bool ShowConfirmationDialog(List<CustomFieldChange> changes)
        {
            var message = new StringBuilder();
            message.AppendLine("Apply Custom Field Changes?");
            message.AppendLine();

            var newFields = changes.Where(c => c.ChangeType == CustomFieldChangeType.Add).ToList();
            var activatedFields = changes.Where(c => c.ChangeType == CustomFieldChangeType.Activate).ToList();
            var deactivatedFields = changes.Where(c => c.ChangeType == CustomFieldChangeType.Deactivate).ToList();

            if (newFields.Any())
            {
                message.AppendLine($"New Fields: {newFields.Count}");
                foreach (var field in newFields)
                {
                    message.AppendLine($"  - {field.PropertyName}");
                }
                message.AppendLine();
            }

            if (activatedFields.Any())
            {
                message.AppendLine($"Activated Fields: {activatedFields.Count}");
                foreach (var field in activatedFields)
                {
                    message.AppendLine($"  - {field.PropertyName}");
                }
                message.AppendLine();
            }

            if (deactivatedFields.Any())
            {
                message.AppendLine($"Deactivated Fields: {deactivatedFields.Count}");
                foreach (var field in deactivatedFields)
                {
                    message.AppendLine($"  - {field.PropertyName}");
                }
                message.AppendLine();
            }

            if (newFields.Any())
            {
                message.AppendLine("Note: New fields will create records for all documents.");
            }

            var result = System.Windows.MessageBox.Show(
                message.ToString(),
                "Confirm Changes",
                System.Windows.MessageBoxButton.YesNo,
                System.Windows.MessageBoxImage.Question);

            return result == System.Windows.MessageBoxResult.Yes;
        }

        /// <summary>
        /// Applies custom field changes to the database
        /// </summary>
        private async Task ApplyCustomFieldChangesAsync(List<CustomFieldChange> changes)
        {
            foreach (var change in changes)
            {
                switch (change.ChangeType)
                {
                    case CustomFieldChangeType.Add:
                        var addResult = await _docManagerApi.AddCustomFieldDefinitionAsync(
                            change.PropertyName,
                            change.IsActive);

                        if (!addResult.Success)
                        {
                            throw new Exception($"Failed to add field '{change.PropertyName}': {string.Join("; ", addResult.Errors)}");
                        }
                        break;

                    case CustomFieldChangeType.Activate:
                    case CustomFieldChangeType.Deactivate:
                        var updateResult = await _docManagerApi.UpdateCustomFieldIsActiveAsync(
                            change.Id,
                            change.IsActive);

                        if (!updateResult.Success)
                        {
                            throw new Exception($"Failed to update field '{change.PropertyName}': {string.Join("; ", updateResult.Errors)}");
                        }
                        break;
                }
            }
        }

        /// <summary>
        /// Cleans up metadata mappings that reference deactivated custom fields
        /// Called after successful database update
        /// </summary>
        private void CleanupInactiveMappings(List<CustomFieldChange> changes)
        {
            // Get all deactivated fields from changes
            var deactivatedFields = changes
                .Where(c => c.ChangeType == CustomFieldChangeType.Deactivate)
                .Select(c => c.PropertyName)
                .ToList();

            if (!deactivatedFields.Any())
                return;

            // Access the metadata mapper through Manager
            var metaDataMapper = _manager.CloudDocumentManager?.MetaDataMapper;
            if (metaDataMapper == null)
                return;

            var removedMappings = new List<string>();

            // Find and remove mappings that reference deactivated custom fields
            var mappingsToRemove = metaDataMapper.MetaDataMap
                .Where(mapping => !string.IsNullOrEmpty(mapping.DocumentPropertyName) &&
                                 deactivatedFields.Contains(mapping.DocumentPropertyName, StringComparer.OrdinalIgnoreCase))
                .ToList();

            foreach (var mapping in mappingsToRemove)
            {
                metaDataMapper.RemoveMapper(mapping);
                removedMappings.Add($"{mapping.MetaFieldName} -> {mapping.DocumentPropertyName}");
            }

            // Show message if any mappings were removed
            if (removedMappings.Any())
            {
                // Raise the MappingsChanged event so subscribers (AconexMetadataControlViewModel) can refresh
                if (_manager.CloudDocumentManager != null)
                    _manager.CloudDocumentManager.RaiseMappingsChanged();

                var message = $"Removed {removedMappings.Count} metadata mapping(s) referencing deactivated custom field(s):\n" +
                             string.Join("\n", removedMappings.Select(m => $"  - {m}"));

                _messageStore.SetCurrentMessage(
                    message,
                    MessageTypes.Information,
                    15);
            }
        }

        #endregion Custom Fields - Helper Methods
    }

    #region Helper Classes

    /// <summary>
    /// Represents a change to a custom field
    /// </summary>
    internal class CustomFieldChange
    {
        public CustomFieldChangeType ChangeType { get; set; }
        public int Id { get; set; }
        public string PropertyName { get; set; } = string.Empty;
        public bool IsActive { get; set; }
    }

    /// <summary>
    /// Type of change to a custom field
    /// </summary>
    internal enum CustomFieldChangeType
    {
        Add,
        Activate,
        Deactivate
    }

    #endregion
}
