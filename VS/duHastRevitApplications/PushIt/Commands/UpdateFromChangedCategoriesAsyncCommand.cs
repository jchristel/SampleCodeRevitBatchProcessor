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


using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.Utilities;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows.Input;

namespace duHastNet.PushIt.Commands
{
    public class UpdateFromChangedCategoriesAsyncCommand
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
                        //Run Revit API code here

                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            // before invoking the action, check if the category selection has changed compared to
                            // the settings stored in the data model. If so, update the data model and invoke the action.
                            // Otherwise pop a message to the user that no changes were made.

                            //this list is automatically updated by the view model managing the categories
                            var allAvailableCategories = _revitDataModel.GetAllCategories();

                            // get the current category selection from the data model
                            List<string> enabledCategoryNamesFromDataModel = [];

                            foreach (var category in allAvailableCategories)
                            {
                                if (category.Enabled)
                                {
                                    enabledCategoryNamesFromDataModel.Add(category.Name);
                                }
                            }

                            //check if any categories are selected
                            if (enabledCategoryNamesFromDataModel.Count == 0)
                            {
                                return ("Please select at least one category to proceed.", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            // compare the category selection from the view model with the one stored in the data model
                            bool needUpdate = false;

                            // if the count of the categories is different, we need to update
                            if (enabledCategoryNamesFromDataModel.Count != _revitDataModel.GetAllCategories().Count)
                            {
                                needUpdate = true;
                            }
                            else
                            {
                                // if the count is the same, check if the category names are the same
                                foreach (string categoryName in enabledCategoryNamesFromDataModel)
                                {
                                    // if a category name is not in the list of supported categories, we need to update
                                    if (!_revitDataModel.GetEnabledCategoryNames().Contains(categoryName))
                                    {
                                        needUpdate = true;
                                        break;
                                    }
                                }
                            }

                            // if no update is needed, pop message to user and return
                            if (!needUpdate)
                            {
                                return ("No changes in category selection detected.", Utils.WPF.Stores.MessageTypes.Information);
                            }

                            // update the categories in the settings
                            // the actual categories objects should be updated by the category selection view model
                            _revitDataModel.Settings.EnabledCategoryNames = enabledCategoryNamesFromDataModel;

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

                            //add new rooms to the data model first
                            UpdateRoomDataModelWithNewRooms actionUpdate = new(
                                _revitDataModel,
                                _roomsMainViewModel
                            );

                            (string messageActionUpdate, Utils.WPF.Stores.MessageTypes messageActionTypeUpdate) = actionUpdate.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionUpdate.GetLogMessagesAndLogTypes());

                            // Execute the action to refresh the room data with the Revit data
                            RefreshRoomDataWithRevitData action = new(
                                revitModel: _revitDataModel,
                                roomsMainViewModel: _roomsMainViewModel,
                                revitMockRooms: actionUpdate.CurrentMockRoomsData //re-use mock room data to speed things up
                            );

                            (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) = action.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            // return the message to the caller
                            return (
                                $"{messageActionUpdate}\n{messageAction}",
                                Utilities.MessageActionTypesUtils.CombineMessageActionType([messageActionTypeUpdate, messageActionType])
                            );

                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the external event handler update after changed categories event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
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

        public UpdateFromChangedCategoriesAsyncCommand(
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