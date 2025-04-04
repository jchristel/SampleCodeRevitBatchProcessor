
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
using duHast.PushIt.Models;
using System.Collections.Generic;

namespace duHast.PushIt.RevitActions
{
    public class WipeSelectedRevitRoomsData: RevitActionBase, IRevitAction
    {
        private readonly List<FamilyInstance> _pushTargets;
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;

        public ViewModels.RoomsSelectionViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;
        

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try
            {
                // wipe the data from the selected rooms
                WipeData(
                   doc,
                   RevitModel._roomsContainer.GetAllRooms(),
                   RevitModel.Settings.SupportedCategories
                );
            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error wiping seleted room(s) data in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue($"Wiped {_pushTargets.Count} selected room(s) data in Revit.");
        }

        public void WipeData(Document doc, List<Models.RoomDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            if (roomsDataModel.Count == 0)
            {
                // no sample room available...means no parameter mapping available
                AddMessage ("Data model contains no rooms to push to Revit.", duHast.Utils.WPF.Stores.MessageTypes.Error);
                return;
            }

            // convert family instances to revit rooms
            List<duHast.PushIt.Models.RoomsRevit> revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(
                _pushTargets, 
                roomsDataModel[0], 
                AddMessage
            );

            List<FamilyInstance> staleFamilyInstances = new List<FamilyInstance>();
            
            foreach (var revitRoomInstance in revitRooms)
            {
                staleFamilyInstances.Add(doc.GetElement(new ElementId(revitRoomInstance.RevitElementId)) as FamilyInstance);
            }

            AddMessage($"Wiping {staleFamilyInstances.Count} family instances.", Utils.WPF.Stores.MessageTypes.Log);

            bool wipeSuccess = WipeIt(doc, staleFamilyInstances, roomsDataModel[0]);
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
                        AddMessage:AddMessage
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
                if (wipeSuccessCounter> 0)
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

        
        public WipeSelectedRevitRoomsData(RevitDataModel revitModel, List<FamilyInstance> pushTargets, ViewModels.RoomsSelectionViewModel roomsSelectionViewModel)
        {
            RevitModel = revitModel;
            _pushTargets = pushTargets;
            _roomsSelectionViewModel = roomsSelectionViewModel;
        }
    }
}
