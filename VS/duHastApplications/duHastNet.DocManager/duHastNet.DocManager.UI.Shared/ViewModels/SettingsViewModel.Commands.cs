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
        /// Command to save settings and close
        /// </summary>
        [RelayCommand]
        private void Save()
        {
            // TODO: Implement save logic
            // - Save current folder settings
            // - Save Aconex metadata settings
            // - Save database connection settings

            _messageStore.SetCurrentMessage(
                "Settings saved successfully",
                MessageTypes.Information,
                dismissAfterSeconds: 3);

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
