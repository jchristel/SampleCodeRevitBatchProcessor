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

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    /// <summary>
    /// Partial class for DatabaseConnectionViewModel containing all custom fields functionality
    /// </summary>
    public partial class DatabaseConnectionViewModel
    {
        #region Custom Fields - Observable Properties

        /// <summary>
        /// Observable collection of custom fields for display in ListView
        /// </summary>
        [ObservableProperty]
        private ObservableCollection<CustomFieldViewModel> _customFields = new();

        /// <summary>
        /// Currently selected custom field in the ListView
        /// </summary>
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(RemoveCustomFieldCommand))]
        private CustomFieldViewModel? _selectedCustomField;

        /// <summary>
        /// Controls whether the custom fields expander is expanded
        /// Bound to database connection state
        /// </summary>
        public bool IsCustomFieldsExpanded => IsConnected;

        #endregion Custom Fields - Observable Properties

        #region Custom Fields - Initialization

        /// <summary>
        /// Initializes the custom fields collection from Manager
        /// Called during ViewModel construction
        /// </summary>
        private void InitializeCustomFields()
        {
            LoadCustomFieldsFromManager();
        }

        /// <summary>
        /// Loads custom field names from Manager into the CustomFields observable collection
        /// </summary>
        private void LoadCustomFieldsFromManager()
        {
            CustomFields.Clear();

            var propertyNames = _manager.GetAllCustomPropertyNames();

            foreach (var propertyName in propertyNames)
            {
                var displayModel = new CustomFieldViewModel(propertyName);
                CustomFields.Add(displayModel);
            }
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
                    // Add to display collection
                    AddCustomFieldToCollection(dialogViewModel.CreatedFieldName);

                    _messageStore.SetCurrentMessage(
                        "Custom field added successfully",
                        MessageTypes.Information,
                        10); // Auto-dismiss after 10 seconds
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
        /// Requires database connection and a selected field
        /// </summary>
        private bool CanRemoveCustomField()
        {
            return IsConnected && SelectedCustomField != null;
        }

        /// <summary>
        /// Command to remove the selected custom field
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanRemoveCustomField))]
        private void RemoveCustomField()
        {
            if (SelectedCustomField == null)
                return;

            try
            {
                var fieldName = SelectedCustomField.PropertyName;

                // Confirm removal with user
                var result = System.Windows.MessageBox.Show(
                    $"Are you sure you want to remove the custom field '{fieldName}'?\n\n" +
                    "Note: This only removes the field definition. Any existing documents with this custom property will retain their data.",
                    "Confirm Removal",
                    System.Windows.MessageBoxButton.YesNo,
                    System.Windows.MessageBoxImage.Question);

                if (result == System.Windows.MessageBoxResult.Yes)
                {
                    // Remove from display collection
                    RemoveCustomFieldFromCollection(SelectedCustomField);

                    _messageStore.SetCurrentMessage(
                        $"Custom field '{fieldName}' removed successfully",
                        MessageTypes.Information,
                        10); // Auto-dismiss after 10 seconds
                }
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Error removing custom field: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Command to update database schema with custom fields
        /// </summary>
        [RelayCommand]
        private async Task UpdateDatabaseSchemaAsync()
        {
            // TODO: Determine what this command should do
            // The CustomProperty table already exists in the schema
            // This might be deprecated or need clarification
            await Task.CompletedTask;

            _messageStore.SetCurrentMessage(
                "Update database schema not yet implemented",
                MessageTypes.Information);
        }

        #endregion Custom Fields - Commands

        #region Custom Fields - Helper Methods

        /// <summary>
        /// Checks if a custom field with the given name already exists
        /// Used for duplicate prevention
        /// </summary>
        /// <param name="fieldName">The field name to check (case-insensitive)</param>
        /// <returns>True if a duplicate exists, false otherwise</returns>
        public bool IsDuplicateCustomField(string fieldName)
        {
            return CustomFields.Any(cf => 
                cf.PropertyName.Equals(fieldName, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Adds a newly created custom field to the display collection
        /// </summary>
        /// <param name="fieldName">The field name to add</param>
        private void AddCustomFieldToCollection(string fieldName)
        {
            var displayModel = new CustomFieldViewModel(fieldName);
            CustomFields.Add(displayModel);
        }

        /// <summary>
        /// Removes a custom field from the display collection
        /// </summary>
        /// <param name="customField">The custom field to remove</param>
        private void RemoveCustomFieldFromCollection(CustomFieldViewModel customField)
        {
            CustomFields.Remove(customField);
        }

        #endregion Custom Fields - Helper Methods
    }
}
