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
using PushIt.Models;
using RevitUtils;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;

namespace PushIt.RevitActions
{
    public class WipeStaleRoomData : IRevitAction
    {
        private readonly RevitDataModel _revitModel;
        public Models.RevitDataModel RevitModel => _revitModel;

        public void Execute(Document doc)
        {
            WipeData(
                doc,
                _revitModel._roomsContainer.GetAllRooms(),
                _revitModel.Settings.SupportedCategories
             );
        }


        public bool wipeIt(Document doc, List<FamilyInstance> familyInstancesToWipe, RoomDataModel sampleRoom)
        {
            bool wipeSuccess = Utilities.Revit.FamilyUpdate.wipeMultipleFamilyInstances(doc, familyInstancesToWipe, sampleRoom);
            if (!wipeSuccess)
            {
                // attempt to wipe one by one
                foreach (var familyInstance in familyInstancesToWipe)
                {
                    // at least one will fail...but the rest will succeed
                    bool wipeSuccessSingle = Utilities.Revit.FamilyUpdate.wipeMultipleFamilyInstances(doc, new List<FamilyInstance> { familyInstance }, sampleRoom);
                    if (!wipeSuccessSingle)
                    {
                        // log error
                    }

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
                // todo log error
                return;
            }

            // get supported categories
            List<Category> categories = RevitUtils.CategoryUtils.GetMainCategoriesByName(doc, supportedCategoryName);
            if (categories.Count == 0)
            {
                // no supported categories found
                // todo log error
                return;
            }

            // convert revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            //get families of supported built in categories
            List<FamilyInstance> familyInstances = RevitUtils.Families.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            // convert family instances to revit rooms
            List<PushIt.Models.RoomsRevit> revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(familyInstances, roomsDataModel[0]);

            //build a list of family instances that contain stale data ( stale data is a family instance where the room id is not in the rooms data model)
            List<FamilyInstance> staleFamilyInstances = new List<FamilyInstance>();
            foreach (var revitRoomInstance in revitRooms)
            {
                if (!roomsDataModel.Exists(x => x.Id.Value == revitRoomInstance.Id))
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
                
                //reached bucket limit?
                if (familyInstancesToWipe.Count == 20)
                {
                    // update the family instances
                    bool wipeSuccess = wipeIt(doc, familyInstancesToWipe, roomsDataModel[0]);
                    overallWipeSuccess = overallWipeSuccess && wipeSuccess;
                    // clear the update family instances
                    familyInstancesToWipe.Clear();
                }
                
            }

            //wipe the remaining family instances
            if (familyInstancesToWipe.Count > 0)
            {
                bool wipeSuccess = wipeIt(doc, familyInstancesToWipe, roomsDataModel[0]);
                overallWipeSuccess = overallWipeSuccess && wipeSuccess;
            }

        }
        public WipeStaleRoomData(Models.RevitDataModel revitModel)
        {
            _revitModel = revitModel;
        }
    }
}
