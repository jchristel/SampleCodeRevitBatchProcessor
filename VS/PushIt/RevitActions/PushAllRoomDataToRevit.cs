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

using duHast.PushIt.Models;
using System.Collections.Generic;
using Autodesk.Revit.DB;

namespace duHast.PushIt.RevitActions
{
    public class PushAllRoomDataToRevit: RevitActionBase, IRevitAction
    {
        /// <summary>
        /// Execute the action
        /// </summary>
        /// <param name="doc"></param>
        /// <returns></returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            List<Models.RoomDataModel> roomsDataModel = RevitModel.GetAllRooms();

            if (roomsDataModel.Count == 0)
            {
                // no rooms available...nothing to push
                // todo log error
                return ("Data model contains no rooms to push to Revit.", duHast.Utils.WPF.Stores.MessageTypes.Error);
            }

            // get shared parameter data from the model
            // get shared parameter ids by GUID
            Dictionary<string, ElementId> sharedParameterIdsByGUIDs = duHast.RevitUtils.Parameters.SharedParaUtils.GetSharedParameterIdsByGUID(doc);

            // get supported categories
            List<Category> categories = duHast.RevitUtils.Categories.CategoryUtils.GetMainCategoriesByName(doc, RevitModel.Settings.SupportedCategories);
            if (categories.Count == 0)
            {
                return("No supported Revit categories selected in settings.", duHast.Utils.WPF.Stores.MessageTypes.Error);
            }

            // convert revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = duHast.RevitUtils.Categories.CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            //get families of supported built in categories
            List<FamilyInstance> familyInstances = duHast.RevitUtils.Families.FamilyUtils.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            //check if there are any family instances
            if (familyInstances.Count == 0)
            {
                // no family instances available...nothing to push
                return("No family instances of supported Revit categories found.", Utils.WPF.Stores.MessageTypes.Information);
            }

            // convert family instances to revit rooms
            List<duHast.PushIt.Models.RoomsRevit> revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(
                familyInstances, 
                roomsDataModel[0], 
                AddMessage
             );

            // build a dictioanry of family instances that contain valid data ( valid data is a family instance where the room id has a match in the rooms data model)
            // the dictionary key is the room id and the value is a tuple of the room data model and a list of revit family instances
            Dictionary<string,(RoomDataModel,List < FamilyInstance>)> currentFamilyInstances = new Dictionary<string, (RoomDataModel, List<FamilyInstance>)>();
            foreach (var revitRoomInstance in revitRooms)
            {
                if (roomsDataModel.Exists(x => x.Id.Value == revitRoomInstance.Id.Value))
                {
                    if (currentFamilyInstances.ContainsKey(revitRoomInstance.Id.Value))
                    {
                        //add to existing key
                        currentFamilyInstances[revitRoomInstance.Id.Value].Item2.Add(doc.GetElement(new ElementId(revitRoomInstance.RevitElementId)) as FamilyInstance);
                    }
                    else
                    {
                        currentFamilyInstances[revitRoomInstance.Id.Value] = (
                            roomsDataModel.Find(x => x.Id.Value == revitRoomInstance.Id.Value), 
                            new List<FamilyInstance> { doc.GetElement(new ElementId(revitRoomInstance.RevitElementId)) as FamilyInstance }
                        );
                    }
                }
            }

            // keep track of the overall success of the wipe operation
            bool overallUpdateSuccess = true;
            int updateCounter = 0;
            int taskBucketFamilyInstancesCounter = 0;

            //attempt to update room data in bundles of 20 family instances to speed up the process
            Dictionary<string, (RoomDataModel, List<FamilyInstance>)> updateFamilyInstances = new Dictionary<string, (RoomDataModel, List<FamilyInstance>)>();
            foreach (var currentFamilyInstance in currentFamilyInstances)
            {
                //fill the task bucket
                updateFamilyInstances.Add(currentFamilyInstance.Key, currentFamilyInstance.Value);

                //update the running count of number of family instances per room id
                taskBucketFamilyInstancesCounter = taskBucketFamilyInstancesCounter + currentFamilyInstance.Value.Item2.Count;

                //update the overall counter
                updateCounter = updateCounter + taskBucketFamilyInstancesCounter;

                // check if max number of family instances to update for the task bucket has been reached
                if (taskBucketFamilyInstancesCounter >= 20)
                {
                    // update the family instances
                    bool updateFamily = Utilities.Revit.FamilyUpdate.UpdateMultipleFamilyInstances(
                        doc: doc,
                        familyData: updateFamilyInstances,
                        AddMessage: AddMessage
                    );

                    if (!updateFamily) {
                        // get all keys in the update family instances
                        string keys = string.Join(", ", updateFamilyInstances.Keys);
                        // log the error
                        AddMessage($"Failed to update room(s): {keys}", Utils.WPF.Stores.MessageTypes.Error); 
                    }

                    // update the overall success
                    overallUpdateSuccess = overallUpdateSuccess && updateFamily;
                    
                    // clear the update family instances
                    updateFamilyInstances.Clear();

                    // reset the task bucket family instances counter
                    taskBucketFamilyInstancesCounter = 0;
                }
            }

            //update the remaining family instances if any
            if (updateFamilyInstances.Count>0)
            {
                bool updateFamily = Utilities.Revit.FamilyUpdate.UpdateMultipleFamilyInstances(
                    doc: doc,
                    familyData: updateFamilyInstances,
                    AddMessage: AddMessage
                );

                // log the error if the update failed
                if (!updateFamily)
                {
                    // get all keys in the update family instances
                    string keys = string.Join(", ", updateFamilyInstances.Keys);
                    // log the error
                    AddMessage($"Failed to update room(s): {keys}", Utils.WPF.Stores.MessageTypes.Error);
                }

                // update the overall success
                overallUpdateSuccess = overallUpdateSuccess && updateFamily;
                // clear the update family instances
                updateFamilyInstances.Clear();
            }

            // build the return message depending on error count
            return GetReturnValue($"Updated {updateCounter} rooms in the model with status: {overallUpdateSuccess}");
        }

        public PushAllRoomDataToRevit(RevitDataModel revitModel)
        {
            RevitModel = revitModel;
        }
    }
}
