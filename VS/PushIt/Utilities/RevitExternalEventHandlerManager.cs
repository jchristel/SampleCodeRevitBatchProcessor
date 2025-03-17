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


using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Metadata;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using duHast.PushIt.RevitActions;
using System.CodeDom.Compiler;
using duHast.PushIt.ViewModels;
using System.Runtime.InteropServices;

namespace duHast.PushIt.Utilities
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


        Revit.CustomExternalEvent _updateAllRoomsInRevitEventHandler;
        ExternalEvent _updateAllRoomsInRevitEvent;

        Revit.CustomExternalEvent _updateAfterSupportedCategoryChangeEventHandler;
        ExternalEvent _updateAfterSupportedCategoryChangeEvent;

        Revit.CustomExternalEvent _wipeStaleRoomDataEventHandler;
        ExternalEvent _wipeStaleRoomDataEvent;

        Revit.CustomExternalEvent _highlightSelectedRoomEventHandler;
        ExternalEvent _highlightSelectedRoomEvent;

        Revit.CustomExternalEvent _refreshUIDataEventHandler;
        ExternalEvent _refreshUIDataEvent;

        Revit.CustomExternalEvent _pushSingleRoomEventHandler;
        ExternalEvent _pushSingleRoomEvent;

        Revit.CustomExternalEvent _reloadDataEventHandler;
        ExternalEvent _reloadDataEvent;


        public RevitExternalEventHandlerManager()
        {
            // Create an instance of the CustomExternalEvent class to update all rooms in the Revit model
            _updateAllRoomsInRevitEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => UpdateAllRoomsInRevitEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _updateAllRoomsInRevitEvent = ExternalEvent.Create(_updateAllRoomsInRevitEventHandler);

            // Create an instance of the CustomExternalEvent class to update the model after a supported category change
            _updateAfterSupportedCategoryChangeEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => UpdateAfterSupportedCategoryChangeEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _updateAfterSupportedCategoryChangeEvent = ExternalEvent.Create(_updateAfterSupportedCategoryChangeEventHandler);

            // Create an instance of the CustomExternalEvent class to wipe stale room data
            _wipeStaleRoomDataEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => WipeStaleRoomDataEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _wipeStaleRoomDataEvent = ExternalEvent.Create(_wipeStaleRoomDataEventHandler);

            // Create an instance of the CustomExternalEvent class to highlight the selected room
            _highlightSelectedRoomEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => HighlightSelectedRoomEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _highlightSelectedRoomEvent = ExternalEvent.Create(_highlightSelectedRoomEventHandler);

            // Create an instance of the CustomExternalEvent class to reload the data from the file path
            _reloadDataEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => ReloadDataEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _reloadDataEvent = ExternalEvent.Create(_reloadDataEventHandler);

            // Create an instance of the CustomExternalEvent class to push a single room to the Revit model
            _pushSingleRoomEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => PushItSingleEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _pushSingleRoomEvent = ExternalEvent.Create(_pushSingleRoomEventHandler);

            // Create an instance of the CustomExternalEvent class to refresh all the model room data in the UI
            _refreshUIDataEventHandler = new Utilities.Revit.CustomExternalEvent((UIApplication uiapp) => RefreshUIDataEventExecute(uiapp));
            // External Event for the dialog to use (to post requests)
            _refreshUIDataEvent = ExternalEvent.Create(_refreshUIDataEventHandler);
        }

        public void UpdateAllRoomsInRevitEventRaise()
        {
            // Raise the external event
            _updateAllRoomsInRevitEvent.Raise();
        }

        public void UpdateAllRoomsInRevitEventExecute(UIApplication uiapp)
        {
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;
            try
            {
                // Execute the action to update all rooms in the Revit model
                PushAllRoomDataToRevitIRevitAction action = new PushAllRoomDataToRevitIRevitAction(_revitDataModel, _roomsSelectionViewModel);
                action.Execute(doc);
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage($"An exception occurred within the external event handler update all rooms in Revit event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        public void UpdateAfterSupportedCategoryChangeEventRaise()
        {
            // Raise the external event
            _updateAfterSupportedCategoryChangeEvent.Raise();
        }

        public void UpdateAfterSupportedCategoryChangeEventExecute(UIApplication uiapp)
        {

            // this is the same code as in the RefreshUIDataEventExecute method...
            //but it is here to be able to raise the event from the view model
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;

            try
            {
                // Execute the action to refresh the room data with the Revit data
                RefreshRoomDataWithRevitData action = new RefreshRoomDataWithRevitData(_revitDataModel, _roomsSelectionViewModel);
                action.Execute(doc);

                // raise event to notify the view model that the model has been updated
                _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);

            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage( 
                    $"An exception occurred within the external event handler update after supported category change event: { ex.Message}", 
                    Utils.WPF.Stores.MessageTypes.Error
                );
            }
        }


        public void WipeStaleRoomDataEventRaise()
        {
            // Raise the external event
            _wipeStaleRoomDataEvent.Raise();
        }

        public void WipeStaleRoomDataEventExecute(UIApplication uiapp)
        {
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;
            try
            {
                // Execute the action to wipe stale room data from the Revit model
                WipeStaleRoomData action = new WipeStaleRoomData(
                    revitModel: _revitDataModel,
                    roomsSelectionViewModel: _roomsSelectionViewModel
                );
                action.Execute(doc);
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage(
                    $"An exception occurred within the external event handler update after wipe stale room data event: {ex.Message}",
                    Utils.WPF.Stores.MessageTypes.Error
                );
            }
        }

        public void HighlightSelectedRoomEventRaise()
        {
            // Raise the external event
            _highlightSelectedRoomEvent.Raise();
        }

        public void HighlightSelectedRoomEventExecute(UIApplication uiapp)
        {
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;
            try
            {
                //check if there is a room to highlight
                if (_roomsSelectionViewModel.SelectedRoom == null)
                {
                    _roomsSelectionViewModel.AddMessage("No room selected in the user interface to highlight in Revit.", Utils.WPF.Stores.MessageTypes.Error);
                    return;
                }
                // Execute the action to highlight the selected room in the Revit model
                HighlightRoomsInRevit action = new HighlightRoomsInRevit(
                    revitModel: _revitDataModel,
                    roomToPush: _roomsSelectionViewModel.SelectedRoom,
                    uiDoc: uiapp.ActiveUIDocument
                );
                action.Execute(doc);
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage(
                    $"An exception occurred within the external event handler update after highlight selected room event: {ex.Message}",
                    Utils.WPF.Stores.MessageTypes.Error
                );
            }
        }

        public void ReloadDataEventRaise()
        {
            // Raise the external event
            _reloadDataEvent.Raise();
        }

        public void ReloadDataEventExecute(UIApplication uiapp)
        {
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;
            try
            {
                //clear out all rooms from the data model
                _revitDataModel.ClearRooms();

                // reset the column order in the view model in case it was changed
                _roomsSelectionViewModel.ColumnOrder = new List<string>();

                // reload data from the file path
                _revitDataModel.LoadRoomsData();
                
                // Execute the action to refresh the room data with the Revit data
                RefreshRoomDataWithRevitData action = new RefreshRoomDataWithRevitData(_revitDataModel, _roomsSelectionViewModel);
                action.Execute(doc);
                
                // raise event to notify the view model that the model has been updated
                _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage($"An exception occurred within the external event handler update after reload data event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }
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
                    _roomsSelectionViewModel.AddMessage("No room selected in the user interface to push to Revit.", Utils.WPF.Stores.MessageTypes.Error);
                    return;
                }

                //check what is selected in the UI
                UIDocument uidoc = uiapp.ActiveUIDocument;

                // get the selected element ids
                List<ElementId> selectedElementIds = uidoc.Selection.GetElementIds().ToList();
                // check quantity of selected elements
                if (selectedElementIds.Count == 0)
                {
                    _roomsSelectionViewModel.AddMessage("No room selected in the Revit model to push to.", Utils.WPF.Stores.MessageTypes.Error);
                    return;
                }
                else if (selectedElementIds.Count > 1)
                {
                    _roomsSelectionViewModel.AddMessage("More than one room selected in the Revit model to push to.", Utils.WPF.Stores.MessageTypes.Error);
                    return;
                }

                //get the selected Element from Revit
                Element selectedElement = doc.GetElement(selectedElementIds.First());
                // check if the selected element is of a supported category (or has category to start with)
                if (selectedElement.Category ==null ||  !_revitDataModel.Settings.SupportedCategories.Contains (selectedElement.Category.Name))
                {
                    string supportedCategories = string.Join(", ", _revitDataModel.Settings.SupportedCategories);
                    _roomsSelectionViewModel.AddMessage($"The selected element is not of a supported category. Supported categories are: {supportedCategories}.", Utils.WPF.Stores.MessageTypes.Error);
                    return;
                }

                // Execute the action to push a single room to the Revit model
                PushSingleRoomDataToRevit action = new PushSingleRoomDataToRevit(
                    revitModel: _revitDataModel,
                    roomToPush: _roomsSelectionViewModel.SelectedRoom,
                    pushTarget: selectedElement,
                    roomsSelectionViewModel: _roomsSelectionViewModel
                );

                action.Execute(doc);
                // raise event to notify the view model that the model has been updated
                _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage($"An exception occurred within the external event handler update after push single room event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
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
                RefreshRoomDataWithRevitData action = new RefreshRoomDataWithRevitData(_revitDataModel, _roomsSelectionViewModel);
                action.Execute(doc);

                // raise event to notify the view model that the model has been updated
                _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
                
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage($"An exception occurred within the external event handler update after refresh UI data event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        /// <summary>
        /// Dispose the external events
        /// </summary>
        public void DisposeEvents()
        {
            _updateAllRoomsInRevitEvent.Dispose();
            _updateAllRoomsInRevitEvent = null;
            _updateAllRoomsInRevitEventHandler = null;

            _updateAfterSupportedCategoryChangeEvent.Dispose();
            _updateAfterSupportedCategoryChangeEvent = null;
            _updateAfterSupportedCategoryChangeEventHandler = null;

            _wipeStaleRoomDataEvent.Dispose();
            _wipeStaleRoomDataEvent = null;
            _wipeStaleRoomDataEventHandler = null;

            _highlightSelectedRoomEvent.Dispose();
            _highlightSelectedRoomEvent = null;
            _highlightSelectedRoomEventHandler = null;

            _refreshUIDataEvent.Dispose();
            _refreshUIDataEvent = null;
            _refreshUIDataEventHandler = null;

            _pushSingleRoomEvent.Dispose();
            _pushSingleRoomEvent = null;
            _pushSingleRoomEventHandler = null;
        }
    }
}
