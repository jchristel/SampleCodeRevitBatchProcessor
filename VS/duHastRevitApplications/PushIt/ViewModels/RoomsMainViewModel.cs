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


using duHastNet.PushIt.Utilities;
using duHastNet.UI.CustomControls;
using duHastNet.Utils.WPF.Commands;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Linq;
using System.Windows.Input;

namespace duHastNet.PushIt.ViewModels
{
    public class RoomsMainViewModel : Utils.WPF.ViewModels.ViewModelBase, INotifyDataErrorInfo
    {
        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly Utils.WPF.ViewModels.ErrorsViewModel _errorsViewModel;

        // the global message view model
        public Utils.WPF.ViewModels.GlobalMessageViewModel GlobalMessageViewModel { get; }

        /// <summary>
        /// View model managing the supported categories data grid.
        /// </summary>
        public duHastNet.PushIt.ViewModels.SupportedCatgeoriesDataGridViewModel SupportedCategoriesDataGridViewModel { get; }

        /// <summary>
        /// View model managing push it data grid
        /// </summary>
        public duHastNet.PushIt.ViewModels.RoomsDataGridViewModel RoomsDataGridViewModel { get; }


        private string _activeDesignSetName = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME;
        private string _activeDesignOptionName = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME;

        //command to raise an event to refresh the gui
        private readonly Commands.RefreshUIFromRevitModelAsyncCommand _raiseRefreshGUICommand;
        //command to push a single room to revit
        private readonly Commands.PushSingleRoomInRevitAsyncCommand _raisePushSingleRoomCommand;
        //command to raise an event to reload data from file path
        private readonly Commands.ReloadDataFromFileAsyncCommand _raiseReloadDataCommand;
        //command to highlight a room in Revit
        private readonly Commands.HighlightRoomsInRevitAsyncCommand _highLightRoomCommand;
        //command to wipe stale rooms data
        private readonly Commands.WipeStaleDataRevitAsyncCommand _wipeStaleRoomsDataCommand;
        //command to update from changed categories
        private readonly Commands.UpdateFromChangedCategoriesAsyncCommand _updateFromChangedCategoriesCommand;
        //command to update all rooms in revit from data model
        private readonly Commands.PushAllRoomsInRevitAsyncCommand _updateAllRoomsCommand;
        //command to update the view model if the column order changes
       
        //command to wipe selected rooms in revit
        private readonly Commands.WipeSelectedRevitRoomInstancesAsyncCommand _wipeSelectedRoomDataCommand;
        //command to save data to csv file
        private readonly Commands.SaveRoomDataAsyncCommand _saveDataCommand;

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

        #region push modus

        //three way control setting the operation modus
        private ThreeWaySwitch.SwitchState _switchState;

        /// <summary>
        /// property containing the three possible operation modi
        /// </summary>
        public ThreeWaySwitch.SwitchState SwitchState
        {
            get => _switchState;
            set
            {
                if (_switchState != value)
                {
                    _switchState = value;

                    if (_switchState == ThreeWaySwitch.SwitchState.Left)
                    {
                        PushItButtonText = "Push It";
                        PushOperationMode = PushIt.Utilities.PushMode.Push;
                    }
                    else if (_switchState == ThreeWaySwitch.SwitchState.Centre)
                    {
                        PushItButtonText = "Split It";
                        PushOperationMode = PushMode.Split;
                    }
                    else
                    {
                        PushItButtonText = "Create New";
                        PushOperationMode = PushIt.Utilities.PushMode.New;
                    }

                    OnPropertyChanged(nameof(SwitchState));
                }
            }
        }

        /// the mode of operation for the push it command (push, push and split, push and  new)
        private PushIt.Utilities.PushMode _pushOperationMode;

        /// <summary>
        /// property to set the push operation mode through the three way switch
        /// some commands are checking this value to work out whether they can exceute!
        /// </summary>
        public PushIt.Utilities.PushMode PushOperationMode
        {
            get => _pushOperationMode;

            set
            {
                _pushOperationMode = value;

                //notify commands of change
                OnPropertyChanged(nameof(PushOperationMode));
            }
        }

        //default button text for push it mode
        string _pushItButtonText = "Push It";

        //button text for push it mode
        public string PushItButtonText
        {
            get => _pushItButtonText;
            set
            {
                _pushItButtonText = value;
                OnPropertyChanged(nameof(PushItButtonText));
            }
        }

        #endregion push modus

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


        // the currently active design set name
        public string ActiveDesignSetName
        {
            get => _activeDesignSetName;
            set
            {
                _activeDesignSetName = value;
                OnPropertyChanged(nameof(ActiveDesignSetName));
            }
        }

        // the currently active design option name
        public string ActiveDesignOptionName
        {
            get => _activeDesignOptionName;
            set
            {
                _activeDesignOptionName = value;
                OnPropertyChanged(nameof(ActiveDesignOptionName));
            }
        }

        #endregion settings

        #region user selection


        private bool _saveFilePathValid;
        public bool SaveFilePathValid
        {
            get => _saveFilePathValid;
            set
            {
                _saveFilePathValid = value;
                OnPropertyChanged(nameof(SaveFilePathValid));
            }
        }

        private string _saveFilePath;
        public string SaveFilePath
        {
            get => _saveFilePath;
            set
            {
                _saveFilePath = value;
                // check if the file path is valid, if not add an error
                if (string.IsNullOrEmpty(value))
                {
                    // set the data path to invalid
                    SaveFilePathValid = false;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(SaveFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.AddError(nameof(SaveFilePath), "Save file path cannot be empty");
                    AddMessage($"Save file path cannot be empty: {value}", Utils.WPF.Stores.MessageTypes.Error);
                }
                else
                {
                    // set the data path to valid
                    SaveFilePathValid = true;
                    // this will trigger data validation, which in turn will eventually call OnPropertyChanged(nameof(SaveFilePathValid))
                    // from the eventhandler ErrorsViewModel_ErrorsChanged
                    _errorsViewModel.ClearErrors(nameof(SaveFilePath));
                    //excute the command to save data if set up
                    if (SaveDataCommand is null == false)
                    {
                        SaveDataCommand.Execute(null);
                    }
                }

                OnPropertyChanged(nameof(SaveFilePath));
            }
        }
        
        #endregion user selection

        #region Commands

        //commands
        public ICommand RefreshGUICommand { get { return _raiseRefreshGUICommand; } }
        public ICommand PushSingleRoomCommand { get { return _raisePushSingleRoomCommand; } }
        public ICommand ReloadDataCommand { get { return _raiseReloadDataCommand; } }
        public ICommand HighLightRoomCommand { get { return _highLightRoomCommand; } }
        public ICommand WipeStaleRoomsDataCommand { get { return _wipeStaleRoomsDataCommand; } }
        public ICommand UpdateFromChangedCategoriesCommand { get { return _updateFromChangedCategoriesCommand; } }
        public ICommand UpdateAllRoomsCommand { get { return _updateAllRoomsCommand; } }
        public ICommand WipeSelectedRoomDataCommand { get { return _wipeSelectedRoomDataCommand; } }
        public ICommand SaveDataCommand { get { return _saveDataCommand; } }

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
            foreach (var columnId in RoomsDataGridViewModel.ColumnDefinitions)
            {
                _revitDataModel.Settings.ColumnIds.Add(columnId.PropertyName);
            }

            // close any child view models
            base.OnClosing();

            GlobalMessageViewModel.Dispose();

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
        /// The rooms selection view model class constructor.
        /// </summary>
        /// <param name="revitDataModel">The underlying revit data model</param>
        /// <param name="navigationStore">A navigation store for the UI</param>
        /// <param name="messageStore">A message store used to display messages to the user</param>
        /// <param name="globalMessageViewModel">A message view model, the message store uses to display messages to the user.</param>
        public RoomsMainViewModel(
            Models.RevitDataModel revitDataModel,
            Utils.WPF.Stores.NavigationStore navigationStore,
            Utils.WPF.Stores.MessageStore messageStore,
            Utils.WPF.ViewModels.GlobalMessageViewModel globalMessageViewModel)
        {
            //store services
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;

            //initialize the errors view model
            _errorsViewModel = new Utils.WPF.ViewModels.ErrorsViewModel();
            
            //subscribe to errors changed event
            _errorsViewModel.ErrorsChanged += ErrorsViewModel_ErrorsChanged;

            //store the global message view model
            GlobalMessageViewModel = globalMessageViewModel;
            RegisterChild(GlobalMessageViewModel); // Register as child

            // supported categories data grid view model
            SupportedCategoriesDataGridViewModel = new SupportedCatgeoriesDataGridViewModel(revitDataModel: revitDataModel);
            RegisterChild(SupportedCategoriesDataGridViewModel);

            //push it data grid view model
            RoomsDataGridViewModel  = new RoomsDataGridViewModel(revitDataModel: revitDataModel);
            RegisterChild(RoomsDataGridViewModel);

            //set the data file path
            DataFilePath = _revitDataModel.Settings.DataPath;

            // set up commands
            // refresh gui with data from model
            _raiseRefreshGUICommand = new Commands.RefreshUIFromRevitModelAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel);
            // push single room to revit
            _raisePushSingleRoomCommand = new Commands.PushSingleRoomInRevitAsyncCommand(
                roomsMainViewModel: this,
                roomsDataGridViewModel: RoomsDataGridViewModel,
                revitDataModel: _revitDataModel
             );
            //load data from file path
            _raiseReloadDataCommand = new Commands.ReloadDataFromFileAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel
            );
            //highlight room in Revit
            _highLightRoomCommand = new Commands.HighlightRoomsInRevitAsyncCommand(
                roomsMainViewModel: this,
                roomsDataGridViewModel: RoomsDataGridViewModel,
                revitDataModel: _revitDataModel
            );
            //wipe stale rooms data
            _wipeStaleRoomsDataCommand = new Commands.WipeStaleDataRevitAsyncCommand(
                roomsSelectionViewModel: this,
                revitDataModel: _revitDataModel
            );
            //update from changed categories
            _updateFromChangedCategoriesCommand = new Commands.UpdateFromChangedCategoriesAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel
            );
            //update all rooms in revit from data model
            _updateAllRoomsCommand = new Commands.PushAllRoomsInRevitAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel
            );
            
            //wipe selected rooms in revit
            _wipeSelectedRoomDataCommand = new Commands.WipeSelectedRevitRoomInstancesAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel
            );
            //save data to file command
            _saveDataCommand = new Commands.SaveRoomDataAsyncCommand(
                roomsMainViewModel: this,
                revitDataModel: _revitDataModel
            );

            // set the default push operation mode to push
            _pushOperationMode = PushIt.Utilities.PushMode.Push;

            //update rooms data with data from revit through an external event
            RefreshGUICommand.Execute(null);
        }
    }
}
