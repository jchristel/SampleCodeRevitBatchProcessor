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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    public partial class NavigationHostViewModel : AppViewModelBase
    {
        private readonly IDocManagerApi _docManagerApi;
        private readonly IManager _manager;
        private readonly IMessageStore _messageStore;
        private readonly ICurrentFolderManager _currentFolderManager;
        private readonly NavigationStore _navigationStore;
        private readonly IDialogService _dialogService;
        public readonly ISettingsService _settingsService;

        #region Public Properties

        /// <summary>
        /// Current ViewModel for binding in the View
        /// </summary>
        public ObservableObject? CurrentViewModel => _navigationStore.CurrentViewModel;

        #endregion

        public NavigationHostViewModel(
            IDocManagerApi docManagerApi,
            IManager manager,
            ICurrentFolderManager currentFolderManager,
            IMessageStore messageStore,
            NavigationStore navigationStore,
            ISettingsService settingsService,
            IDialogService dialogService
            )
        {
            _docManagerApi = docManagerApi;
            _manager = manager;
            _currentFolderManager = currentFolderManager;
            _messageStore = messageStore;
            _navigationStore = navigationStore;
            _settingsService = settingsService;
            _dialogService = dialogService;

            // Subscribe to navigation changes via named handler so it can be unsubscribed
            _navigationStore.PropertyChanged += OnNavigationStorePropertyChanged;

            // Navigate to initial view
            _navigationStore.NavigateTo(CreateMergeViewModel);
        }

        /// <summary>
        /// Handles PropertyChanged from NavigationStore to forward CurrentViewModel changes to the View.
        /// Named method (not lambda) so it can be unsubscribed in OnClosing().
        /// </summary>
        private void OnNavigationStorePropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(NavigationStore.CurrentViewModel))
            {
                OnPropertyChanged(nameof(CurrentViewModel));
            }
        }

        /// <summary>
        /// Creates and initializes a new instance of <see cref="Settings.SettingsViewModel"/> with the required
        /// dependencies.
        /// </summary>
        private Settings.SettingsViewModel CreateSettingsViewModel()
        {
            return new Settings.SettingsViewModel(
                _docManagerApi!,
                _manager!,
                _messageStore!,
                _currentFolderManager!,
                _navigationStore!,
                _dialogService!,
                _settingsService!,
                CreateMergeViewModel
            );
        }

        /// <summary>
        /// Creates a new instance of <see cref="Merge.MergeViewModel"/> with the required dependencies.
        /// </summary>
        private Merge.MergeViewModel CreateMergeViewModel()
        {
            return new Merge.MergeViewModel(
                _docManagerApi!,
                _messageStore!,
                _navigationStore!,
                _manager!,
                _currentFolderManager!,
                _dialogService!,
                CreateSettingsViewModel,
                CreateTransmittalViewModel
            );
        }

        /// <summary>
        /// Creates a new instance of <see cref="Transmittal.TransmittalViewModel"/> with the required dependencies.
        /// </summary>
        private Transmittal.TransmittalViewModel CreateTransmittalViewModel()
        {
            return new Transmittal.TransmittalViewModel(
                _navigationStore!,
                _messageStore!,
                CreateMergeViewModel,
                _docManagerApi!,
                _dialogService!
            );
        }

        public override void OnClosing()
        {
            // Unsubscribe from NavigationStore before notifying it to close
            _navigationStore.PropertyChanged -= OnNavigationStorePropertyChanged;

            // Notify the navigation store to close the current ViewModel
            _navigationStore.NotifyClosing();

            base.OnClosing();
        }

        public override void Dispose()
        {
            // No unmanaged resources — NavigationStore is an injected dependency,
            // not owned by this ViewModel
            base.Dispose();
        }
    }
}
