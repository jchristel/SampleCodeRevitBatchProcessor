using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHast.PushIt.Models;
using duHast.PushIt.RevitActions;
using duHast.PushIt.Utilities;
using duHast.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace duHast.PushIt.Commands
{
    public class PushSingleRoomInRevitAsyncCommand: Utils.WPF.Commands.CommandBase
    {
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly Utils.WPF.Stores.MessageStore _messageStore;

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

                            action.Execute(doc);

                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the external event handler update after push single room event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                        }
                        return ("all good", MessageTypes.Information);
                    });

                //activate the ui
                _roomsSelectionViewModel.IsWaitingForRevitCommandToFinish = false;

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
            Models.RevitDataModel revitDataModel,
            Utils.WPF.Stores.MessageStore messageStore
            )
        {
            _revitDataModel = revitDataModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _messageStore = messageStore;
            //_action = action;
            _roomsSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
