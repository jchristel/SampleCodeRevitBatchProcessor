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

using System.Collections.Generic;

namespace duHastNet.PushIt.Utilities
{
    public static class UpdateRoomDataModelWithRoomsRevitModelUtils
    {
        /// <summary>
        /// Check if the room should be added to the data model based on the active design set and design option
        /// </summary>
        /// <param name="revitRoom"></param>
        /// <param name="revitModelActiveDesignSetName"></param>
        /// <param name="revitModelActiveDesignOptionName"></param>
        /// <returns></returns>
        public static bool AddRoom(
            Models.RoomsRevit revitRoom,
            string revitModelActiveDesignSetName,
            string revitModelActiveDesignOptionName)
        {
            bool addRoom = false;

            // check if the family is placed in the active design option / set
            if (revitRoom.DesignOption == revitModelActiveDesignOptionName && revitRoom.DesignSet == revitModelActiveDesignSetName)
            {
                addRoom = true;
            }
            // check if the family is placed in the main model
            else if (revitRoom.DesignOption == duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME
                && revitRoom.DesignSet == duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME)
            {
                addRoom = true;
            }
            // check if the family is placed in another design sets primary design option
            // and the main model is active
            else if (revitModelActiveDesignSetName == duHastNet.RevitUtils.DesignSetAndOptions.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME
                && revitRoom.DesignOptionIsPrimary)
            {
                addRoom = true;
            }
            //check if the family is in a primary design option which does not match the active design set
            else if (revitRoom.DesignOptionIsPrimary && revitRoom.DesignSet != revitModelActiveDesignSetName)
            {
                addRoom = true;
            }

            return addRoom;
        }

        /// <summary>
        /// Attach the rooms from the revit model to the rooms in the data model based on the room id property
        /// <\summary>
        public static List<Models.RoomDataModel> UpdateRoomDataModelWithRoomsRevitModel(
            List<Models.RoomDataModel> roomsDataModel, 
            List<Models.RoomsRevit> roomsRevit,
            string revitModelActiveDesignSetName,
            string revitModelActiveDesignOptionName
        )
        {
            // build a dictionary of room revit id to store all rooms with the same id
            Dictionary<string, List<Models.RoomsRevit>> roomsRevitById = new Dictionary<string, List<Models.RoomsRevit>>();
            foreach (Models.RoomsRevit revitRoom in roomsRevit)
            {
                if (!roomsRevitById.ContainsKey(revitRoom.Id.Value))
                {
                    roomsRevitById[revitRoom.Id.Value] = new List<Models.RoomsRevit>();
                }
                roomsRevitById[revitRoom.Id.Value].Add(revitRoom);
            }

            // loop over all rooms in the data model and check if they exist in the revit model
            foreach (Models.RoomDataModel roomDataModel in roomsDataModel)
            {
                // clear the list of matching rooms in revit from the room in the data model
                roomDataModel.ClearMatchingRevitRooms();
                roomDataModel.ClearMatchingSplitRevitRooms();

                // check if the room id exists in the revit model or a split room
                if (!roomsRevitById.ContainsKey(roomDataModel.Id.Value) && 
                    !roomsRevitById.ContainsKey(Utilities.PushModeUtils.GetSplitModeIdValue(roomDataModel.Id.Value)))
                {
                    continue;
                }

                // check if the room id exists in the revit model
                if (roomsRevitById.ContainsKey(roomDataModel.Id.Value))
                {
                    // iterate over all rooms with the same id and check if they match the active design set and design option
                    // if they do, add them to the list of matching rooms in the data model
                    foreach (Models.RoomsRevit revitRoom in roomsRevitById[roomDataModel.Id.Value])
                    {
                        if (AddRoom(
                            revitRoom: revitRoom,
                            revitModelActiveDesignSetName: revitModelActiveDesignSetName,
                            revitModelActiveDesignOptionName: revitModelActiveDesignOptionName))
                        {
                            roomDataModel.AddMatchingRevitRoom(revitRoom);
                        }
                    }

                    //Remove the matched families from the dictionary to speed up the search
                    roomsRevitById.Remove(roomDataModel.Id.Value);
                    
                }

                //get the split room id 
                string splitRoomId = Utilities.PushModeUtils.GetSplitModeIdValue(roomDataModel.Id.Value);
                
                //check if there is an entry for the split room id in the dictionary
                // if not, continue
                if (roomsRevitById.ContainsKey(splitRoomId))
                {
                    // check if the room id exists in the revit model as a split room
                    foreach (Models.RoomsRevit revitRoom in roomsRevitById[splitRoomId])
                    {
                        if (AddRoom(
                            revitRoom: revitRoom,
                            revitModelActiveDesignSetName: revitModelActiveDesignSetName,
                            revitModelActiveDesignOptionName: revitModelActiveDesignOptionName))
                        {
                            roomDataModel.AddMatchingSplitRevitRoom(revitRoom);
                        }
                    }

                    //Remove the matched families from the dictionary to speed up the search
                    roomsRevitById.Remove(splitRoomId);
                }
            }


            // loop over all rooms in the data model and update the read only properties from matched Revit rooms
            foreach (Models.RoomDataModel roomDataModel in roomsDataModel)
            {
                roomDataModel.UpdateReadProperties();
            }

            // return the updated data model
            return roomsDataModel;
        }
    }
}
