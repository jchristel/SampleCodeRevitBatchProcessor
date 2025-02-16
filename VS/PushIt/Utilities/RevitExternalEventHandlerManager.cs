using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Metadata;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using PushIt.RevitActions;
using System.CodeDom.Compiler;
using PushIt.ViewModels;

namespace PushIt.Utilities
{
    public class RevitExternalEventHandlerManager
    {
        Models.RevitDataModel _revitDataModel;
        
        public Models.RevitDataModel RevitDataModel {
            get { return _revitDataModel; } 
            set { _revitDataModel = value; } 
        }

        ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        public RoomsSelectionViewModel RoomsSelectionViewModel { get => _roomsSelectionViewModel; set => _roomsSelectionViewModel = value; }

        



        Revit.CustomExternalEvent _refreshUIDataEventHandler;
        ExternalEvent _refreshUIDataEvent;

        Revit.CustomExternalEvent _pushSingleRoomEventHandler;
        ExternalEvent _pushSingleRoomEvent;


        public RevitExternalEventHandlerManager()
        {
            // Create an instance of the CustomExternalEvent class to push a single room to the Revit model
            _pushSingleRoomEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => PushItSingleEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _pushSingleRoomEvent = ExternalEvent.Create(_pushSingleRoomEventHandler);

            // Create an instance of the CustomExternalEvent class to refresh all the model room data in the UI
            _refreshUIDataEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => RefreshUIDataEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _refreshUIDataEvent = ExternalEvent.Create(_refreshUIDataEventHandler);
        }


        public void PushItSingleEventRaise()
        {
            // Raise the external event
            _pushSingleRoomEvent.Raise();
        }

        public void PushItSingleEventExecute(UIApplication uiapp)
        {
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;
            try
            {
                //check if there is a room to push
                if (_roomsSelectionViewModel.SelectedRoom == null)
                {
                    _roomsSelectionViewModel.AddMessage("No room selected in the user interface to push to Revit.", Stores.MessageTypes.Error);
                    TaskDialog.Show("Push Single Room", "No room selected to push to Revit.");
                    return;
                }

                //check what is selected in the UI
                UIDocument uidoc = uiapp.ActiveUIDocument;

                // get the selected element ids
                List<ElementId> selectedElementIds = uidoc.Selection.GetElementIds().ToList();
                // check quantity of selected elements
                if (selectedElementIds.Count == 0)
                {
                    _roomsSelectionViewModel.AddMessage("No room selected in the Revit model to push to.", Stores.MessageTypes.Error);
                    TaskDialog.Show("Push Single Room", "No room selected in the Revit model to push to.");
                    return;
                }
                else if (selectedElementIds.Count > 1)
                {
                    _roomsSelectionViewModel.AddMessage("More than one room selected in the Revit model to push to.", Stores.MessageTypes.Error);
                    TaskDialog.Show("Push Single Room", "More than one room selected in the Revit model to push to.");
                    return;
                }

                //get the selected Element from Revit
                Element selectedElement = doc.GetElement(selectedElementIds.First());
                if (!_revitDataModel.Settings.SupportedCategories.Contains (selectedElement.Category.Name))
                {
                    string supportedCategories = string.Join(", ", _revitDataModel.Settings.SupportedCategories);
                    _roomsSelectionViewModel.AddMessage($"The selected element is not of a supported category. Supported categories are: {supportedCategories}.", Stores.MessageTypes.Error);
                    TaskDialog.Show("Push Single Room", $"The selected element is not of a supported category. Supported categories are: {supportedCategories}.");
                    return;
                }

                // Execute the action to push a single room to the Revit model
                PushSingleRoomDataToRevit action = new PushSingleRoomDataToRevit(
                    revitModel: _revitDataModel,
                    roomToPush: _roomsSelectionViewModel.SelectedRoom,
                    pushTarget: selectedElement
                );

                action.Execute(doc);
                // raise event to notify the view model that the model has been updated
                _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
            }
            catch (Exception ex)
            {
                TaskDialog.Show("External Event Handler", $"An exception occurred within the external event handler: {ex.Message}");
            }
        }


        public void RefreshUIDataEventRaise()
        {
            // Raise the external event
            _refreshUIDataEvent.Raise();
        }

        public void RefreshUIDataEventExecute(UIApplication uiapp)
        {
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;

            try
            {
                // Execute the action to refresh the room data with the Revit data
                RefreshRoomDataWithRevitData action = new RefreshRoomDataWithRevitData(_revitDataModel);
                action.Execute(doc);

                // raise event to notify the view model that the model has been updated
                _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
                
            }
            catch (Exception ex)
            {
                TaskDialog.Show("External Event Handler", $"An exception occurred within the external event handler: {ex.Message}");
            }
        }

        /// <summary>
        /// Dispose the external events
        /// </summary>
        public void DisposeEvents()
        {
            _refreshUIDataEvent.Dispose();
            _refreshUIDataEvent = null;
            _refreshUIDataEventHandler = null;

            _pushSingleRoomEvent.Dispose();
            _pushSingleRoomEvent = null;
            _pushSingleRoomEventHandler = null;
        }
    }
}
