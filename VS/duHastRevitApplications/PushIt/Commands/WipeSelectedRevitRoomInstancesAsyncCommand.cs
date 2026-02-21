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
    public class WipeSelectedRevitRoomInstancesAsyncCommand
    {
        private readonly ViewModels.RoomsMainViewModel _roomsMainViewModel;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly AsyncRelayCommand _command;

        public ICommand Command => _command;

        private bool CanExecute()
        {
            return !_roomsMainViewModel.IsWaitingForRevitCommandToFinish;
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
                        int wipeCounter = 0;
                        //Run Revit API code here
                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            //check what is selected in the UI
                            UIDocument uidoc = app.ActiveUIDocument;

                            // get the selected element ids
                            List<ElementId> selectedElementIds = [.. uidoc.Selection.GetElementIds()];
                            // check quantity of selected elements
                            if (selectedElementIds.Count == 0)
                            {
                                return ("No room selected in the Revit model to wipe.", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            // filter selected elements by supported categories
                            List<FamilyInstance> validElements = [];
                            string return_message = "";
                            foreach (ElementId elementId in selectedElementIds)
                            {
                                Element selectedElement = doc.GetElement(elementId);
                                // check if the selected element is of a supported category (or has category to start with)
                                if (selectedElement.Category == null || !_revitDataModel.GetEnabledCategoryNames().Contains(selectedElement.Category.Name))
                                {
                                    string supportedCategories = string.Join(", ", _revitDataModel.GetEnabledCategoryNames());
                                    return_message += ($"\nThe selected element {elementId.Value} is not of a supported category. Supported categories are: {supportedCategories}.", Utils.WPF.Stores.MessageTypes.Error);
                                }
                                else
                                {
                                    try
                                    {
                                        validElements.Add(selectedElement as FamilyInstance);
                                    }
                                    catch (Exception ex)
                                    {
                                        return_message += ($"\nAn exception occurred while converting the selected element {elementId.Value} to a family instance: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                                    }
                                }
                            }

                            //check if any elements are valid
                            if (validElements.Count == 0)
                            {
                                return (return_message, Utils.WPF.Stores.MessageTypes.Error);
                            }
                            else
                            {
                                wipeCounter = validElements.Count;
                            }

                            // update parameter data in the data model
                            VerifyParametersInModel actionVerify = new(_revitDataModel);
                            (string messageActionVerify, Utils.WPF.Stores.MessageTypes messageActionTypeVerify) = actionVerify.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionVerify.GetLogMessagesAndLogTypes());

                            //only proceed if all parameters are verified
                            if (messageActionTypeVerify == MessageTypes.Error)
                            {
                                return (messageActionVerify, messageActionTypeVerify);
                            }

                            // Execute the action to wipe selected rooms in the Revit model
                            WipeSelectedRevitRoomsData actionWipe = new(
                                revitModel: _revitDataModel,
                                pushTargets: validElements,
                                roomsMainViewModel: _roomsMainViewModel
                            );
                            // execute the wipe action
                            (string messageActionWipe, Utils.WPF.Stores.MessageTypes messageActionTypeWipe) = actionWipe.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionWipe.GetLogMessagesAndLogTypes());

                            // update the room data model again (check whether a new room was wiped and needs removing from the data model)
                            UpdateRoomDataModelWithNewRooms actionUpdateTwo = new(_revitDataModel, _roomsMainViewModel);
                            (string messageActionUpdateTwo, Utils.WPF.Stores.MessageTypes messageActionTypeUpdateTwo) = actionUpdateTwo.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionUpdateTwo.GetLogMessagesAndLogTypes());

                            // refresh the rooms data model with the rooms from the revit model
                            RefreshRoomDataWithRevitData refreshRoomDataWithRevitData = new(
                                revitModel: _revitDataModel,
                                roomsMainViewModel: _roomsMainViewModel,
                                revitMockRooms: actionUpdateTwo.CurrentMockRoomsData //re-use mock room data to speed things up
                            );

                            //execute the refresh action
                            (string messageActionRefresh, Utils.WPF.Stores.MessageTypes messageActionTypeRefresh) = refreshRoomDataWithRevitData.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(refreshRoomDataWithRevitData.GetLogMessagesAndLogTypes());

                            // return the message to the caller
                            return (
                                $"{messageActionWipe}\n{messageActionUpdateTwo}\n{messageActionRefresh}",
                                Utilities.MessageActionTypesUtils.CombineMessageActionType(
                                    [messageActionTypeWipe, messageActionTypeUpdateTwo, messageActionTypeRefresh]
                                )
                            );
                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the external event handler update after wipe selected rooms event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
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
            if (e.PropertyName == nameof(ViewModels.RoomsMainViewModel.IsWaitingForRevitCommandToFinish))
            {
                _command.NotifyCanExecuteChanged();
            }
        }

        public WipeSelectedRevitRoomInstancesAsyncCommand(
            ViewModels.RoomsMainViewModel roomsMainViewModel,
            Models.RevitDataModel revitDataModel
            )
        {
            _revitDataModel = revitDataModel;
            _roomsMainViewModel = roomsMainViewModel;
            _command = new AsyncRelayCommand(Execute, CanExecute);
            _roomsMainViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}