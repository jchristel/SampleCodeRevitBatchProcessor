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
using duHastNet.PushIt.ViewModels;
using System.Collections.Generic;

namespace duHastNet.PushIt.RevitActions
{
    /// <summary>
    /// Scans all supported Revit family instances for split-suffixed IDs
    /// ({parentId}::SPLIT::{counter}) and synchronises the _splitRooms list
    /// in the data model accordingly.
    ///
    /// Mirrors UpdateRoomDataModelWithNewRooms. Called during every refresh
    /// operation so that split rooms created in previous sessions are recovered
    /// on load and any wipe/re-push changes are reflected immediately.
    /// </summary>
    public class UpdateRoomDataModelWithSplitRooms : RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {
        private readonly ViewModels.RoomsMainViewModel _roomsMainViewModel;
        public ViewModels.RoomsMainViewModel RoomsMainViewModel => _roomsMainViewModel;

        // current set of push it mock rooms — can be re-used by the caller to avoid a second scan
        private List<RoomRevit> _roomsData;
        public List<RoomRevit> CurrentMockRoomsData { get { return _roomsData; } }

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try
            {
                // reset the split rooms in the data model
                RevitModel.ClearSplitRooms();

                // get all supported families from the Revit model
                _roomsData = Utilities.Revit.FamilyGet.GetAllSupportedFamilies(
                    doc: doc,
                    revitDataModel: RevitModel,
                    supportedCategoryNames: RevitModel.GetEnabledCategoryNames(),
                    AddMessage: RoomsMainViewModel.AddMessage);

                if (_roomsData == null || _roomsData.Count == 0)
                {
                    return GetReturnValue("No split rooms found in the model.");
                }

                // group split rooms by their full split ID
                Dictionary<string, List<RoomRevit>> splitRoomsInModel = [];

                foreach (var room in _roomsData)
                {
                    if (duHastNet.PushIt.Utilities.PushModeUtils.IsSplitRoomMode(room.Id.Value))
                    {
                        if (!splitRoomsInModel.TryGetValue(room.Id.Value, out List<RoomRevit> value))
                        {
                            value = [];
                            splitRoomsInModel.Add(room.Id.Value, value);
                        }
                        value.Add(room);
                    }
                }

                int countSplitRooms = 0;

                foreach (KeyValuePair<string, List<RoomRevit>> kvp in splitRoomsInModel)
                {
                    // build a standalone RoomDataModel from the first instance (one per split ID)
                    Models.RoomDataModel splitRoom = Utilities.ConvertRevitRoomObjectToDataModelRoomObject.ConvertRevitRoomToDataModelRoom(
                        revitRoom: kvp.Value[0]
                    );

                    RevitModel.AddSplitRoom(splitRoom);
                    countSplitRooms++;
                }

                return ($"{countSplitRooms} split rooms added to the data model from the Revit model.", Utils.WPF.Stores.MessageTypes.Information);
            }
            catch (System.Exception ex)
            {
                AddMessage($"Error adding split rooms from Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            return GetReturnValue("Created split rooms from Revit.");
        }

        public UpdateRoomDataModelWithSplitRooms(RevitDataModel revitModel, ViewModels.RoomsMainViewModel roomsMainViewModel)
        {
            RevitModel = revitModel;
            _roomsMainViewModel = roomsMainViewModel;
        }
    }
}
