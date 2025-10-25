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
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.UI.Shared.Stores;
using System.Printing;
using duHastNet.DocManager.UI.Shared.Interfaces;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    public partial class NavigationHostViewModel : ObservableObject, ICloseable
    {
        private readonly DocManagerApi _docManagerApi;
        private readonly Manager _manager;
        private readonly MessageStore _messageStore;
        private readonly Core.Models.CurrentFolder.CurrentFolderManager _currentFolderManager;
        private readonly MetaDataMapperAconex _cloudMetaData;
        private readonly NavigationStore _navigationStore;
        private readonly IDialogService _dialogService;

        #region Public Properties

        /// <summary>
        /// Current ViewModel for binding in the View
        /// </summary>
        public ObservableObject? CurrentViewModel => _navigationStore.CurrentViewModel;

        #endregion

        public NavigationHostViewModel(
            DocManagerApi docManagerApi, 
            Manager manager, 
            Core.Models.CurrentFolder.CurrentFolderManager currentFolderManager,
            MetaDataMapperAconex cloudMetaData,
            MessageStore messageStore,
            NavigationStore navigationStore,
            IDialogService dialogService
            )
        {
            _docManagerApi = docManagerApi;
            _manager = manager;
            _currentFolderManager = currentFolderManager;
            _cloudMetaData = cloudMetaData;
            _messageStore = messageStore;
            _navigationStore = navigationStore;
            _dialogService = dialogService;

            // Subscribe to navigation changes
            _navigationStore.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(NavigationStore.CurrentViewModel))
                {
                    OnPropertyChanged(nameof(CurrentViewModel));
                }
            };

            // Navigate to initial view
            _navigationStore.NavigateTo(CreateSettingsViewModel);
        }

        private SettingsViewModel CreateSettingsViewModel()
        {
            return new SettingsViewModel(
                _docManagerApi!,
                _manager!,
                _messageStore!,
                _currentFolderManager!,
                _cloudMetaData!,
                _navigationStore!,
                _dialogService!,
                CreateMergeViewModel
            );
        }

        private MergeViewModel CreateMergeViewModel()
        {
            return new MergeViewModel(
                _docManagerApi!,
                _messageStore!,
                _navigationStore!,
                CreateSettingsViewModel
            );
        }

        public void OnClosing()
        {
            // Notify the navigation store to close current view model
            _navigationStore.NotifyClosing();
        }
    }
}