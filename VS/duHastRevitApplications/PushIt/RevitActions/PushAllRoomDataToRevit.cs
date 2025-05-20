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
    public class PushAllRoomDataToRevit : RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {

        /// <summary>
        /// build a dictionary of family instances that contain valid data ( valid data is a family instance where the room id has a match in the rooms data model)
        /// the dictionary key is the room id and the value is a tuple of the room data model and a list of revit family instances
        /// </summary>
        /// <param name="roomsDataModel">rooms in the data model</param>
        /// <param name="revitRooms">push it mock room intances</param>
        /// <param name="doc">Revit document</param>
        /// <returns></returns>
        public Dictionary<string, (RoomDataModel, List<FamilyInstance>)> GetFamilyInstancesWithIdInDataModel(List<Models.RoomDataModel> roomsDataModel, List<duHastNet.PushIt.Models.RoomRevit> revitRooms, Document doc)
        {
            // build a dictioanry of family instances that contain valid data ( valid data is a family instance where the room id has a match in the rooms data model)
            // the dictionary key is the room id and the value is a tuple of the room data model and a list of revit family instances
            Dictionary<string, (RoomDataModel, List<FamilyInstance>)> currentFamilyInstances = new Dictionary<string, (RoomDataModel, List<FamilyInstance>)>();

            foreach (var revitRoomInstance in revitRooms)
            {
                // check a pushed room ( id matches the room data model id)
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
                else if (Utilities.PushModeUtils.IsNewRoomMode(revitRoomInstance.Id.Value))
                {
                    // new rooms are not supported by this operation
                }
                else if (Utilities.PushModeUtils.IsSplitRoomMode(revitRoomInstance.Id.Value))
                {
                    //a split room, remove the split from the id value
                    string idValue = Utilities.PushModeUtils.GetIdWithoutSplitModeIndicator(revitRoomInstance.Id.Value);

                    if (roomsDataModel.Exists(x => x.Id.Value == idValue))
                    {
                        // get the data model of the original room
                        var originalRoom = roomsDataModel.Find(x => x.Id.Value == idValue);

                        //make a copy of the original room and update the id to include split
                        //??

                        // add the split room to the family instances
                        if (currentFamilyInstances.ContainsKey(idValue))
                        {
                            //add to existing key
                            currentFamilyInstances[idValue].Item2.Add(doc.GetElement(new ElementId(revitRoomInstance.RevitElementId)) as FamilyInstance);
                        }
                        else
                        {
                            currentFamilyInstances[idValue] = (
                                roomsDataModel.Find(x => x.Id.Value == idValue),
                                new List<FamilyInstance> { doc.GetElement(new ElementId(revitRoomInstance.RevitElementId)) as FamilyInstance }
                            );
                        }
                    }
                }
            }

            return currentFamilyInstances;
        }

        /// <summary>
        /// Update the family instances in the Revit model with data from the data model
        /// </summary>
        /// <param name="updateCounter"></param>
        /// <param name="taskBucketFamilyInstancesCounter"></param>
        /// <param name="updateFamilyInstances"></param>
        /// <param name="doc"></param>
        /// <returns></returns>
        public (bool, int) UpdateFamiliesInBucket(int updateCounter, int taskBucketFamilyInstancesCounter, Dictionary<string, (RoomDataModel, List<FamilyInstance>)> updateFamilyInstances, Document doc)
        {
            //update the overall counter when then task bucket is full
            updateCounter = updateCounter + taskBucketFamilyInstancesCounter;

            // update the family instances
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

            // return tjhe flag for update family and the update counter
            return (updateFamily, updateCounter);
        }

        /// <summary>
        /// Update the psuh it family instances in the Revit model with data from the data model
        /// </summary>
        /// <param name="currentFamilyInstances">A dictionary where the key is the room id and the value is a tuple of the room data model instance and a list of revit family instances belonging to it</param>
        /// <param name="doc">Revit document</param>
        /// <param name="bucketSize">The number of families to be updated in one transaction</param>
        /// <returns></returns>
        public (bool, int) UpdateRevitModel(Dictionary<string, (RoomDataModel, List<FamilyInstance>)> currentFamilyInstances, Document doc, int bucketSize)
        {
            // keep track of the overall success of the wipe operation
            bool overallUpdateSuccess = true;
            int updateCounter = 0;
            int taskBucketFamilyInstancesCounter = 0;

            //attempt to update room data in bundles of bucket size number of family instances to speed up the process
            Dictionary<string, (RoomDataModel, List<FamilyInstance>)> updateFamilyInstances = new Dictionary<string, (RoomDataModel, List<FamilyInstance>)>();

            // loop through the family instances and add them to the task bucket
            foreach (var currentFamilyInstance in currentFamilyInstances)
            {
                //fill the task bucket
                updateFamilyInstances.Add(currentFamilyInstance.Key, currentFamilyInstance.Value);

                //update the running count of number of family instances per room id
                taskBucketFamilyInstancesCounter = taskBucketFamilyInstancesCounter + currentFamilyInstance.Value.Item2.Count;

                // check if max number of family instances to update for the task bucket has been reached
                if (taskBucketFamilyInstancesCounter >= bucketSize)
                {
                    // flag for update family
                    bool updateFamily = true;

                    //update all families in the task bucket
                    (updateFamily, updateCounter) = UpdateFamiliesInBucket(updateCounter, taskBucketFamilyInstancesCounter, updateFamilyInstances, doc);

                    // update the overall success
                    overallUpdateSuccess = overallUpdateSuccess && updateFamily;

                    // clear the update family instances
                    updateFamilyInstances.Clear();

                    // reset the task bucket family instances counter
                    taskBucketFamilyInstancesCounter = 0;
                }
            }

            //update the remaining family instances if any ( if the last task bucket was not full )
            if (updateFamilyInstances.Count > 0)
            {
                // flag for update family
                bool updateFamily = true;

                //update all families in the task bucket
                (updateFamily, updateCounter) = UpdateFamiliesInBucket(updateCounter, taskBucketFamilyInstancesCounter, updateFamilyInstances, doc);

                // update the overall success
                overallUpdateSuccess = overallUpdateSuccess && updateFamily;

                // clear the update family instances
                updateFamilyInstances.Clear();
            }

            return (overallUpdateSuccess, updateCounter);
        }

        /// <summary>
        /// Execute the action
        /// </summary>
        /// <param name="doc">The current Revit document</param>
        /// <returns></returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            // get all rooms in the model ( these rooms have their equivalent revit rooms already attached )??
            List<Models.RoomDataModel> roomsDataModel = RevitModel.GetAllRooms();

            if (roomsDataModel.Count == 0)
            {
                // no rooms available...nothing to push
                // todo log error
                return ("Data model contains no rooms to push to Revit.", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }

            // get the revit rooms
            List<duHastNet.PushIt.Models.RoomRevit> revitRooms = Utilities.Revit.FamilyGet.GetAllSupportedFamilies(
                doc: doc,
                roomsDataModel: roomsDataModel,
                supportedCategoryName: RevitModel.Settings.SupportedCategories,
                AddMessage: AddMessage
            );

            // check if any rooms were found in the model
            if (revitRooms.Count == 0)
            {
                // no rooms available...nothing to push
                // todo log error
                return ("No rooms found in the model to push data to.", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }

            // build a dictionary of family instances that contain valid data ( valid data is a family instance where the room id has a match in the rooms data model)
            // the dictionary key is the room id and the value is a tuple of the room data model and a list of revit family instances
            Dictionary<string, (RoomDataModel, List<FamilyInstance>)> currentFamilyInstances = GetFamilyInstancesWithIdInDataModel(
                roomsDataModel,
                revitRooms,
                doc);

            // check if any family instances with id's were found in the model
            if (currentFamilyInstances.Count == 0)
            {
                // no family instances available...nothing to push
                // todo log error
                return ("No push it family instances with valid id's found in the model to push data to.", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }

            // keep track of the overall success of the wipe operation
            bool overallUpdateSuccess = true;
            int updateCounter = 0;

            //attempt to update room data in bundles of 20 family instances to speed up the process
            (overallUpdateSuccess, updateCounter) = UpdateRevitModel(
                currentFamilyInstances,
                doc,
                bucketSize: 20
            );

            // build the return message depending on error count
            return GetReturnValue($"Updated {updateCounter} rooms in the model with status: {overallUpdateSuccess}");
        }

        public PushAllRoomDataToRevit(RevitDataModel revitModel)
        {
            RevitModel = revitModel;
        }
    }
}
