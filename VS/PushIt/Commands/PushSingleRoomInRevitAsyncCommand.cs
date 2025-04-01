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
using duHast.PushIt.RevitActions;
using duHast.PushIt.Utilities;
using duHast.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;


namespace duHast.PushIt.Commands
{
    public class PushSingleRoomInRevitAsyncCommand: Utils.WPF.Commands.CommandBase
    {
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;
        private readonly Models.RevitDataModel _revitDataModel;

        public override async void Execute(object parameter)
        {
            //deactivate the ui
            _roomsSelectionViewModel.IsWaitingForRevitCommandToFinish = true;

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
                            if (_roomsSelectionViewModel.SelectedRoom == null)
                            {
                                return ("No room selected in the user interface to push to Revit.", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            //check what is selected in the UI
                            UIDocument uidoc = app.ActiveUIDocument;

                            // get the selected element ids
                            List<ElementId> selectedElementIds = uidoc.Selection.GetElementIds().ToList();
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
                            if (selectedElement.Category == null || !_revitDataModel.Settings.SupportedCategories.Contains(selectedElement.Category.Name))
                            {
                                string supportedCategories = string.Join(", ", _revitDataModel.Settings.SupportedCategories);
                                return ($"The selected element is not of a supported category. Supported categories are: {supportedCategories}.", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            // Execute the action to push a single room to the Revit model
                            PushSingleRoomDataToRevit action = new PushSingleRoomDataToRevit(
                                revitModel: _revitDataModel,
                                roomToPush: _roomsSelectionViewModel.SelectedRoom,
                                pushTarget: selectedElement,
                                roomsSelectionViewModel: _roomsSelectionViewModel
                            );

                            (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) = action.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            // return status message for UI
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
                _roomsSelectionViewModel.AddMessage(message, messageType);
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage(ex.Message, MessageTypes.Error);
            }
            finally
            {
                //activate the ui
                _roomsSelectionViewModel.IsWaitingForRevitCommandToFinish = false;
            }
        }

        public override bool CanExecute(object parameter)
        {
            // check if IsWaitingForRevitCommandToFinish is true
            if (_roomsSelectionViewModel.IsWaitingForRevitCommandToFinish)
            {
                return false;
            }

            // if safety off mode enabled this command is always available
            if (_roomsSelectionViewModel.SafetyOffMode) { return true; }

            // check if IsMatchingRevitRoomsEmpty is true and call the base CanExecute method
            return _roomsSelectionViewModel.IsMatchingRevitRoomsEmpty && base.CanExecute(parameter);
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.IsMatchingRevitRoomsEmpty) ||
                e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.IsWaitingForRevitCommandToFinish))
            {
                OnCanExecutedChanged();
            }
        }

        public PushSingleRoomInRevitAsyncCommand(
            ViewModels.RoomsSelectionViewModel roomsSelectionViewModel,
            Models.RevitDataModel revitDataModel
            )
        {
            _revitDataModel = revitDataModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _roomsSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
