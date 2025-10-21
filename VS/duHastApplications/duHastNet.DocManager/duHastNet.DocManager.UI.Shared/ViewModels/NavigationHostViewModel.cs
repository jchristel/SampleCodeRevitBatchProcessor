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

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    public partial class NavigationHostViewModel : ObservableObject
    {
        private readonly DocManagerApi _docManagerApi;
        private readonly Manager _manager;
        private readonly MessageStore _messageStore;
        private readonly Core.Models.CurrentFolder.CurrentFolderManager _currentFolderManager;
        private readonly Core.Interfaces.ICloudMetaData _cloudMetaData;

        [ObservableProperty]
        private ObservableObject _currentViewModel;

        public NavigationHostViewModel(
            DocManagerApi docManagerApi, 
            Manager manager, 
            Core.Models.CurrentFolder.CurrentFolderManager currentFolderManager,
            Core.Interfaces.ICloudMetaData cloudMetaData,
            MessageStore messageStore)
        {
            _docManagerApi = docManagerApi;
            _manager = manager;
            _currentFolderManager = currentFolderManager;
            _cloudMetaData = cloudMetaData;
            _messageStore = messageStore;

            // Initialize with SettingsViewModel as the default view
            _currentViewModel = new SettingsViewModel(
                _docManagerApi, 
                _manager, 
                _messageStore,
                _currentFolderManager,
                _cloudMetaData
                );
        }
    }
}