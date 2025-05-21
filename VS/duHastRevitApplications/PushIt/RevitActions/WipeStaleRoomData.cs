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
    public class WipeStaleRoomData : RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        private int _wipeCounter = 0;

        //current set or push it mock rooms
        private List<RoomRevit> _roomsData;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try
            {
                WipeData(
                    doc,
                    RevitModel._roomsContainer.GetAllRoomsCombined(), //include SoA and new rooms
                    RevitModel.Settings.SupportedCategories
                 );
            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error wiping stale room(s) data in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue($"Wiped {_wipeCounter} stale room(s) data in Revit");
        }


        public void WipeData(Document doc, List<Models.RoomDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            if (roomsDataModel.Count == 0)
            {
                // no sample room available...means no parameter mapping available
                AddMessage("Data model contains no rooms to push to Revit.", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                return;
            }

            if (_roomsData == null)
            {
                // get the revit rooms
                _roomsData = Utilities.Revit.FamilyGet.GetAllSupportedFamilies(
                    doc: doc,
                    roomsDataModel: roomsDataModel,
                    supportedCategoryNames: supportedCategoryName,
                    AddMessage: AddMessage
                );

                // check if any revit rooms were found
                if (_roomsData == null || _roomsData.Count == 0)
                {
                    // no revit rooms found
                    AddMessage("No Revit rooms found to wipe stale data.", Utils.WPF.Stores.MessageTypes.Error);
                    return;
                }
            }


            //build a list of family instances that contain stale data ( stale data is a family instance where the room id is not in the rooms data model)
            List<FamilyInstance> staleFamilyInstances = new List<FamilyInstance>();
            foreach (var revitRoomInstance in _roomsData)
            {
                string revitRoomInstanceId = revitRoomInstance.Id.Value;

                // check if the room is a split room
                if (Utilities.PushModeUtils.IsSplitRoomMode(revitRoomInstance.Id.Value))
                {
                    // get the id without the split indicator
                    revitRoomInstanceId = Utilities.PushModeUtils.GetIdWithoutSplitModeIndicator(revitRoomInstance.Id.Value);
                }

                // check if the room id is in the data model
                if (!roomsDataModel.Exists(x => x.Id.Value == revitRoomInstanceId))
                {
                    staleFamilyInstances.Add(doc.GetElement(new ElementId(revitRoomInstance.RevitElementId)) as FamilyInstance);
                }
            }

            // keep track of the overall success of the wipe operation
            bool overallWipeSuccess = true;

            //attempt to wipe the stale data in bundles of 20 family instances to speed up the process
            List<FamilyInstance> familyInstancesToWipe = new List<FamilyInstance>();
            foreach (var staleFamilyInstance in staleFamilyInstances)
            {
                //fill the task bucket
                familyInstancesToWipe.Add(staleFamilyInstance);
                _wipeCounter++;

                //reached bucket limit?
                if (familyInstancesToWipe.Count == 20)
                {
                    // update the family instances
                    bool wipeSuccess = WipeIt(doc, familyInstancesToWipe, roomsDataModel[0]);
                    AddMessage($"Wiping {familyInstancesToWipe.Count} family instances. {wipeSuccess}", Utils.WPF.Stores.MessageTypes.Log);
                    overallWipeSuccess = overallWipeSuccess && wipeSuccess;
                    // clear the update family instances
                    familyInstancesToWipe.Clear();
                }
            }

            //wipe the remaining family instances
            if (familyInstancesToWipe.Count > 0)
            {
                bool wipeSuccess = WipeIt(doc, familyInstancesToWipe, roomsDataModel[0]);
                AddMessage($"Wiping {familyInstancesToWipe.Count} family instances. {wipeSuccess}", Utils.WPF.Stores.MessageTypes.Log);
                overallWipeSuccess = overallWipeSuccess && wipeSuccess;
            }
        }

        public bool WipeIt(Document doc, List<FamilyInstance> familyInstancesToWipe, RoomDataModel sampleRoom)
        {
            bool wipeSuccess = Utilities.Revit.FamilyUpdate.WipeMultipleFamilyInstances(
                doc: doc,
                familyInstances: familyInstancesToWipe,
                sampleRoom: sampleRoom,
                AddMessage: AddMessage
            );

            if (!wipeSuccess)
            {
                AddMessage("Error wiping multiple family instances. Attempting wiping one at the time.", Utils.WPF.Stores.MessageTypes.Error);

                int wipeSuccessCounter = 0;
                // attempt to wipe one by one
                foreach (var familyInstance in familyInstancesToWipe)
                {
                    // at least one will fail...but the rest will succeed
                    bool wipeSuccessSingle = Utilities.Revit.FamilyUpdate.WipeMultipleFamilyInstances(
                        doc: doc,
                        familyInstances: new List<FamilyInstance> { familyInstance },
                        sampleRoom: sampleRoom,
                        AddMessage: AddMessage
                    );

                    if (!wipeSuccessSingle)
                    {
                        // log error
                        AddMessage($"Error wiping family instance: {familyInstance.Id.IntegerValue}", Utils.WPF.Stores.MessageTypes.Error);
                    }
                    else
                    {
                        wipeSuccessCounter++;
                    }

                }
                if (wipeSuccessCounter > 0)
                {
                    AddMessage($"Wiped {wipeSuccessCounter} family instances.", Utils.WPF.Stores.MessageTypes.Information);
                }
                return false;
            }
            else
            {
                AddMessage($"Wiped {familyInstancesToWipe.Count} family instances.", Utils.WPF.Stores.MessageTypes.Log);
                return true;
            }
        }

        public WipeStaleRoomData(
            Models.RevitDataModel revitModel,
            ViewModels.RoomsSelectionViewModel roomsSelectionViewModel,
            List<RoomRevit> roomsData = null)
        {
            RevitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _roomsData = roomsData;
        }
    }
}
