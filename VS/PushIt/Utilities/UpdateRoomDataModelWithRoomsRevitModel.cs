using RevitUtils;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Utilities
{
    public static class UpdateRoomDataModelWithRoomsRevitModelUtils
    {

        /// <summary>
        /// Attach the rooms from the revit model to the rooms in the data model based on the room id property
        /// <\summary>
        public static List<Models.RoomsDataModel> UpdateRoomDataModelWithRoomsRevitModel(
            List<Models.RoomsDataModel> roomsDataModel, 
            List<Models.RoomsRevit> roomsRevit,
            string revitModelActiveDesignSetName,
            string revitModelActiveDesignOptionName
        )
        {
            // build a dictionary of room revit id to store all rooms with the same id
            Dictionary<string, List<Models.RoomsRevit>> roomsRevitById = new Dictionary<string, List<Models.RoomsRevit>>();
            foreach (Models.RoomsRevit revitRoom in roomsRevit)
            {
                if (!roomsRevitById.ContainsKey(revitRoom.Id))
                {
                    roomsRevitById[revitRoom.Id] = new List<Models.RoomsRevit>();
                }
                roomsRevitById[revitRoom.Id].Add(revitRoom);
            }

            // loop over all rooms in the data model and check if they exist in the revit model
            foreach (Models.RoomsDataModel roomDataModel in roomsDataModel)
            {
                // clear the list of matching rooms in revit from the room in the data model
                roomDataModel.ClearMatchingRevitRooms();

                // check if the room id exists in the revit model
                if (!roomsRevitById.ContainsKey(roomDataModel.Id.Value))
                {
                    continue;
                }

                // iterate over all rooms with the same id and check if they match the active design set and design option
                // if they do, add them to the list of matching rooms in the data model
                foreach (Models.RoomsRevit revitRoom in roomsRevitById[roomDataModel.Id.Value])
                {
                    bool addRoom = false;

                    // check if the family is placed in the active design option / set
                    if (revitRoom.DesignOption == revitModelActiveDesignOptionName && revitRoom.DesignSet == revitModelActiveDesignSetName)
                    {
                        addRoom = true;
                    }
                    // check if the family is placed in the main model
                    else if (revitRoom.DesignOption == DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME 
                        && revitRoom.DesignSet == DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME)
                    {
                        addRoom = true;
                    }
                    // check if the family is placed in another design sets primary design option
                    // and the main model is active
                    else if (revitModelActiveDesignSetName == DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME 
                        && revitRoom.DesignOptionIsPrimary)
                    {
                        addRoom = true;
                    }
                    //check if the family is in a primary design option which does not match the active design set
                    else if (revitRoom.DesignOptionIsPrimary && revitRoom.DesignSet != revitModelActiveDesignSetName)
                    {
                        addRoom = true;
                    }

                    if (addRoom)
                    {
                        roomDataModel.AddMatchingRevitRoom(revitRoom);
                    }
                }

                //Remove the matched families from the dictionary to speed up the search
                // check if the room id exists in the revit model
                if (!roomsRevitById.ContainsKey(roomDataModel.Id.Value))
                {
                    roomsRevitById.Remove(roomDataModel.Id.Value);
                }

            }

            // return the updated data model
            return roomsDataModel;
        }
    }
}
