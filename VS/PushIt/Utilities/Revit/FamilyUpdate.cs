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


namespace PushIt.Utilities.Revit
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
        public static bool updateProperties(Document doc, FamilyInstance familyInstance, Models.RoomDataModel roomData, bool safetyOff)
        {
            try
            {
                string room_id = roomData.Id.Value;
                if (safetyOff)
                {
                    string userName = doc.Application.Username;
                    string dateStamp = DateTime.Now.ToString("yyyy_MM_dd_HH_mm_ss");
                    room_id = $"{room_id}::{userName}<{dateStamp}>";
                }

                // set the room id parameter
                bool flag_Id = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.Id.ParameterGUID, room_id);

                // set the room area briefed parameter
                bool flag_AreaBriefed = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.AreaBriefed.ParameterGUID, roomData.AreaBriefed.Value);
                // set the room name short parameter
                bool flag_NameShort = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.NameShort.ParameterGUID, roomData.NameShort.Value);
                // set the room department and subdepartment parameters
                bool flag_Department = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.Department.ParameterGUID, roomData.Department.Value);
                bool flag_SubDepartment = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.SubDepartment.ParameterGUID, roomData.SubDepartment.Value);

                return flag_Id && flag_AreaBriefed && flag_NameShort && flag_Department && flag_SubDepartment;
            }
            catch (Exception)
            {
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
        public static bool updateSingleFamilyInstance(Document doc, FamilyInstance familyInstance, Models.RoomDataModel roomData, bool safetyOff )
        {

            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                try
                {
                    //update single family instance
                    return updateProperties(doc, familyInstance, roomData, safetyOff);
                }
                catch (Exception)
                {
                    return false;
                }
            };

            bool transactionFlag =  RevitUtils.TransactionUtils.inTransaction(
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
        public static bool updateMultipleFamilyInstances(Document doc, Dictionary<string, (PushIt.Models.RoomDataModel, List<FamilyInstance>)> familyData)
        {
            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                //run this outside of a try catch so the transaction can be rolled back if update fails
                // loop over instances and update with room data
                foreach (var (roomData, familyInstances) in familyData.Values)
                {
                    // loop over instances and update with blank room data
                    foreach (var familyInstance in familyInstances)
                    {
                        // update the family instance
                        bool flag_update = updateProperties(doc, familyInstance, roomData, false);
                        // if the update fails throw an exception to roll back the transaction and attempt to update one by one
                        if (!flag_update)
                        {
                            throw new Exception("Failed to update family instance");
                        }
                    }
                }
                // if all updates are successful return true
                return true;
            };

            // run the action in a transaction
            bool transactionFlag = RevitUtils.TransactionUtils.inTransaction(
                doc, "Wiping stale room data", actionInTranny);
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
        public static bool wipeMultipleFamilyInstances(Document doc, List<FamilyInstance> familyInstances, Models.RoomDataModel sampleRoom)
        {
            // setup an empty room data model
            Models.RoomDataModel emptyRoom = new Models.RoomDataModel();
            //update all room data properties
            emptyRoom.Id =  new Models.RoomDataProperty(sampleRoom.Id.Name, sampleRoom.Id.ParameterGUID, sampleRoom.Id.ParameterName,"");
            emptyRoom.AreaBriefed = new Models.RoomDataProperty(sampleRoom.AreaBriefed.Name, sampleRoom.AreaBriefed.ParameterGUID, sampleRoom.AreaBriefed.ParameterName, "0.0");
            emptyRoom.NameShort = new Models.RoomDataProperty(sampleRoom.NameShort.Name, sampleRoom.NameShort.ParameterGUID, sampleRoom.NameShort.ParameterName, "");
            emptyRoom.Department = new Models.RoomDataProperty(sampleRoom.Department.Name, sampleRoom.Department.ParameterGUID, sampleRoom.Department.ParameterName, "");
            emptyRoom.SubDepartment = new Models.RoomDataProperty(sampleRoom.SubDepartment.Name, sampleRoom.SubDepartment.ParameterGUID, sampleRoom.SubDepartment.ParameterName, "");


            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                //run this outside of a try catch so the transaction can be rolled back if update fails
                // loop over instances and update with blank room data
                foreach (var familyInstance in familyInstances)
                {
                    // update the family instance
                    bool flag_update = updateProperties(doc, familyInstance, emptyRoom, false);

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
            bool transactionFlag = RevitUtils.TransactionUtils.inTransaction(
                doc, "Wiping stale room data", actionInTranny);

            return transactionFlag;
        }
    }
}
