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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Stores;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Main ViewModel for the Settings view - handles database configuration and management
/// </summary>
public partial class SettingsViewModel : ObservableObject
{
    #region Private Fields

    private readonly DocManagerApi _docManagerApi;
    private readonly MessageStore _messageStore;
    private readonly Manager _manager;
    private readonly NavigationStore _navigationStore;
    Core.Models.CurrentFolder.CurrentFolderManager _currentFolderManager;
    Core.Models.MetaDataMapperAconex _aconexMetaDataManager;

    #endregion

    // Expose message ViewModel for the view
    public GlobalMessageViewModel MessageViewModel { get; }

    // Expose Aconex Metadata ViewModel for the view
    public MetaDataAconexViewModel AconexMetadataViewModel { get; }

    // Expose current folder ViewModel for the view
    public CurrentFolderViewModel CurrentFolderViewModel { get;}

    // Expose the database connection ViewModel for the view
    public DatabaseConnectionViewModel DatabaseConnectionViewModel { get;}

    #region Constructor

    public SettingsViewModel(
        DocManagerApi docManagerApi, 
        Manager manager, 
        MessageStore messageStore, 
        Core.Models.CurrentFolder.CurrentFolderManager currentFolderManager,
        MetaDataMapperAconex aconexMetaDataManager,
        NavigationStore navigationStore,
        Func<MergeViewModel> createViewModel
        )
    {
        _docManagerApi = docManagerApi;
        _manager = manager;
        _messageStore = messageStore;
        _currentFolderManager = currentFolderManager;
        _aconexMetaDataManager = aconexMetaDataManager;
        _navigationStore = navigationStore;

        MessageViewModel = new GlobalMessageViewModel(_messageStore);
        DatabaseConnectionViewModel = new DatabaseConnectionViewModel(_docManagerApi, _messageStore, _manager);
        AconexMetadataViewModel = new MetaDataAconexViewModel(_messageStore, _manager);
        CurrentFolderViewModel = new CurrentFolderViewModel(_messageStore, _manager, currentFolderManager);

    }

    #endregion

}