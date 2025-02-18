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
        public static bool updateSingleFamilyInstance(Document doc, FamilyInstance familyInstance, Models.RoomDataModel roomData, bool safetyOff )
        {

            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                try
                {
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
               
                foreach (var familyInstance in familyInstances)
                {
                    bool flag_update = updateProperties(doc, familyInstance, emptyRoom, false);
                    if (!flag_update)
                    {
                        throw new Exception("Failed to update family instance");
                    }
                }
                return true;
            };


            bool transactionFlag = RevitUtils.TransactionUtils.inTransaction(
                doc, "Wiping stale room data", actionInTranny);

            return transactionFlag;
        }
    }
}
