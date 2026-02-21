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
using System;
using System.Collections.Generic;
using System.Text;


namespace duHastNet.PushIt.Utilities.Revit
{
    public static class FamilyUpdate
    {
        /// <summary>
        /// Update the properties of a family instance with the room data
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="familyInstance"></param>
        /// <param name="roomData"></param>
        /// <param name="pushMode"></param>
        /// <param name="AddMessage"> a way to log messages</param>
        /// <param name="updateId">if true the ID of the element will be updated (default), otherwise it will be left as is. That can be usefull when updating existing rooms based on an ID ( the id value
        /// is already set and does need to be changed. Especially when that room is a split room.)</param>
        /// <returns></returns>
        public static bool UpdateProperties(
            Document doc,
            FamilyInstance familyInstance,
            Models.RoomDataModel roomData,
            duHastNet.PushIt.Utilities.PushMode pushMode,
            Action<string, Utils.WPF.Stores.MessageTypes> AddMessage,
            bool updateId = true)
        {

            // set up a variable to store the name of the property that is being updated in case of an exception
            string propertyName = "";

            try
            {
                // assume id update was successful ( can also be true if no id update was required )
                bool flagId = true;
                if (updateId)
                {
                    string room_id = roomData.Id.Value;
                    if (pushMode == PushMode.Split)
                    {

                        room_id = PushModeUtils.GetSplitModeIdValue(idValue: room_id);
                    }
                    else if (pushMode == PushMode.New)
                    {
                        room_id = PushModeUtils.GetNewModeIdValue();
                    }

                    // set the room id parameter
                    flagId = duHastNet.RevitUtils.Parameters.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.Id.ParameterGUID, room_id);
                    AddMessage($"Updated room id with value [{room_id}] for family instance [{familyInstance.Id}] with status: [{flagId}]", Utils.WPF.Stores.MessageTypes.Information);
                }
                else
                {
                    // add a log message
                    AddMessage($"Skipping ID update for room [{roomData.Id.Value}]", Utils.WPF.Stores.MessageTypes.Information);
                }

                //update other properties
                bool flagOtherProperties = true;

                // loop over the properties and update them
                foreach (var property in roomData.Properties)
                {
                    propertyName = property.Name;

                    // skip read only properties
                    if (property.IsReadOnly)
                    {
                        AddMessage($"Skipping read only property [{property.Name}] for family instance [{familyInstance.Id}]", Utils.WPF.Stores.MessageTypes.Warning);
                        continue;
                    }

                    // update the property depending on whether it has a GUID or not
                    if (property.ParameterGUID != "")
                    {
                        // get the current value of the property
                        string currentValue = duHastNet.RevitUtils.Parameters.SharedParaUtils.GetSharedParameterValueFromElementByGUID(
                            familyInstance,
                            property.ParameterGUID
                        );

                        if (currentValue != property.Value)
                        {
                            bool flag = duHastNet.RevitUtils.Parameters.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, property.ParameterGUID, property.Value);
                            AddMessage($"Updated shared parameter property [{property.Name}] with value [{property.Value}] from [{currentValue}] for family instance [{familyInstance.Id}] with status: {flag}", Utils.WPF.Stores.MessageTypes.Information);
                            flagOtherProperties = flagOtherProperties && flag;
                        }
                        else
                        {
                            AddMessage($"Property [{property.Name}] value does not need updating: current value [{currentValue}] equals SoA value [{property.Value}]", Utils.WPF.Stores.MessageTypes.Information);
                        }
                    }
                    else
                    {
                        // get the current value of the property
                        string currentValue = duHastNet.RevitUtils.Parameters.ParaUtils.GetParameterValueByName(familyInstance, property.Name);

                        if (currentValue != property.Value)
                        {
                            bool flag = duHastNet.RevitUtils.Parameters.ParaUtils.SetParameterValueByName(familyInstance, property.Name, property.Value);
                            AddMessage($"Updated non shared parameter property [{property.Name}] with value [{property.Value}] for family instance [{familyInstance.Id}] with status: {flag}", Utils.WPF.Stores.MessageTypes.Information);
                            flagOtherProperties = flagOtherProperties && flag;
                        }
                        else
                        {
                            AddMessage($"Property [{property.Name}] value does not need updating: current value [{currentValue}] equals SoA value [{property.Value}]", Utils.WPF.Stores.MessageTypes.Information);
                        }
                    }
                }
                return flagId && flagOtherProperties;
            }
            catch (Exception ex)
            {
                AddMessage($"Failed to update property [{propertyName}] on family instance [{familyInstance.Id}] with room data [{roomData.Id.Value}]: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                return false;
            }
        }


        /// <summary>
        /// Update a single family instance with the room data
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="familyInstance"></param>
        /// <param name="roomData"></param>
        /// <param name="pushOperationMode"></param>
        /// <returns> 
        /// True if the update was successful, false if not
        /// </returns>
        public static bool UpdateSingleFamilyInstance(Document doc, FamilyInstance familyInstance, Models.RoomDataModel roomData, duHastNet.PushIt.Utilities.PushMode pushOperationMode, Action<string, Utils.WPF.Stores.MessageTypes> AddMessage)
        {

            // set up an action to run inside a Revit transaction
            bool actionInTranny()
            {
                try
                {
                    //update single family instance
                    return UpdateProperties(doc, familyInstance, roomData, pushOperationMode, AddMessage);
                }
                catch (Exception ex)
                {
                    //log the exception
                    AddMessage($"Error updating family instance [{familyInstance.Id}] with room data [{roomData.Id.Value}]: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                    return false;
                }
            }

            bool transactionFlag = duHastNet.RevitUtils.Transactions.TransactionUtils.InTransaction(
                doc, $"Pushing room {roomData.Id.Value}", actionInTranny);

            return transactionFlag;
        }


        /// <summary>
        /// Check out family instances in the document
        /// </summary>
        /// <param name="doc">Current Revit document</param>
        /// <param name="processElementIds">The ids of elements to process</param>
        /// <param name="roomIdByFamilyInstanceIdMapper">a dictioanry mapping a family id to a room id</param>
        /// <param name="AddMessage">Function to provide user feedback</param>
        /// <returns></returns>
        public static HashSet<ElementId> CheckOutFamilyInstances(
            Document doc,
            HashSet<ElementId> processElementIds,
            Dictionary<ElementId, string> roomIdByFamilyInstanceIdMapper,
            Action<string, Utils.WPF.Stores.MessageTypes> AddMessage
            )
        {
            // create a transaction with central option
            // instructing Revit not to wait for the lock
            // this is done to avoid deadlocks when multiple users are trying to work on the same elements
            TransactWithCentralOptions transactWithCentralOptions = new();
            duHastNet.RevitUtils.Transactions.TransactionCallBack transactionCallBack = new(shouldWaitForLock: false);
            transactWithCentralOptions.SetLockCallback(transactionCallBack);

            //attempt to check out all elements
            ISet<ElementId> successfullyCheckedOutIds = WorksharingUtils.CheckoutElements(doc, processElementIds, transactWithCentralOptions);

            StringBuilder stringBuilder = new();
            //collect all room ids that were not checked out successfully
            foreach (var id in processElementIds)
            {
                if (!successfullyCheckedOutIds.Contains(id))
                {
                    // get the room id from the family instance
                    string roomId = roomIdByFamilyInstanceIdMapper[id];
                    stringBuilder.Append($"\nFailed to check out family instance [{id.Value}]. Skipping update for room [{roomId}].");
                }
            }

            //check if stringBuilder is empty
            if (stringBuilder.Length > 0)
            {
                // log the message
                AddMessage(stringBuilder.ToString(), Utils.WPF.Stores.MessageTypes.Error);
            }

            // Remove elements that could not be checked out
            processElementIds.RemoveWhere(id => !successfullyCheckedOutIds.Contains(id));

            //return the successfully checked out elements
            return processElementIds;
        }

        /// <summary>
        /// Update the properties of multiple family instances with the room data
        /// </summary>
        /// <param name="doc">The current Revit document</param>
        /// <param name="familyData"></param>
        /// <param name="AddMessage"> Function to log messages</param>
        /// <param name="updateId">If true Id will be updated during th update process to the id in the room data model, if false ID will be left as is. ( usefull for split room updates )</param>
        /// <returns>True if the update was successful, false if not</returns>
        /// <exception cref="Exception"></exception>
        public static bool UpdateMultipleFamilyInstances(
            Document doc,
            Dictionary<string, (duHastNet.PushIt.Models.RoomDataModel, List<FamilyInstance>)> familyData,
            Action<string, Utils.WPF.Stores.MessageTypes> AddMessage,
            bool updateId)
        {
            // set up an action to run inside a Revit transaction
            bool actionInTranny()
            {
                // keep track of the overall success of the wipe operation
                bool overallUpdateSuccess = true;

                // create a hash set to store the element ids of the family instances
                HashSet<ElementId> processElementIds = [];

                //create a set recording the family instance id to room id mapping
                Dictionary<ElementId, string> familyInstancesByRoomId = []; // room id -> family instance ids

                //build list of all family instance ids to check out
                foreach (var (roomData, familyInstances) in familyData.Values)
                {

                    foreach (var familyInstance in familyInstances)
                    {
                        processElementIds.Add(familyInstance.Id);
                        familyInstancesByRoomId[familyInstance.Id] = roomData.Id.Value;
                    }
                }

                // check if the document is workshared and if so attempt to check out the elements to be edited
                if (doc.IsWorkshared)
                {

                    // attempt to check out elements prior to updating them
                    processElementIds = CheckOutFamilyInstances(
                        doc: doc,
                         processElementIds: processElementIds,
                         roomIdByFamilyInstanceIdMapper: familyInstancesByRoomId,
                         AddMessage: AddMessage
                    );

                    //check if any elements were checked out successfully
                    if (processElementIds.Count == 0)
                    {
                        AddMessage("Failed to check out any family instances. Please try again later.", Utils.WPF.Stores.MessageTypes.Error);
                        return false;
                    }
                }

                // run this outside of a try catch so the transaction can be rolled back if update fails
                // loop over instances and update with room data
                foreach (var (roomData, familyInstances) in familyData.Values)
                {
                    // loop over instances and update with blank room data
                    foreach (var familyInstance in familyInstances)
                    {
                        //only update if the family instance is checked out
                        if (!processElementIds.Contains(familyInstance.Id))
                        {
                            // no need to pop a message to the user here since already logged above
                            continue;
                        }

                        // update the family instance
                        bool flag_update = UpdateProperties(
                            doc: doc,
                            familyInstance: familyInstance,
                            roomData: roomData,
                            pushMode: duHastNet.PushIt.Utilities.PushMode.Push,
                            AddMessage: AddMessage,
                            updateId: updateId
                        );

                        //log the overall success of the update
                        overallUpdateSuccess = overallUpdateSuccess && flag_update;

                        // if the update fails throw an exception to roll back the transaction
                        if (!flag_update)
                        {
                            throw new Exception("Failed to update family instance");
                        }
                    }
                }
                // if all updates are successful return true
                return overallUpdateSuccess;
            }

            // run the action in a transaction
            bool transactionFlag = duHastNet.RevitUtils.Transactions.TransactionUtils.InTransaction(
                doc, "Updating room data", actionInTranny);
            return transactionFlag;
        }



        /// <summary>
        /// Wipe the properties of multiple family instances with the room data
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="familyInstances"></param>
        /// <param name="sampleRoom"></param>
        /// <returns>True if the update was successful, false if not</returns>
        /// <exception cref="Exception"></exception>
        public static bool WipeMultipleFamilyInstances(Document doc, List<FamilyInstance> familyInstances, Models.RoomDataModel sampleRoom, Action<string, Utils.WPF.Stores.MessageTypes> AddMessage)
        {

            //update all room data properties
            Models.RoomDataProperty Id = new(sampleRoom.Id.Name, sampleRoom.Id.ParameterGUID, sampleRoom.Id.ParameterName, "", sampleRoom.Id.ShowInUI, sampleRoom.Id.IsReadOnly, true);

            List<Models.RoomDataProperty> otherProperties = [];

            foreach (var property in sampleRoom.Properties)
            {
                Models.RoomDataProperty newProperty = new(property.Name, property.ParameterGUID, property.ParameterName, "", property.ShowInUI, property.IsReadOnly, false);
                otherProperties.Add(newProperty);
            }

            // setup an empty room data model
            Models.RoomDataModel emptyRoom = new(Id, otherProperties);

            // set up an action to run inside a Revit transaction
            bool actionInTranny()
            {
                //run this outside of a try catch so the transaction can be rolled back if update fails
                // loop over instances and update with blank room data
                foreach (var familyInstance in familyInstances)
                {
                    // update the family instance
                    bool flag_update = UpdateProperties(doc, familyInstance, emptyRoom, duHastNet.PushIt.Utilities.PushMode.Push, AddMessage);

                    // if the update fails throw an exception to roll back the transaction and attempt to update one by one
                    if (!flag_update)
                    {
                        throw new Exception("Failed to update family instance");
                    }
                }
                // if all updates are successful return true
                return true;
            }

            // run the action in a transaction
            bool transactionFlag = duHastNet.RevitUtils.Transactions.TransactionUtils.InTransaction(
                doc, "Wiping stale room data", actionInTranny);

            return transactionFlag;
        }
    }
}
