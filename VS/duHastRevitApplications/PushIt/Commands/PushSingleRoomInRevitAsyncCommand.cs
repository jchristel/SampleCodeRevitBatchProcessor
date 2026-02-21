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


using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.Utilities;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Windows.Input;

namespace duHastNet.PushIt.Commands
{
    public class PushSingleRoomInRevitAsyncCommand
    {
        private readonly ViewModels.RoomsMainViewModel _roomsMainViewModel;
        private readonly ViewModels.RoomsDataGridViewModel _roomsDataGridViewModel;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly AsyncRelayCommand _command;

        public ICommand Command => _command;

        private bool CanExecute()
        {
            if (_roomsMainViewModel.IsWaitingForRevitCommandToFinish)
            {
                return false;
            }
            else if (_roomsDataGridViewModel.SelectedRoom == null)
            {
                return false;
            }
            // if push mode is split and a room has been pushed already allow split mode
            // don't allow split mode on a new room
            else if (_roomsMainViewModel.PushOperationMode == PushMode.Split &&
                !_roomsDataGridViewModel.IsMatchingRevitRoomsEmpty &&
                !Utilities.PushModeUtils.IsNewRoomMode(_roomsDataGridViewModel.SelectedRoom.Id.Value))
            {
                return true;
            }
            // if push mode is new allow push mode
            else if (_roomsMainViewModel.PushOperationMode == PushMode.New)
            {
                return true;
            }
            // if standard push mode check if a room is selected
            else if (_roomsMainViewModel.PushOperationMode == PushMode.Push &&
                _roomsDataGridViewModel.IsMatchingRevitRoomsEmpty)
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        private async System.Threading.Tasks.Task Execute()
        {
            //deactivate the ui
            _roomsMainViewModel.IsWaitingForRevitCommandToFinish = true;

            try
            {
                (string message, Utils.WPF.Stores.MessageTypes messageType) = await RevitTask.RunAsync(
                    app =>
                    {
                        //Run Revit API code here

                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            //check if there is a room to push
                            if (_roomsDataGridViewModel.SelectedRoom == null)
                            {
                                return ("No room selected in the user interface to push to Revit.", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            //check what is selected in the UI
                            UIDocument uidoc = app.ActiveUIDocument;

                            // get the selected element ids
                            List<ElementId> selectedElementIds = [.. uidoc.Selection.GetElementIds()];
                            // check quantity of selected elements
                            if (selectedElementIds.Count == 0)
                            {
                                return ("No room selected in the Revit model to push to.", Utils.WPF.Stores.MessageTypes.Error);
                            }
                            else if (selectedElementIds.Count > 1)
                            {
                                return ("More than one room selected in the Revit model to push to.", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            //get the selected Element from Revit
                            Element selectedElement = doc.GetElement(selectedElementIds.First());
                            // check if the selected element is of a supported category (or has category to start with)
                            if (selectedElement.Category == null || !_revitDataModel.GetEnabledCategoryNames().Contains(selectedElement.Category.Name))
                            {
                                string supportedCategories = string.Join(", ", _revitDataModel.GetEnabledCategoryNames());
                                return ($"The selected element is not of a supported category. Supported categories are: [{supportedCategories}].", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            //check all parameters still exist before pushing data
                            VerifyParametersInModel actionVerify = new(_revitDataModel);
                            (string messageActionVerify, Utils.WPF.Stores.MessageTypes messageActionTypeVerify) = actionVerify.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionVerify.GetLogMessagesAndLogTypes());

                            //only proceed if all parameters are verified
                            if (messageActionTypeVerify == MessageTypes.Error)
                            {
                                return (messageActionVerify, messageActionTypeVerify);
                            }

                            // Execute the action to push a single room to the Revit model
                            PushSingleRoomDataToRevit action = new(
                                revitModel: _revitDataModel,
                                roomToPush: _roomsDataGridViewModel.SelectedRoom,
                                pushTarget: selectedElement,
                                roomsMainViewModel: _roomsMainViewModel
                            );

                            (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) = action.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            // return the message to the caller
                            return (messageAction, messageActionType);

                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the external event handler update after push single room event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                        }
                    });

                if (messageType == MessageTypes.Information)
                {
                    // raise event to notify the view model that the model has been updated
                    _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
                }

                //pop message to user
                _roomsMainViewModel.AddMessage(message, messageType);
            }
            catch (Exception ex)
            {
                _roomsMainViewModel.AddMessage(ex.Message, MessageTypes.Error);
            }
            finally
            {
                //activate the ui
                _roomsMainViewModel.IsWaitingForRevitCommandToFinish = false;
            }
        }

        private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(ViewModels.RoomsDataGridViewModel.IsMatchingRevitRoomsEmpty) ||
                e.PropertyName == nameof(ViewModels.RoomsMainViewModel.IsWaitingForRevitCommandToFinish) ||
                e.PropertyName == nameof(ViewModels.RoomsMainViewModel.PushOperationMode))
            {
                _command.NotifyCanExecuteChanged();
            }
        }

        public PushSingleRoomInRevitAsyncCommand(
            ViewModels.RoomsMainViewModel roomsMainViewModel,
            ViewModels.RoomsDataGridViewModel roomsDataGridViewModel,
            Models.RevitDataModel revitDataModel
            )
        {
            _revitDataModel = revitDataModel;
            _roomsMainViewModel = roomsMainViewModel;
            _roomsDataGridViewModel = roomsDataGridViewModel;
            _command = new AsyncRelayCommand(Execute, CanExecute);
            _roomsMainViewModel.PropertyChanged += OnViewModelPropertyChanged;
            _roomsDataGridViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}