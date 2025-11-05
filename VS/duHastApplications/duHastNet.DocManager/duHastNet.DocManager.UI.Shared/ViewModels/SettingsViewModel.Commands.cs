using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.Core.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.DocManager.UI.Shared.ViewModels
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
                    "DatabaseConnection.json");

                if (!databaseResult.Success)
                {
                    _messageStore.SetCurrentMessage(
                        $"Failed to save Database Connection settings: {string.Join("; ", databaseResult.Errors)}",
                        MessageTypes.Error);
                    return;
                }

                // Save CurrentFolderManager settings
                var currentFolderResult = await _settingsService.SaveAsync(
                    _currentFolderManager.Settings,
                    "CurrentFolderManager.json");

                if (!currentFolderResult.Success)
                {
                    _messageStore.SetCurrentMessage(
                        $"Failed to save Current Folder settings: {string.Join("; ", currentFolderResult.Errors)}",
                        MessageTypes.Error);
                    return;
                }

                // Save CloudDocumentManager settings
                var cloudDocResult = await _settingsService.SaveAsync(
                    _manager.CloudDocumentManager,
                    "CloudDocumentManager.json");

                if (!cloudDocResult.Success)
                {
                    _messageStore.SetCurrentMessage(
                        $"Failed to save Cloud Document Manager settings: {string.Join("; ", cloudDocResult.Errors)}",
                        MessageTypes.Error);
                    return;
                }

                // All saves successful
                _messageStore.SetCurrentMessage(
                    "Settings saved successfully",
                    MessageTypes.Information,
                    dismissAfterSeconds: 5);
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
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
