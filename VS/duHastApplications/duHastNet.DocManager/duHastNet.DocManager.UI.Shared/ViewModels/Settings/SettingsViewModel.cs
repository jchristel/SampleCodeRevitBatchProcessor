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
using duHastNet.DocManager.Core.Interfaces;

using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System.ComponentModel;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings;

/// <summary>
/// Main ViewModel for the Settings view - handles database configuration and management
/// Aggregates validation state from child ViewModels to control Save button
/// </summary>
public partial class SettingsViewModel : ObservableObject
{
    #region Private Fields

    private readonly IDocManagerApi _docManagerApi;
    private readonly IMessageStore _messageStore;
    private readonly IManager _manager;
    private readonly NavigationStore _navigationStore;
    private readonly ICurrentFolderManager _currentFolderManager;
    private readonly IDialogService _dialogService;

    //function used to navigate to merge view model
    private readonly Func<Merge.MergeViewModel> _createViewModel;

    //settings service
    private readonly ISettingsService _settingsService;

    #endregion

    // Expose message ViewModel for the view
    public GlobalMessageViewModel MessageViewModel { get; }

    // Expose Aconex Metadata ViewModel for the view
    public CloudDocManager.CloudDocumentManagerViewModel AconexMetadataViewModel { get; }

    // Expose current folder ViewModel for the view
    public Settings.CurrentFolder.CurrentFolderViewModel CurrentFolderViewModel { get;}

    // Expose the database connection ViewModel for the view
    public Database.DatabaseConnectionViewModel DatabaseConnectionViewModel { get;}


    #region Observable Properties

    /// <summary>
    /// Gets the path to the settings directory to be displayed in the UI only.
    /// </summary>
    [ObservableProperty]
    private string _settingsPath = "Ready";

    #endregion Observable Properties

    #region Constructor

    public SettingsViewModel(
        IDocManagerApi docManagerApi, 
        IManager manager, 
        IMessageStore messageStore, 
        ICurrentFolderManager currentFolderManager,
        NavigationStore navigationStore,
        IDialogService dialogService,
        ISettingsService settingsService,
        Func<Merge.MergeViewModel> createViewModel
        )
    {
        _docManagerApi = docManagerApi;
        _manager = manager;
        _messageStore = messageStore;
        _currentFolderManager = currentFolderManager;
        _navigationStore = navigationStore;
        _createViewModel = createViewModel;
        _dialogService = dialogService;
        //store settings service
        _settingsService = settingsService;

        MessageViewModel = new GlobalMessageViewModel(_messageStore);

        DatabaseConnectionViewModel = new Settings.Database.DatabaseConnectionViewModel(
            _docManagerApi,
            _messageStore,
            _manager,
            _dialogService);
        
        AconexMetadataViewModel = new CloudDocManager.CloudDocumentManagerViewModel(
            _messageStore, 
            _manager,
            _manager.CloudDocManager,
            _dialogService);

        CurrentFolderViewModel = new Settings.CurrentFolder.CurrentFolderViewModel(
            _messageStore,
            _manager,
            _currentFolderManager,
            _dialogService);

        // Initialize settings path to be shown in ui
        _settingsPath = _settingsService.SettingsDirectory;

        // Subscribe to child ViewModels' error state changes
        SubscribeToChildErrors();
    }

    #endregion Constructor

    #region Error Aggregation

    /// <summary>
    /// Subscribe to error state changes from all child ViewModels
    /// </summary>
    private void SubscribeToChildErrors()
    {
        // CurrentFolderViewModel - has validation with ErrorsChanged event
        CurrentFolderViewModel.ErrorsChanged += OnChildErrorsChanged;

        // DatabaseConnectionViewModel - has validation with ErrorsChanged event
        DatabaseConnectionViewModel.ErrorsChanged += OnChildErrorsChanged;

        // CloudDocumentManagerViewModel - uses computed properties, subscribe to PropertyChanged
        AconexMetadataViewModel.PropertyChanged += OnCloudDocumentManagerPropertyChanged;
    }

    /// <summary>
    /// Handles ErrorsChanged from child ViewModels with validation attributes
    /// </summary>
    private void OnChildErrorsChanged(object? sender, DataErrorsChangedEventArgs e)
    {
        // Notify that validation summary properties have changed
        OnPropertyChanged(nameof(HasAnyErrors));
        OnPropertyChanged(nameof(ErrorSummary));
        
        // Notify Save command that CanExecute state may have changed
        SaveCommand.NotifyCanExecuteChanged();
    }

    /// <summary>
    /// Handles PropertyChanged from CloudDocumentManagerViewModel
    /// Watches for HasValidationErrors property changes
    /// </summary>
    private void OnCloudDocumentManagerPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        // Only care about validation-related property changes
        if (e.PropertyName == nameof(CloudDocManager.CloudDocumentManagerViewModel.HasValidationErrors) ||
            string.IsNullOrEmpty(e.PropertyName))
        {
            OnPropertyChanged(nameof(HasAnyErrors));
            OnPropertyChanged(nameof(ErrorSummary));
            
            // Notify Save command that CanExecute state may have changed
            SaveCommand.NotifyCanExecuteChanged();
        }
    }

    /// <summary>
    /// Gets whether any child ViewModel has validation errors
    /// </summary>
    public bool HasAnyErrors
    {
        get
        {
            return CurrentFolderViewModel.HasErrors ||
                   DatabaseConnectionViewModel.HasErrors ||
                   AconexMetadataViewModel.HasValidationErrors;
        }
    }

    /// <summary>
    /// Gets summary of validation errors from all child ViewModels
    /// Format: "Cannot save: Current Folder has 2 errors, Database has 1 error"
    /// Excludes disabled sections from count
    /// </summary>
    public string ErrorSummary
    {
        get
        {
            if (!HasAnyErrors)
                return string.Empty;

            var errors = new List<string>();

            // Current Folder errors
            if (CurrentFolderViewModel.HasErrors)
            {
                var errorCount = CurrentFolderViewModel.GetErrors(null).Cast<object>().Count();
                errors.Add($"Current Folder has {errorCount} error{(errorCount != 1 ? "s" : "")}");
            }

            // Database errors
            if (DatabaseConnectionViewModel.HasErrors)
            {
                var errorCount = DatabaseConnectionViewModel.GetErrors(null).Cast<object>().Count();
                errors.Add($"Database has {errorCount} error{(errorCount != 1 ? "s" : "")}");
            }

            // Cloud Document Manager errors (only if enabled)
            if (AconexMetadataViewModel.HasValidationErrors)
            {
                var errorCount = AconexMetadataViewModel.ErrorCount;
                errors.Add($"Cloud Document Manager has {errorCount} error{(errorCount != 1 ? "s" : "")}");
            }

            return errors.Count > 0 ? $"Cannot save: {string.Join(", ", errors)}" : string.Empty;
        }
    }

    #endregion Error Aggregation

}
