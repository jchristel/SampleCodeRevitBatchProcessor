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

using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings
{
    public partial class SettingsViewModel
    {
        #region Commands

        /// <summary>
        /// Determines if settings can be saved
        /// Checks validation state of all child ViewModels
        /// </summary>
        private bool CanSave()
        {
            // Check CurrentFolderViewModel for validation errors
            if (CurrentFolderViewModel.HasErrors)
                return false;

            // Check DatabaseConnectionViewModel - must have database ready
            if (!DatabaseConnectionViewModel.IsDatabaseReady)
                return false;

            // Check CloudDocumentManagerViewModel configuration
            if (!AconexMetadataViewModel.ValidateConfiguration())
                return false;

            return true;
        }

        /// <summary>
        /// Command to save settings and close
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanSave))]
        private async Task SaveAsync()
        {
            try
            {
                // Save DatabaseConnection settings (just the path)
                var databaseSettings = new DatabaseConnectionSettings(
                    _docManagerApi.GetDatabasePath() ?? string.Empty);
                
                var databaseResult = await _settingsService.SaveAsync(
                    databaseSettings,
                    SettingsFileNames.DatabaseConnection);

                if (!databaseResult.Success)
                {
                    _messageStore.EnqueueMessage(
                        $"Failed to save Database Connection settings: {string.Join("; ", databaseResult.Errors)}",
                        MessageTypes.Error);
                    return;
                }

                // Save CurrentFolderManager settings
                var currentFolderResult = await _settingsService.SaveAsync(
                    _currentFolderManager.Settings,
                    SettingsFileNames.CurrentFolderManager);

                if (!currentFolderResult.Success)
                {
                    _messageStore.EnqueueMessage(
                        $"Failed to save Current Folder settings: {string.Join("; ", currentFolderResult.Errors)}",
                        MessageTypes.Error);
                    return;
                }

                // Save CloudDocumentManager settings
                var cloudDocResult = await _settingsService.SaveAsync(
                    _manager.CloudDocManager,
                    SettingsFileNames.CloudDocumentManager);

                if (!cloudDocResult.Success)
                {
                    _messageStore.EnqueueMessage(
                        $"Failed to save Cloud Document Manager settings: {string.Join("; ", cloudDocResult.Errors)}",
                        MessageTypes.Error);
                    return;
                }

                // All saves successful
                _messageStore.EnqueueMessage(
                    "Settings saved successfully",
                    MessageTypes.Information,
                    dismissAfterSeconds: 5);
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Error saving settings: {ex.Message}",
                    MessageTypes.Error);
            }
        }

        /// <summary>
        /// Command to navigate to the Merge view
        /// </summary>
        [RelayCommand]
        private void NavigateToMerge()
        {
            _navigationStore.NavigateTo(() => _createViewModel());
        }

        #endregion
    }
}
