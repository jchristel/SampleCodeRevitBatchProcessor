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

namespace duHastNet.PushIt.Utilities.Revit
{
    public static class RevitRoomObjectsConverter
    {

        public static Models.RoomsRevit ConvertSingleFamilyToRevitRoom(
            FamilyInstance familyInstance, 
            Models.RoomDataModel sampleModelRoom, 
            Dictionary<string, ElementId> sharedParameterIdsByGUIDs
            )
        {
            // get the parameters of the family instance
            IList<Parameter> parameters = familyInstance.GetOrderedParameters();

            // get the id value
            string id_value = duHastNet.RevitUtils.Parameters.SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.Id.ParameterGUID]);

            // ignore fam instance if id is null or empt
            if (id_value == null || id_value == "")
            {
                return null;
            }

            // setup the id property
            Models.RoomDataProperty IdProperty = new Models.RoomDataProperty(
                name: sampleModelRoom.Id.ParameterName,
                value: id_value,
                parameterGUID: sampleModelRoom.Id.ParameterGUID,
                parameterName: sampleModelRoom.Id.ParameterName,
                showInUI:sampleModelRoom.Id.ShowInUI,
                isReadOnly: sampleModelRoom.Id.IsReadOnly);

            // get the other properties and store in list
            List<Models.RoomDataProperty> properties = new List<Models.RoomDataProperty>();

            foreach (Models.RoomDataProperty property in sampleModelRoom.Properties)
            {
                string value = "";
                //check if property is retrieved from shared parameter
                if (property.ParameterGUID != "")
                {
                    // get the value of the property
                    value = duHastNet.RevitUtils.Parameters.SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[property.ParameterGUID]);
                }
                else
                {
                    //standard parameter
                    value = duHastNet.RevitUtils.Parameters.ParaUtils.GetParameterValueByName(familyInstance, property.ParameterName);
                }

                // create a new room data property
                Models.RoomDataProperty roomDataProperty = new Models.RoomDataProperty(
                    name: property.Name,
                    parameterGUID: property.ParameterGUID,
                    parameterName: property.ParameterName,
                    value: value,
                    showInUI: property.ShowInUI,
                    isReadOnly: property.IsReadOnly);
                // add to the list of properties
                properties.Add(roomDataProperty);
            }
            
            // get the design set and option data
            var designSetAndOptionData = duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionsUtils.GetDesignSetOptionInfo(familyInstance.Document, familyInstance);

            // create a new revit room
            Models.RoomsRevit revitRoom = new Models.RoomsRevit(
                id: IdProperty,
                properties: properties,
                designSet: designSetAndOptionData[duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.DESIGN_SET_NAME].ToString(),
                designOption: designSetAndOptionData[duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.DESIGN_OPTION_NAME].ToString(),
                designOptionIsPrimary: (bool)designSetAndOptionData[duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.DESIGN_OPTION_IS_PRIMARY],
                familyInstance.Id.IntegerValue);

            return revitRoom;
        }
        public static List<duHastNet.PushIt.Models.RoomsRevit> ConvertFamiliesToRevitRooms(
            List<FamilyInstance> familyInstances, 
            Models.RoomDataModel sampleModelRoom,
            Action<string, Utils.WPF.Stores.MessageTypes> AddMessage)
        {
            // create a list of revit rooms
            List<Models.RoomsRevit> revitRooms = new List<duHastNet.PushIt.Models.RoomsRevit>();

            // get shared parameter ids by GUID
            Dictionary<string, ElementId> sharedParameterIdsByGUIDs = duHastNet.RevitUtils.Parameters.SharedParaUtils.GetSharedParameterIdsByGUID(familyInstances[0].Document);

            foreach (FamilyInstance familyInstance in familyInstances)
            {
                try
                {
                    // create a new revit room
                    Models.RoomsRevit revitRoom = ConvertSingleFamilyToRevitRoom(familyInstance, sampleModelRoom, sharedParameterIdsByGUIDs);

                    // ignore if revit room is null
                    if (revitRoom == null)
                    {
                        continue;
                    }

                    // add to list to be returned
                    revitRooms.Add(revitRoom);
                }
                catch (Exception ex)
                {
                    AddMessage($"Error converting family instance to revit room: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                }
                
            }
            AddMessage($"Converted {revitRooms.Count} family instances to revit rooms.", Utils.WPF.Stores.MessageTypes.Log);
            return revitRooms;
        }
    }
}
