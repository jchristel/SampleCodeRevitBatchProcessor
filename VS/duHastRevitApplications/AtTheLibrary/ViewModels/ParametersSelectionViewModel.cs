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


using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using System;
using System.Windows.Input;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public class ParametersSelectionViewModel : Utils.WPF.ViewModels.ViewModelBase
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
        public ViewModels.ParametersDataGridViewModel ParametersDataGridViewModel { get; }

        //command to navigate back to families selection view model
        private readonly Commands.LeaveParameterSelectionCommand _navigateCommand;


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

        #region Commands

        //commands
        // switch to families selection view model
        public ICommand SelectFamilies { get { return _navigateCommand; } }

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
        /// Custom closing logic for ParametersSelectionViewModel
        /// Disposes all external events from the event manager
        /// save the state of the data grid view model
        /// </summary>
        public override void OnClosing()
        {

            //update the column ids in settings.
            // clear list first
            _revitDataModel.Settings.ColumnIds.Clear();
            // add current list
            foreach (var columnId in ParametersDataGridViewModel.ColumnDefinitions)
            {
                _revitDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }


            //save the state of the data grid view model
            if (ParametersDataGridViewModel != null && _stateStore != null)
            {
                //save the state
                try
                {
                    var currentState = ParametersDataGridViewModel.CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        _stateStore.SaveState(ParametersDataGridViewModel, currentState);
                        System.Diagnostics.Debug.WriteLine($"Forced save of grid state for {ParametersDataGridViewModel.GetGridStateId()} before closing");
                    }
                }
                catch (Exception stateEx)
                {
                    System.Diagnostics.Debug.WriteLine($"Error forcing state save: {stateEx.Message}");
                    //_familyDataGridViewModel.AddMessage($"Warning: Could not save grid state: {stateEx.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }
            }

            // Get states from StateStore for settings persistence
            var statesForSettings = _stateStore.GetStatesForSettings();
            _revitDataModel.Settings.NavigationStates = statesForSettings;

            GlobalMessageViewModel.Dispose();

            base.OnClosing();
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
        public ParametersSelectionViewModel(
            Models.RevitFamiliesDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.StateStore stateStore,
            Utils.WPF.Stores.MessageStore messageStore,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel,
            Func<ViewModels.FamiliesSelectionViewModel> createViewModel
            )
        {
            //store services
            _navigationStore = navigationStore;
            _stateStore = stateStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel); // Register as child

            //load settings first
            ApplyStateFromSettings();

            //push it data grid view model
            ParametersDataGridViewModel = new ParametersDataGridViewModel(revitDataModel: revitDataModel);
            RegisterChild(ParametersDataGridViewModel);

            //view model switch to families selection view model
            _navigateCommand = new Commands.LeaveParameterSelectionCommand(
                navigationStore: _navigationStore,
                stateStore: _stateStore,
                createViewModel: createViewModel,
                parametersDataGridViewModel: ParametersDataGridViewModel,
                revitFamiliesDataModel: revitDataModel
            );
        }
    }
}
