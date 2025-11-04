using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.UI.Shared.Stores;
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
        /// Save is only enabled when no child ViewModels have validation errors
        /// </summary>
        private bool CanSave()
        {
            return !HasAnyErrors;
        }

        /// <summary>
        /// Command to save all settings
        /// Saves current folder settings, cloud document manager settings, etc.
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanSave))]
        private void Save()
        {
            try
            {
                // TODO: Implement actual save logic using ISettingsService
                // - Save current folder settings via ISettingsService
                // - Save cloud document manager settings via ISettingsService
                // - Database connection doesn't need separate save (connects directly)

                _messageStore.SetCurrentMessage(
                    "Settings saved successfully",
                    MessageTypes.Information,
                    dismissAfterSeconds: 3);
            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage(
                    $"Failed to save settings: {ex.Message}",
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
