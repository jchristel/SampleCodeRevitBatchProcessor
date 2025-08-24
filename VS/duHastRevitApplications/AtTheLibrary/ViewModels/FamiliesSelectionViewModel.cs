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


using duHastNet.AtTheLibrary.Commands;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using System;
using System.Collections;
using System.ComponentModel;
using System.Windows.Input;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public class FamiliesSelectionViewModel : Utils.WPF.ViewModels.ViewModelBase, INotifyDataErrorInfo
    {
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.StateStore _stateStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Models.RevitFamiliesDataModel _revitDataModel;
        private readonly Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }


        /// <summary>
        /// View model managing push it data grid
        /// </summary>
        public ViewModels.FamiliesDataGridViewModel FamiliesDataGridViewModel { get; }


        //command to raise an event to refresh the gui
        private readonly Commands.RefreshUIFromRevitModelAsyncCommand _raiseRefreshGUICommand;
        //command to raise an event to reload data from file path
        private readonly Commands.ReloadDataFromFileAsyncCommand _raiseReloadDataCommand;
        //command to load family from file path
        private readonly Commands.LoadFamilyAsyncCommand _loadFamilyCommand;
        //command to open family into revit
        private readonly Commands.OpenFamilyIntoUIAsyncCommand _openFamilyCommand;
        //command to navigate to parameters selction view model
        private readonly Commands.NavigateCommand _navigateCommand;
        //command to navigate to catalogue file editor view model
        private readonly Commands.OpenTypeFileEditorCommand _navigateEditTypeCatalogueFileCommand;

        //property to check if there are any errors
        public bool HasErrors => _errorsViewModel.HasErrors;
        // event handler for errors changed
        public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;

        // flag indicating whether the view model is waiting for a Revit command to finish
        private bool _isWaitingForRevitCommandToFinish;
        public bool IsWaitingForRevitCommandToFinish
        {
            get => _isWaitingForRevitCommandToFinish;
            set
            {
                _isWaitingForRevitCommandToFinish = value;
                OnPropertyChanged(nameof(IsWaitingForRevitCommandToFinish));
            }
        }

        #region settings

        private string _dataFilePath;
        public string DataFilePath
        {
            get => _dataFilePath;
            set
            {
                _dataFilePath = value;

                _errorsViewModel.ClearErrors(nameof(DataFilePath));

                // check if the file path is valid, if not add an error
                if (string.IsNullOrEmpty(value))
                {
                    // set the data path to invalid
                    DataFilePathValid = false;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.AddError(nameof(DataFilePath), "Data file path cannot be empty");
                }
                else if (!System.IO.File.Exists(value))
                {
                    // set the data path to invalid
                    DataFilePathValid = false;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.AddError(nameof(DataFilePath), "Data file path does not exist");
                }
                else
                {
                    // set the data path to valid
                    DataFilePathValid = true;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(DataFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.ClearErrors(nameof(DataFilePath));

                    // update the data path in the settings
                    _revitDataModel.Settings.DataPath = value;
                }

                // call ui update
                OnPropertyChanged(nameof(DataFilePath));

            }
        }

        private bool _dataFilePathValid;
        public bool DataFilePathValid
        {
            get => _dataFilePathValid;
            set
            {
                _dataFilePathValid = value;
                // call ui update
                OnPropertyChanged(nameof(DataFilePathValid));
            }
        }


        #endregion settings

        #region Commands

        //commands
        public ICommand RefreshGUICommand { get { return _raiseRefreshGUICommand; } }
        public ICommand ReloadDataCommand { get { return _raiseReloadDataCommand; } }
        public ICommand LoadFamilyCommand { get { return _loadFamilyCommand; } }
        public ICommand SelectParameters { get { return _navigateCommand; } }
        public ICommand OpenFamilyIntoUICommand { get { return _openFamilyCommand; } }
        public ICommand EditTypeCatalogueFileCommand { get { return _navigateEditTypeCatalogueFileCommand; } }

        #endregion Commands


        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI
        /// </summary>
        /// <param name="message"></param>
        /// <param name="messageType"></param>
        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {

            _messageStore.SetCurrentMessage(message, messageType);
        }


        // not sure whether this is actually required or not
        // when on closing, dispose of the event manager
        // and remove the event handler
        public override void Dispose()
        {
            base.Dispose();
        }


        /// <summary>
        /// Custom closing logic for RoomsSelectionViewModel
        /// Disposes all external events from the event manager
        /// </summary>
        public override void OnClosing()
        {

            //unsubscribe from errors changed event
            _errorsViewModel.ErrorsChanged -= ErrorsViewModel_ErrorsChanged;

            //update the column ids in settings.
            // clear list first
            _revitDataModel.Settings.ColumnIds.Clear();
            // add current list
            foreach (var columnId in FamiliesDataGridViewModel.ColumnDefinitions)
            {
                _revitDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            //clear the enabled column list
            _revitDataModel.Settings.EnabledTypeParameterNames.Clear();
            foreach (var enabledParameter in _revitDataModel.GetAllEnabeledParameterNames())
            {
                _revitDataModel.Settings.EnabledTypeParameterNames.Add(enabledParameter);
            }

            // clear the shown in UI column list ( this appears to be a duplicate to the column ID list?)
            _revitDataModel.Settings.ShownTypeParameterNames.Clear();
            foreach (var shownParameter in _revitDataModel.GetAllShownParameterNames())
            {
                _revitDataModel.Settings.ShownTypeParameterNames.Add(shownParameter);
            }


            //save the varries states to settings
            // FORCE save current grid state to StateStore before getting states for settings
            if (FamiliesDataGridViewModel != null && _stateStore != null)
            {
                try
                {
                    var currentState = FamiliesDataGridViewModel.CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        _stateStore.SaveState(FamiliesDataGridViewModel, currentState);
                        System.Diagnostics.Debug.WriteLine($"Forced save of grid state for {FamiliesDataGridViewModel.GetGridStateId()} before closing");
                    }
                }
                catch (Exception stateEx)
                {
                    System.Diagnostics.Debug.WriteLine($"Error forcing state save: {stateEx.Message}");
                    AddMessage($"Warning: Could not save grid state: {stateEx.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
            }

            //TODO save parameter selection view model state ( currently this is past in as a func so not available here )


            // Get states from StateStore for settings persistence
            var statesForSettings = _stateStore.GetStatesForSettings();
            _revitDataModel.Settings.NavigationStates = statesForSettings;

            GlobalMessageViewModel.Dispose();

            base.OnClosing();
        }


        /// <summary>
        /// Data validation for text input fields
        /// </summary>
        /// <param name="propertyName">The name of the property of which to get any errors, if they exist, for.</param>
        /// <returns></returns>
        /// <exception cref="NotImplementedException"></exception>
        public IEnumerable GetErrors(string propertyName)
        {
            return _errorsViewModel.GetErrors(propertyName);
        }


        private void ErrorsViewModel_ErrorsChanged(object sender, DataErrorsChangedEventArgs e)
        {
            ErrorsChanged?.Invoke(this, e);
            // update the data file path valid property
            OnPropertyChanged(nameof(DataFilePathValid));
        }


        /// <summary>
        /// loads any existing states from settings into the state store
        /// </summary>
        private void ApplyStateFromSettings()
        {
            // Load StateStore states if they exist
            if (_revitDataModel.Settings.NavigationStates != null && _revitDataModel.Settings.NavigationStates.Count > 0)
            {
                // Create a factory for DataGridState instances
                _stateStore.LoadStatesFromSettings(_revitDataModel.Settings.NavigationStates, () => new DataGridState());
                System.Diagnostics.Debug.WriteLine($"Loaded {_revitDataModel.Settings.NavigationStates.Count} states from settings into StateStore");
            }
        }


        /// <summary>
        /// The rooms selection view model class constructor.
        /// </summary>
        /// <param name="revitDataModel">The underlying revit data model</param>
        /// <param name="navigationStore">A navigation store for the UI</param>
        /// <param name="messageStore">A message store used to display messages to the user</param>
        /// <param name="globalMessageViewModel">A message view model, the message store uses to display messages to the user.</param>
        public FamiliesSelectionViewModel(
            Models.RevitFamiliesDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.StateStore stateStore,
            Utils.WPF.Stores.MessageStore messageStore,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            Func<ViewModels.ParametersSelectionViewModel> createParameterSelectionViewModel,
            Func<Models.FamilyDataModel, ViewModels.TypeCatalogueViewModel> createTypeCatalogueViewModel)
        {
            //store services
            _navigationStore = navigationStore;
            _stateStore = stateStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;

            //initialize the errors view model
            _errorsViewModel = new Utils.WPF.ViewModels.ErrorsViewModel();
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel); // Register as child

            //load settings first
            ApplyStateFromSettings();

            //push it data grid view model
            FamiliesDataGridViewModel = new FamiliesDataGridViewModel(
                revitDataModel: revitDataModel,
                stateStore: stateStore);

            RegisterChild(FamiliesDataGridViewModel);

            //set the data file path
            DataFilePath = _revitDataModel.Settings.DataPath;

            // set up commands
            // refresh gui with data from model
            _raiseRefreshGUICommand = new Commands.RefreshUIFromRevitModelAsyncCommand(
               familiesSelectionViewModel: this,
               revitFamiliesDataModel: _revitDataModel);

            //load data from file path
            _raiseReloadDataCommand = new Commands.ReloadDataFromFileAsyncCommand(
                roomsSelectionViewModel: this,
                revitDataModel: _revitDataModel
            );

            // load family from file path
            _loadFamilyCommand = new Commands.LoadFamilyAsyncCommand(
                familiesSelectionViewModel: this,
                familiesDataGridViewModel: FamiliesDataGridViewModel,
                revitFamiliesDataModel: _revitDataModel
            );

            //open family into UI command
            _openFamilyCommand = new OpenFamilyIntoUIAsyncCommand(
                familiesSelectionViewModel: this,
                familiesDataGridViewModel: FamiliesDataGridViewModel,
                revitFamiliesDataModel: _revitDataModel);

            // navigate to parameter selection view model
            _navigateCommand = new Commands.NavigateCommand(
                navigationStore: _navigationStore,
                createViewModel: createParameterSelectionViewModel
            );

            //navigate to type editor view model command!
            _navigateEditTypeCatalogueFileCommand = new OpenTypeFileEditorCommand(
                navigationStore: _navigationStore,
                stateStore: _stateStore,
                createViewModel: (familyData) => createTypeCatalogueViewModel(familyData),
                familiesDataGridViewModel: FamiliesDataGridViewModel,
                revitFamiliesDataModel: _revitDataModel);

            //update rooms data with data from revit through an external event
            RefreshGUICommand.Execute(null);
        }
    }
}
