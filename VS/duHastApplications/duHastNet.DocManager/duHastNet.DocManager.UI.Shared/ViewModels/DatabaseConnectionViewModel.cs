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
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.ComponentModel.DataAnnotations;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    public partial class DatabaseConnectionViewModel : ObservableValidator
    {
        /// <summary>
        /// view model class for the current folder model
        /// </summary>
        #region Private Fields

        private readonly DocManagerApi _docManagerApi;
        private readonly MessageStore _messageStore;
        private readonly Manager _manager;
        private readonly IDialogService _dialogService;

        #endregion Private Fields

        #region Constructor

        public DatabaseConnectionViewModel(
            DocManagerApi docManagerApi,
            MessageStore messageStore,
            Manager manager,
            IDialogService dialogService)
        {
            _docManagerApi = docManagerApi;
            _manager = manager;
            _messageStore = messageStore;
            _dialogService = dialogService;

            // Load current state from DocManagerApi
            InitializeFromApi();

            // Validate all properties on startup to show initial validation state
            ValidateAllProperties();
        }

        /// <summary>
        /// Initializes ViewModel state from DocManagerApi
        /// Loads database path and connection status
        /// </summary>
        private void InitializeFromApi()
        {
            // Load database path if one is currently connected
            var currentPath = _docManagerApi.GetDatabasePath();

            // get out if no path
            if (string.IsNullOrEmpty(currentPath))
            {
                return;
            }

            // store current path
            DatabasePath = currentPath;
            
            // Set connection status based on whether database is ready
            IsConnected = _docManagerApi.IsDatabaseReady();

            // If connected, initialize custom fields
            if (IsConnected && _manager.IsDataLoaded)
            {
                InitializeCustomFields();
            }
        }

        #endregion Constructor

        #region Observable Properties

        [ObservableProperty]
        [CustomValidation(typeof(DatabaseConnectionViewModel), nameof(ValidateDatabaseConnection))]
        private string _databasePath = string.Empty;

        [ObservableProperty]
        private string _statusMessage = "Ready";

        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(IsCustomFieldsExpanded))]
        [NotifyCanExecuteChangedFor(nameof(AddCustomFieldCommand))]
        private bool _isConnected = false;

        [ObservableProperty]
        private bool _isBusy = false;

        [ObservableProperty]
        private bool _isCreateDatabaseEnabled = true;

        [ObservableProperty]
        private bool _isConnectDatabaseEnabled = true;

        [ObservableProperty]
        private bool _isBrowseEnabled = true;

        [ObservableProperty]
        private bool _isImportExportEnabled = false;

        [ObservableProperty]
        private int _loadedDocumentCount = 0;

        [ObservableProperty]
        private int _loadedRevisionCount = 0;

        [ObservableProperty]
        private int _customPropertyCount = 0;

        #endregion

        #region Validation

        /// <summary>
        /// Validates the database connection state
        /// Requires a database to be connected before settings can be saved
        /// </summary>
        public static ValidationResult? ValidateDatabaseConnection(string? value, ValidationContext context)
        {
            var viewModel = context.ObjectInstance as DatabaseConnectionViewModel;
            if (viewModel == null)
                return ValidationResult.Success;

            // Must be connected to a database
            if (!viewModel.IsConnected)
            {
                return new ValidationResult("Database must be connected");
            }

            // If connected, validate the path format
            if (!string.IsNullOrWhiteSpace(value))
            {
                if (!viewModel.IsValidDatabasePath(value))
                {
                    return new ValidationResult("Database path is invalid or cannot be created");
                }
            }

            return ValidationResult.Success;
        }

        #endregion Validation

        #region Computed Properties

        /// <summary>
        /// Gets whether database operations are available
        /// </summary>
        public bool IsDatabaseReady => _docManagerApi.IsDatabaseReady();

        /// <summary>
        /// Gets the current database path from the API
        /// </summary>
        public string? CurrentDatabasePath => _docManagerApi.GetDatabasePath();

        /// <summary>
        /// Gets whether data is loaded into the Manager
        /// </summary>
        public bool IsDataLoaded => _manager.IsDataLoaded;

        #endregion
    }
}
