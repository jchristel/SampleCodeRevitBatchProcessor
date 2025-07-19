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
using duHastNet.PushIt.Models;
using System.Collections.Generic;

namespace duHastNet.PushIt.RevitActions
{
    public class PushSingleRoomDataToRevit : RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {

        private readonly RoomDataModel _roomToPush;
        private readonly Element _pushTarget;
        private readonly ViewModels.RoomsMainViewModel _roomsMainViewModel;


        public ViewModels.RoomsMainViewModel RoomsSelectionViewModel => _roomsMainViewModel;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try
            {
                // get shared parameter data from the model
                // get shared parameter ids by GUID
                Dictionary<string, ElementId> sharedParameterIdsByGUIDs = duHastNet.RevitUtils.Parameters.SharedParaUtils.GetSharedParameterIdsByGUID(doc);

                //extract current model data from the element selected
                var modelDataPrevious = Utilities.Revit.RevitRoomObjectsConverter.ConvertSingleFamilyToRevitRoom(
                    familyInstance: _pushTarget as Autodesk.Revit.DB.FamilyInstance,
                    parametersRequired:RevitModel.GetAllParameters(),
                    sharedParameterIdsByGUIDs: sharedParameterIdsByGUIDs
                );

                bool updateFamily = Utilities.Revit.FamilyUpdate.UpdateSingleFamilyInstance(
                    doc: doc,
                    familyInstance: _pushTarget as Autodesk.Revit.DB.FamilyInstance,
                    roomData: _roomToPush,
                    pushOperationMode: _roomsMainViewModel.PushOperationMode,
                    AddMessage: AddMessage
                );

                if (!updateFamily)
                {
                    // log error
                    AddMessage($"Failed to update family instance(s): {_pushTarget.Id.Value}", Utils.WPF.Stores.MessageTypes.Error);
                }
                else
                {
                    // log success
                    AddMessage($"Updated family instance(s): {_pushTarget.Id.Value}", Utils.WPF.Stores.MessageTypes.Information);
                }

                // get updated model data from the element selected
                var modelDataUpdated = Utilities.Revit.RevitRoomObjectsConverter.ConvertSingleFamilyToRevitRoom(
                    familyInstance: _pushTarget as Autodesk.Revit.DB.FamilyInstance,
                    parametersRequired: RevitModel.GetAllParameters(),
                    sharedParameterIdsByGUIDs: sharedParameterIdsByGUIDs
                );

                //only remove previous data if there is a valid room
                if (modelDataPrevious != null)
                {

                    //check if the previous room was a pushed room ,split room or a new room
                    if (Utilities.PushModeUtils.IsSplitRoomMode(modelDataPrevious.Id.Value))
                    {
                        // remove the previous Revit room from the data model before adding it back in with new data
                        RevitModel.RemovePlacedRevitRoom(modelDataPrevious.RevitElementId);
                    }
                    else if (Utilities.PushModeUtils.IsNewRoomMode(modelDataPrevious.Id.Value))
                    {
                        // remove the previous Revit room from the data model before adding it back in with new data
                        RevitModel.RemovePlacedNewRevitRoom(
                            roomId: modelDataPrevious.Id.Value,
                            revitElementId: modelDataPrevious.RevitElementId
                        );
                    }
                    else
                    {
                        // remove the previous Revit room from the data model before adding it back in with new data
                        RevitModel.RemovePlacedRevitRoom(modelDataPrevious.RevitElementId);
                    }
                }

                //depending on the push operation mode, add the updated Revit room to the data model
                if (_roomsMainViewModel.PushOperationMode == duHastNet.PushIt.Utilities.PushMode.Push)
                {
                    // add the updated Revit room to the data model
                    RevitModel.AddPlacedRevitRoom(_roomToPush.Id.Value, modelDataUpdated);
                }
                else if (_roomsMainViewModel.PushOperationMode == duHastNet.PushIt.Utilities.PushMode.Split)
                {
                    // add the updated Revit room to the data model but mkae sure its added as a split room
                    var splitId = Utilities.PushModeUtils.GetSplitModeIdValue(_roomToPush.Id.Value);
                    RevitModel.AddPlacedRevitRoom(splitId, modelDataUpdated);
                }
                else if (_roomsMainViewModel.PushOperationMode == duHastNet.PushIt.Utilities.PushMode.New)
                {
                    // update the existing Revit room in the data model
                    RevitModel.AddPlacedNewRevitRoom(
                        roomId: modelDataUpdated.Id.Value,
                        revitRoom: modelDataUpdated
                    );
                }

            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error updating single room in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue($"Updated room {_roomToPush.Id.Value} in the model.");
        }

        public PushSingleRoomDataToRevit(RevitDataModel revitModel, Models.RoomDataModel roomToPush, Element pushTarget, ViewModels.RoomsMainViewModel roomsMainViewModel)
        {
            RevitModel = revitModel;
            _roomToPush = roomToPush;
            _pushTarget = pushTarget;
            _roomsMainViewModel = roomsMainViewModel;
        }
    }
}
