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
using Autodesk.Revit.DB;


namespace duHast.PushIt.Utilities.Revit
{
    public static class FamilyUpdate
    {
        /// <summary>
        /// Update the properties of a family instance with the room data
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="familyInstance"></param>
        /// <param name="roomData"></param>
        /// <param name="safetyOff"></param>
        /// <returns></returns>
        public static bool UpdateProperties(Document doc, FamilyInstance familyInstance, Models.RoomDataModel roomData, bool safetyOff, Action<string, Utils.WPF.Stores.MessageTypes> AddMessage)
        {

            // set up a variable to store the name of the property that is being updated in case of an exception
            string propertyName = "";

            try
            {
                string room_id = roomData.Id.Value;
                if (safetyOff)
                {
                    // in the moment, this will just push the same id again without changing it
                    //string userName = doc.Application.Username;
                    //string dateStamp = DateTime.Now.ToString("yyyy_MM_dd_HH_mm_ss");
                    // room_id = $"{room_id}::{userName}<{dateStamp}>";
                }

                // set the room id parameter
                bool flagId = duHast.RevitUtils.Parameters.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.Id.ParameterGUID, room_id);
                AddMessage($"Updated room id with value [{room_id}] for family instance [{familyInstance.Id}] with status: [{flagId}]", Utils.WPF.Stores.MessageTypes.Log);
                
                //update other properties
                bool flagOtherProperties = true;

                // loop over the properties and update them
                foreach (var property in roomData.Properties)
                {
                    propertyName = property.Name;
                    // skip read only properties
                    if (property.IsReadOnly)
                    {
                        AddMessage($"Skipping read only property [{property.Name}] for family instance [{familyInstance.Id}]", Utils.WPF.Stores.MessageTypes.Log);
                        continue;
                    }
                    
                    // update the property depending on whether it has a GUID or not
                    if (property.ParameterGUID != "")
                    {
                        bool flag = duHast.RevitUtils.Parameters.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, property.ParameterGUID, property.Value);
                        AddMessage($"Updated shared parameter property [{property.Name}] with value [{property.Value}] for family instance [{familyInstance.Id}] with status: {flag}", Utils.WPF.Stores.MessageTypes.Log);
                        flagOtherProperties = flagOtherProperties && flag;
                    }
                    else
                    {
                        bool flag = duHast.RevitUtils.Parameters.ParaUtils.SetParameterValueByName(familyInstance, property.Name, property.Value);
                        AddMessage($"Updated non shared parameter property [{property.Name}] with value [{property.Value}] for family instance [{familyInstance.Id}] with status: {flag}", Utils.WPF.Stores.MessageTypes.Log);
                        flagOtherProperties = flagOtherProperties && flag;
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
        /// <param name="safetyOff"></param>
        /// <returns> 
        /// True if the update was successful, false if not
        /// </returns>
        public static bool UpdateSingleFamilyInstance(Document doc, FamilyInstance familyInstance, Models.RoomDataModel roomData, bool safetyOff , Action<string, Utils.WPF.Stores.MessageTypes> AddMessage)
        {

            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                try
                {
                    //update single family instance
                    return UpdateProperties(doc, familyInstance, roomData, safetyOff, AddMessage);
                }
                catch (Exception ex)
                {
                    //log the exception
                    AddMessage($"Error updating family instance [{familyInstance.Id}] with room data [{roomData.Id.Value}]: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                    return false;
                }
            };

            bool transactionFlag =  duHast.RevitUtils.Transactions.TransactionUtils.InTransaction(
                doc, $"Pushing room {roomData.Id.Value}", actionInTranny);

            return transactionFlag;

        }


        /// <summary>
        /// Update the properties of multiple family instances with the room data
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="familyData"></param>
        /// <returns>True if the update was successful, false if not</returns>
        /// <exception cref="Exception"></exception>
        public static bool UpdateMultipleFamilyInstances(Document doc, Dictionary<string, (duHast.PushIt.Models.RoomDataModel, List<FamilyInstance>)> familyData, Action<string, Utils.WPF.Stores.MessageTypes> AddMessage)
        {
            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                // keep track of the overall success of the wipe operation
                bool overallUpdateSuccess = true;

                //run this outside of a try catch so the transaction can be rolled back if update fails
                // loop over instances and update with room data
                foreach (var (roomData, familyInstances) in familyData.Values)
                {
                    // loop over instances and update with blank room data
                    foreach (var familyInstance in familyInstances)
                    {
                        // update the family instance
                        bool flag_update = UpdateProperties(doc, familyInstance, roomData, false, AddMessage);
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
            };

            // run the action in a transaction
            bool transactionFlag = duHast.RevitUtils.Transactions.TransactionUtils.InTransaction(
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
            Models.RoomDataProperty Id =  new Models.RoomDataProperty(sampleRoom.Id.Name, sampleRoom.Id.ParameterGUID, sampleRoom.Id.ParameterName,"", sampleRoom.Id.ShowInUI, sampleRoom.Id.IsReadOnly);
            
            List<Models.RoomDataProperty> otherProperties = new List<Models.RoomDataProperty>();

            foreach (var property in sampleRoom.Properties)
            {
                Models.RoomDataProperty newProperty = new Models.RoomDataProperty(property.Name, property.ParameterGUID, property.ParameterName, "", property.ShowInUI, property.IsReadOnly);
                otherProperties.Add(newProperty);
            }

            // setup an empty room data model
            Models.RoomDataModel emptyRoom = new Models.RoomDataModel(Id, otherProperties);

            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                //run this outside of a try catch so the transaction can be rolled back if update fails
                // loop over instances and update with blank room data
                foreach (var familyInstance in familyInstances)
                {
                    // update the family instance
                    bool flag_update = UpdateProperties(doc, familyInstance, emptyRoom, false, AddMessage);

                    // if the update fails throw an exception to roll back the transaction and attempt to update one by one
                    if (!flag_update)
                    {
                        throw new Exception("Failed to update family instance");
                    }
                }
                // if all updates are successful return true
                return true;
            };

            // run the action in a transaction
            bool transactionFlag = duHast.RevitUtils.Transactions.TransactionUtils.InTransaction(
                doc, "Wiping stale room data", actionInTranny);

            return transactionFlag;
        }
    }
}
