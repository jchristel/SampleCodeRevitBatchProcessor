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


using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.Utilities;
using duHastNet.PushIt.ViewModels;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;

namespace duHastNet.PushIt.Commands
{
    /// <summary>
    /// Refreshes the UI from the Revit model asynchronously.
    /// - updates pushed and split rooms counts for SoA rooms in the model
    /// - updates new rooms from the model
    /// - this command can be slow if there are a large amount of mock room families in the model
    /// </summary>
    public class RefreshUIFromRevitModelAsyncCommand : Utils.WPF.Commands.CommandBase
    {
        private readonly ViewModels.RoomsMainViewModel _roomsMainViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;
        private readonly Models.RevitDataModel _revitDataModel;


        public override async void Execute(object parameter)
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

                            //need to add any new rooms to the data model first...
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
                                revitMockRooms: actionUpdate.CurrentMockRoomsData //re-use mock room data to speed thhings up
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
                            return ($"An exception occurred within the external event handler refresh UI from rooms in model event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                        }
                    });

                //pop message to user
                _roomsMainViewModel.AddMessage(message, messageType);

                //update the view model
                if (messageType == MessageTypes.Information)
                {
                    // raise event to notify the view model that the model has been updated
                    _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
                }
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

        /// <summary>
        /// this command is always available
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        public override bool CanExecute(object parameter)
        {
            // check if IsWaitingForRevitCommandToFinish is true
            if (_roomsMainViewModel.IsWaitingForRevitCommandToFinish)
            {
                return false;
            }
            return true;
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.RoomsMainViewModel.IsWaitingForRevitCommandToFinish))
            {
                OnCanExecutedChanged();
            }
        }

        public RefreshUIFromRevitModelAsyncCommand(
           ViewModels.RoomsMainViewModel roomsMainViewModel,
           Models.RevitDataModel revitDataModel
           )
        {
            _revitDataModel = revitDataModel;
            _roomsMainViewModel = roomsMainViewModel;

            _roomsMainViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
