//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Revit.Models.Database;
using duHastNet.DocManager.Revit.Models.Revit;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// Main ViewModel for the Revit integration view.
    /// <para>
    /// Owns the header strip data (app name, database path, connection status) and the
    /// global message banner. Manages panel switching between
    /// <see cref="SheetsPanelViewModel"/> and <see cref="RevisionsPanelViewModel"/>
    /// via a single navigation button. Sheets panel is shown by default on startup.
    /// </para>
    /// <para>
    /// Subscribes to <see cref="SheetsPanelViewModel.RefreshRequested"/> and
    /// <see cref="RevisionsPanelViewModel.RefreshRequested"/>. On receipt, calls
    /// <see cref="DatabaseDataModel.Reload"/> on the shared <see cref="_databaseDataModel"/>
    /// instance, which clears and repopulates its <see cref="DatabaseDataModel.Documents"/>
    /// and <see cref="DatabaseDataModel.Revisions"/> collections in place. Panel ViewModels
    /// bound to those collections update automatically via <see cref="ObservableCollection{T}"/>
    /// change notification.
    /// </para>
    /// </summary>
    public partial class RevitIntegrationViewModel : AppViewModelBase
    {
        #region Private Fields

        private readonly RevitDataModel _revitDataModel;
        private readonly DatabaseDataModel _databaseDataModel;
        private readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
        private readonly duHastNet.UI.DocManagerSettingsUI.Utils.Settings _revitSettings;
        private readonly DocManagerApi _docManagerApi;

        private readonly SheetsPanelViewModel _sheetsPanelViewModel;
        private readonly RevisionsPanelViewModel _revisionsPanelViewModel;

        #endregion Private Fields

        #region Constructor

        /// <summary>
        /// Initializes a new instance of <see cref="RevitIntegrationViewModel"/>.
        /// Sheets panel is set as the default panel on construction.
        /// </summary>
        /// <param name="revitDataModel">Revit data collected before the window opened. Must not be null.</param>
        /// <param name="databaseDataModel">Shared database data model whose collections are observed directly by panel ViewModels. Must not be null.</param>
        /// <param name="messageStore">Message store for surfacing errors and status to the UI banner. Must not be null.</param>
        /// <param name="revitSettings">Settings loaded from the Revit model, including the database path. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when any parameter is null.
        /// </exception>
        public RevitIntegrationViewModel(
            RevitDataModel revitDataModel,
            DatabaseDataModel databaseDataModel,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore,
            duHastNet.UI.DocManagerSettingsUI.Utils.Settings revitSettings)
        {
            _revitDataModel = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));
            _databaseDataModel = databaseDataModel ?? throw new ArgumentNullException(nameof(databaseDataModel));
            _messageStore = messageStore ?? throw new ArgumentNullException(nameof(messageStore));
            _revitSettings = revitSettings ?? throw new ArgumentNullException(nameof(revitSettings));

            _docManagerApi = new DocManagerApi();

            _sheetsPanelViewModel = new SheetsPanelViewModel(
                _revitDataModel,
                _databaseDataModel,
                _messageStore,
                _docManagerApi);

            _revisionsPanelViewModel = new RevisionsPanelViewModel(
                _revitDataModel,
                _databaseDataModel,
                _messageStore);

            // subscribe to refresh events from both panels
            _sheetsPanelViewModel.RefreshRequested += OnPanelRefreshRequested;
            _revisionsPanelViewModel.RefreshRequested += OnPanelRefreshRequested;

            // wire global message banner
            GlobalMessageViewModel = new duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel(_messageStore);

            // sheets panel is the default
            _currentPanelViewModel = _sheetsPanelViewModel;
        }

        #endregion Constructor

        #region Observable Properties

        /// <summary>
        /// Gets the currently displayed panel ViewModel.
        /// Switches between <see cref="SheetsPanelViewModel"/> and <see cref="RevisionsPanelViewModel"/>.
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(NavigationButtonLabel))]
        private ObservableObject _currentPanelViewModel;

        #endregion Observable Properties

        #region Derived Properties

        /// <summary>
        /// Gets the label for the navigation button, indicating which panel will be shown on click.
        /// </summary>
        public string NavigationButtonLabel =>
            CurrentPanelViewModel is SheetsPanelViewModel
                ? "Go to Revisions"
                : "Go to Sheets";

        /// <summary>
        /// Gets the name of the Revit model currently loaded.
        /// </summary>
        public string ModelName => _revitDataModel.ModelName;

        /// <summary>
        /// Gets the database path from settings. Displays a placeholder when not configured.
        /// </summary>
        public string DatabasePath =>
            string.IsNullOrWhiteSpace(_revitSettings.DatabasePath)
                ? "Not configured"
                : _revitSettings.DatabasePath;

        /// <summary>
        /// Gets a value indicating whether the database is currently connected.
        /// Reflects the <see cref="DatabaseDataModel.IsConnected"/> state of the shared model.
        /// </summary>
        public bool IsDatabaseConnected => _databaseDataModel.IsConnected;

        /// <summary>
        /// Gets the ViewModel for the global message banner.
        /// </summary>
        public duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        #endregion Derived Properties

        #region Commands

        /// <summary>
        /// Toggles between the Sheets panel and the Revisions panel.
        /// </summary>
        [RelayCommand]
        private void NavigatePanel()
        {
            CurrentPanelViewModel = CurrentPanelViewModel is SheetsPanelViewModel
                ? _revisionsPanelViewModel
                : _sheetsPanelViewModel;
        }

        #endregion Commands

        #region Database Refresh

        /// <summary>
        /// Handles <see cref="SheetsPanelViewModel.RefreshRequested"/> and
        /// <see cref="RevisionsPanelViewModel.RefreshRequested"/>.
        /// Delegates to <see cref="DatabaseDataModel.Reload"/> which clears and repopulates
        /// the shared collections in place, triggering downstream UI updates automatically.
        /// After the reload, notifies <see cref="SheetsPanelViewModel"/> so it can rebuild
        /// its filtered row list from the refreshed data.
        /// </summary>
        private void OnPanelRefreshRequested(object? sender, EventArgs e)
        {
            _databaseDataModel.Reload(
                _docManagerApi,
                _revitSettings.DatabasePath ?? string.Empty,
                _messageStore);

            // IsDatabaseConnected is derived from the model so notify the view in case it changed.
            OnPropertyChanged(nameof(IsDatabaseConnected));

            // Let the sheets panel rebuild its filtered view from the refreshed database data.
            _sheetsPanelViewModel.OnDatabaseRefreshed();
        }

        #endregion Database Refresh
    }
}
