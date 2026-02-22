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
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Stores;
using System;
using System.Windows.Input;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public partial class ParametersSelectionViewModel : AppViewModelBase
    {
        private readonly NavigationStore _navigationStore;
        private readonly StateStore _stateStore;
        private readonly MessageStore _messageStore;
        private readonly Models.RevitFamiliesDataModel _revitDataModel;
        private readonly Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// View model managing the parameters data grid.
        /// </summary>
        public ViewModels.ParametersDataGridViewModel ParametersDataGridViewModel { get; }

        #region loading datagrid overlay properties

        [ObservableProperty]
        private bool _isGridBusy;

        [ObservableProperty]
        private string _loadingMessage = "Busy...";

        #endregion loading datagrid overlay properties

        //command to navigate back to families selection view model
        private readonly Commands.LeaveParameterSelectionCommand _navigateCommand;

        /// <summary>
        /// Flag indicating whether the view model is waiting for a Revit command to finish.
        /// Side effect: also drives the loading overlay via IsGridBusy.
        /// </summary>
        [ObservableProperty]
        private bool _isWaitingForRevitCommandToFinish;

        partial void OnIsWaitingForRevitCommandToFinishChanged(bool value)
        {
            IsGridBusy = value;
        }

        #region Commands

        // Command property delegates to the .Command property on the command object,
        // since the command class wraps RelayCommand internally rather than implementing ICommand directly.
        public ICommand SelectFamilies => _navigateCommand.Command;

        #endregion Commands


        /// <summary>
        /// Adds a message to the global message store which will then be displayed in the UI.
        /// </summary>
        /// <param name="message">The message text.</param>
        /// <param name="messageType">The type/severity of the message.</param>
        public void AddMessage(string message, Utils.WPF.Stores.MessageTypes messageType)
        {
            if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Error)
            {
                //let user dismiss the message themselves for error messages, since they might want to copy the message text for further use, and errors are more important to see for a longer time
                _messageStore.EnqueueMessage(message, messageType);
            }
            else if (messageType == duHastNet.Utils.WPF.Stores.MessageTypes.Information)
            {
                //just flash message to user for information messages, since they are less important and user might not need to copy the message text, and it is better to dismiss them after a short time to avoid too many messages building up in the UI
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 2);
            }
            else
            {
                //default to short display time for other message types
                _messageStore.EnqueueMessage(message, messageType, dismissAfterSeconds: 5);
            }
        }


        /// <summary>
        /// Custom closing logic for ParametersSelectionViewModel.
        /// Saves grid and navigation state before handing off to base cleanup.
        /// </summary>
        public override void OnClosing()
        {
            //update the column ids in settings.
            _revitDataModel.Settings.ColumnIds.Clear();
            foreach (var columnId in ParametersDataGridViewModel.ColumnDefinitions)
            {
                _revitDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            //save the state of the data grid view model
            if (ParametersDataGridViewModel != null && _stateStore != null)
            {
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
                }
            }

            // Get states from StateStore for settings persistence
            var statesForSettings = _stateStore.GetStatesForSettings();
            _revitDataModel.Settings.NavigationStates = statesForSettings;

            // GlobalMessageViewModel and ParametersDataGridViewModel are registered via RegisterChild()
            // and will be disposed automatically by base.OnClosing() — do not dispose manually here.
            base.OnClosing();
        }


        /// <summary>
        /// Loads any existing states from settings into the state store.
        /// </summary>
        private void ApplyStateFromSettings()
        {
            if (_revitDataModel.Settings.NavigationStates != null && _revitDataModel.Settings.NavigationStates.Count > 0)
            {
                _stateStore.LoadStatesFromSettings(_revitDataModel.Settings.NavigationStates, () => new DataGridState());
                System.Diagnostics.Debug.WriteLine($"Loaded {_revitDataModel.Settings.NavigationStates.Count} states from settings into StateStore");
            }
        }

        /// <summary>
        /// The parameters selection view model constructor.
        /// </summary>
        /// <param name="revitDataModel">The underlying revit data model.</param>
        /// <param name="navigationStore">A navigation store for the UI.</param>
        /// <param name="stateStore">A state store for grid state persistence.</param>
        /// <param name="messageStore">A message store used to display messages to the user.</param>
        /// <param name="globalMessageViewModel">A message view model the message store uses to display messages to the user.</param>
        /// <param name="createViewModel">Factory function to create the FamiliesSelectionViewModel for navigation.</param>
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
            RegisterChild(GlobalMessageViewModel);

            //load settings first
            ApplyStateFromSettings();

            //parameters data grid view model
            ParametersDataGridViewModel = new ParametersDataGridViewModel(revitDataModel: revitDataModel);
            RegisterChild(ParametersDataGridViewModel);

            //command to navigate back to families selection view model
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