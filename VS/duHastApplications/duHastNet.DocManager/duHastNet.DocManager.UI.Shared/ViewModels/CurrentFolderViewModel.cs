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
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Stores;


namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    public partial class CurrentFolderViewModel: ObservableObject
    {
        /// <summary>
        /// view model class for the current folder model
        /// </summary>
        #region Private Fields

        private readonly MessageStore _messageStore;
        private readonly Manager _manager;
        private readonly Core.Models.CurrentFolder.CurrentFolderManager _currentFolderManager;

        #endregion Private Fields

        #region Constructor

        public CurrentFolderViewModel(MessageStore messageStore, Manager manager, Core.Models.CurrentFolder.CurrentFolderManager currentFolderManager)
        {
            _manager = manager;
            _messageStore = messageStore;
            _currentFolderManager = currentFolderManager;
        }

        #endregion

        #region Observable Properties

        [ObservableProperty]
        private string _incomingFolderPath = string.Empty;

        [ObservableProperty]
        private bool _isBrowseIncomingFolderEnabled = true;

        [ObservableProperty]
        private string _archiveFolderPath = string.Empty;

        [ObservableProperty]
        private bool _isBrowseArchiveFolderEnabled = true;

        [ObservableProperty]
        private string _revisionPrefix = string.Empty;

        [ObservableProperty]
        private string _revisionSuffix = string.Empty;

        #endregion Observable Properties

        #region Commands - To be implemented

        #endregion  Commands - To be implemented

    }
}

