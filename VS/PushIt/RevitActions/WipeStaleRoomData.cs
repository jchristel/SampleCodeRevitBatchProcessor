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
    public class WipeStaleRoomData : RevitActionBase, IRevitAction
    {
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        private int _wipeCounter = 0;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try
            {
                WipeData(
                    doc,
                    RevitModel._roomsContainer.GetAllRooms(),
                    RevitModel.Settings.SupportedCategories
                 );
            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error wiping stale room(s) data in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // check if any error messages were added
            if (GetErrorMessages().Count > 0)
            {
                // return the message
                return (string.Join("\n", GetErrorMessages()), Utils.WPF.Stores.MessageTypes.Error);
            }
            else
            {
                // return the message
                return ($"Wiped {_wipeCounter} stale room(s) data in Revit", Utils.WPF.Stores.MessageTypes.Information);
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
                return true;
            }
        }

        public void WipeData(Document doc, List<Models.RoomDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            if (roomsDataModel.Count == 0)
            {
                // no sample room available...means no parameter mapping available
                AddMessage("Data model contains no rooms to push to Revit.", duHast.Utils.WPF.Stores.MessageTypes.Error);
                return;
            }

            // get supported categories
            List<Category> categories = duHast.RevitUtils.Categories.CategoryUtils.GetMainCategoriesByName(doc, supportedCategoryName);
            if (categories.Count == 0)
            {
                // no supported categories found
                AddMessage("Data model contains no supported Revit categories.", duHast.Utils.WPF.Stores.MessageTypes.Error);
                return;
            }

            // convert revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = duHast.RevitUtils.Categories.CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            //get families of supported built in categories
            List<FamilyInstance> familyInstances = duHast.RevitUtils.Families.FamilyUtils.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            //check if there are any family instances
            if (familyInstances.Count == 0)
            {
                // no family instances available...nothing to push
                _roomsSelectionViewModel.AddMessage("No family instances found in the model", duHast.Utils.WPF.Stores.MessageTypes.Information);
                return;
            }

            // convert family instances to revit rooms
            List<duHast.PushIt.Models.RoomsRevit> revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(
                familyInstances, roomsDataModel[0], AddMessage);

            //build a list of family instances that contain stale data ( stale data is a family instance where the room id is not in the rooms data model)
            List<FamilyInstance> staleFamilyInstances = new List<FamilyInstance>();
            foreach (var revitRoomInstance in revitRooms)
            {
                if (!roomsDataModel.Exists(x => x.Id.Value == revitRoomInstance.Id.Value))
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
        public WipeStaleRoomData(Models.RevitDataModel revitModel, ViewModels.RoomsSelectionViewModel roomsSelectionViewModel)
        {
            RevitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
        }
    }
}
