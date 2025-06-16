using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.Utilities;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;

namespace duHastNet.PushIt.Commands
{
    public class WipeSelectedRevitRoomInstancesAsyncCommand : Utils.WPF.Commands.CommandBase
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

                        int wipeCounter = 0;
                        //Run Revit API code here
                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            //check what is selected in the UI
                            UIDocument uidoc = app.ActiveUIDocument;

                            // get the selected element ids
                            List<ElementId> selectedElementIds = uidoc.Selection.GetElementIds().ToList();
                            // check quantity of selected elements
                            if (selectedElementIds.Count == 0)
                            {
                                return ("No room selected in the Revit model to wipe.", Utils.WPF.Stores.MessageTypes.Error);
                            }

                            // filter selected elements by supported categories
                            List<FamilyInstance> validElements = new List<FamilyInstance>();
                            string return_message = "";
                            foreach (ElementId elementId in selectedElementIds)
                            {
                                Element selectedElement = doc.GetElement(elementId);
                                // check if the selected element is of a supported category (or has category to start with)
                                if (selectedElement.Category == null || !_revitDataModel.Settings.EnabledCategoryNames.Contains(selectedElement.Category.Name))
                                {
                                    string supportedCategories = string.Join(", ", _revitDataModel.Settings.EnabledCategoryNames);
                                    return_message = return_message + ($"\nThe selected element {elementId.IntegerValue} is not of a supported category. Supported categories are: {supportedCategories}.", Utils.WPF.Stores.MessageTypes.Error);
                                }
                                else
                                {
                                    // convert element to family instance
                                    try
                                    {
                                        validElements.Add(selectedElement as FamilyInstance);
                                    }
                                    catch (Exception ex)
                                    {
                                        return_message = return_message + ($"\nAn exception occurred while converting the selected element {elementId.IntegerValue} to a family instance: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
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

                            //add new rooms to the data model first
                            //UpdateRoomDataModelWithNewRooms actionUpdate = new PushIt.RevitActions.UpdateRoomDataModelWithNewRooms(_revitDataModel, _roomsSelectionViewModel);
                            //(string messageActionUpdate, Utils.WPF.Stores.MessageTypes messageActionTypeUpdate) = actionUpdate.Execute(doc);

                            //write messages to log...
                            //_revitDataModel.LogMessages(actionUpdate.GetLogMessagesAndLogTypes());

                            // Execute the action to wipe selected rooms in the Revit model
                            WipeSelectedRevitRoomsData actionWipe = new WipeSelectedRevitRoomsData(
                                revitModel: _revitDataModel,
                                pushTargets: validElements,
                                roomsSelectionViewModel: _roomsSelectionViewModel
                            );
                            // execute the wipe action
                            (string messageActionWipe, Utils.WPF.Stores.MessageTypes messageActionTypeWipe) = actionWipe.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionWipe.GetLogMessagesAndLogTypes());

                            //update the room data model again ( this time to check whether a new room was wiped and therefore needs to be removed from the data model)
                            //add new rooms to the data model first
                            UpdateRoomDataModelWithNewRooms actionUpdateTwo = new PushIt.RevitActions.UpdateRoomDataModelWithNewRooms(_revitDataModel, _roomsSelectionViewModel);
                            (string messageActionUpdateTwo, Utils.WPF.Stores.MessageTypes messageActionTypeUpdateTwo) = actionUpdateTwo.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionUpdateTwo.GetLogMessagesAndLogTypes());

                            // refresh the rooms data model with the rooms from the revit model
                            RefreshRoomDataWithRevitData refreshRoomDataWithRevitData = new RefreshRoomDataWithRevitData(
                                revitModel: _revitDataModel,
                                roomsSelectionViewModel: _roomsSelectionViewModel,
                                revitMockRooms: actionUpdateTwo.CurrentMockRoomsData //re-use mock room data to speed thhings up
                            );


                            //execute the refresh action
                            (string messageActionRefresh, Utils.WPF.Stores.MessageTypes messageActionTypeRefresh) = refreshRoomDataWithRevitData.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(refreshRoomDataWithRevitData.GetLogMessagesAndLogTypes());

                            // return the message to the caller
                            return (
                                $"{messageActionWipe}\n{messageActionUpdateTwo}\n{messageActionRefresh}",
                                Utilities.MessageActionTypesUtils.CombineMessageActionType(
                                    new List<MessageTypes> { messageActionTypeWipe, messageActionTypeUpdateTwo, messageActionTypeRefresh }
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
                //button is not available
                return false;
            }
            else
            {
                return true;
            }
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.IsWaitingForRevitCommandToFinish))
            {
                OnCanExecutedChanged();
            }
        }

        public WipeSelectedRevitRoomInstancesAsyncCommand(
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
