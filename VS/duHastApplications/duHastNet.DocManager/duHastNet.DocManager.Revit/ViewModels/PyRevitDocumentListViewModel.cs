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
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.ViewModels
{
    /// <summary>
    /// ViewModel for displaying documents from a hardcoded database path in PyRevit
    /// Demonstrates integration of DocManagerSync API with WPF using Community Toolkit MVVM
    /// </summary>
    public partial class PyRevitDocumentListViewModel : ObservableObject
    {
        #region Private Fields

        private readonly DocManagerApi _docManagerApi;
        private const string HARDCODED_DATABASE_PATH = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager.Standalone.Tests\DataBaseTests\20251201_02.db";
        private duHastNet.UI.DocManagerSettingsUI.Utils.Settings? _revitSettings;
        private Utilities.UISettings.UISettings? _uiSettings;


        #endregion Private Fields

        #region Constructor

        /// <summary>
        /// Initializes the ViewModel with DocManager API
        /// </summary>
        public PyRevitDocumentListViewModel(duHastNet.UI.DocManagerSettingsUI.Utils.Settings revitSettings, Utilities.UISettings.UISettings uiSettings)
        {
            _docManagerApi = new DocManagerApi();
            Documents = new ObservableCollection<DocumentViewModel>();
            _revitSettings = revitSettings;
            _uiSettings = uiSettings;

            //populate database path from settings if available, otherwise use hardcoded path
            if (_revitSettings != null && !string.IsNullOrEmpty( _revitSettings.DatabasePath))
            {
                _databasePath = _revitSettings.DatabasePath;
            }
            else            {
                _databasePath = HARDCODED_DATABASE_PATH;
            }
        }

        #endregion Constructor

        #region Observable Properties

        [ObservableProperty]
        private ObservableCollection<DocumentViewModel> _documents;

        [ObservableProperty]
        private string _statusMessage = "Ready";

        [ObservableProperty]
        private bool _isLoading = false;

        [ObservableProperty]
        private int _totalDocuments = 0;

        [ObservableProperty]
        private string _databasePath;

        [ObservableProperty]
        private bool _isDatabaseConnected = false;

        #endregion Observable Properties

        #region Commands

        /// <summary>
        /// Command to load documents from the hardcoded database
        /// Uses synchronous DocManagerSync methods for IronPython compatibility
        /// </summary>
        [RelayCommand]
        private void LoadDocuments()
        {
            try
            {
                IsLoading = true;
                StatusMessage = $"Connecting to database: {DatabasePath}";
                Documents.Clear();

                // Connect to hardcoded database path using synchronous method
                var connectionResult = _docManagerApi.ConnectDatabase(DatabasePath);

                if (!connectionResult.Success)
                {
                    StatusMessage = $"Failed to connect: {connectionResult.Message}";
                    IsDatabaseConnected = false;
                    return;
                }

                IsDatabaseConnected = true;
                StatusMessage = "Database connected. Loading documents...";

                // Get all documents using synchronous method
                var documents = _docManagerApi.GetActiveDocuments();// GetAllDocuments();

                // Convert to ViewModels and add to collection
                foreach (var doc in documents)
                {
                    Documents.Add(new DocumentViewModel(doc));
                }

                TotalDocuments = Documents.Count;
                StatusMessage = $"Loaded {TotalDocuments} documents successfully";
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error: {ex.Message}";
                IsDatabaseConnected = false;
            }
            finally
            {
                IsLoading = false;
            }
        }

        /// <summary>
        /// Command to refresh the document list
        /// </summary>
        [RelayCommand(CanExecute = nameof(CanRefresh))]
        private void Refresh()
        {
            LoadDocuments();
        }

        private bool CanRefresh() => IsDatabaseConnected && !IsLoading;

        /// <summary>
        /// Command to close and cleanup database connection
        /// </summary>
        [RelayCommand]
        private void Close()
        {
            try
            {
                if (IsDatabaseConnected)
                {
                    _docManagerApi.Close();//  CloseDatabase();
                    IsDatabaseConnected = false;
                    Documents.Clear();
                    TotalDocuments = 0;
                    StatusMessage = "Database connection closed";
                }
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error closing database: {ex.Message}";
            }
        }

        #endregion Commands
    }

    /// <summary>
    /// ViewModel wrapper for Document entity
    /// Provides display-friendly properties for DataGrid binding
    /// </summary>
    public partial class DocumentViewModel : ObservableObject
    {
        private readonly Document _document;

        public DocumentViewModel(Document document)
        {
            _document = document ?? throw new ArgumentNullException(nameof(document));
        }

        public int Id => _document.Id;
        
        public string Number => _document.Number;
        
        public string Name => _document.Name;
        
        public string Revision => _document.Revision;
        
        public int RevisionId => _document.RevisionId;

        public bool IsActive => _document.IsActive;

        /// <summary>
        /// Display text combining number and name
        /// </summary>
        public string DisplayText => $"{Number} - {Name}";

        /// <summary>
        /// Status display text
        /// </summary>
        public string Status => IsActive ? "Active" : "Inactive";
    }
}
