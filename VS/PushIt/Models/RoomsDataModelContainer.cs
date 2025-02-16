using Autodesk.Revit.DB.Architecture;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RoomsDataModelContainer
    {
        public List<Models.RoomsDataModel> _rooms;

        public void AddRoom(Models.RoomsDataModel room)
        {
            //check if rooms are conflicting by id value
            foreach (var existingRoom in _rooms)
            {
                if (existingRoom.Conflicts(room))
                {
                    // throw an exception
                    throw new Exceptions.RoomConflictException(
                        existingRoom, room);
                }
            }
                
            _rooms.Add(room);
                
        }
        public List<Models.RoomsDataModel> GetAllRooms()
        {
            return _rooms;
        }

        public void ClearRooms() 
        {
            _rooms = new List<Models.RoomsDataModel>();
        }

        public void RemovePlacedRevitRoom(int revitElementId)
        {
            foreach (var room in _rooms)
            {
                // need to update the area designed value...
                //check if the room has the placed room
                if (room.MatchingRevitRooms.Any(x => x.RevitElementId == revitElementId))
                {
                    // remove the placed room from the data model
                    room.MatchingRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);
                    // update the area designed value depending on number of placed rooms
                    if (room.MatchingRevitRooms.Count == 1)
                        room.AreaDesigned.Value = room.MatchingRevitRooms[0].AreaDesigned;
                    else if(room.MatchingRevitRooms.Count > 1)
                        room.AreaDesigned.Value = "Multiple";
                    else
                        room.AreaDesigned.Value = "0.0";
                    break;
                }
                room.MatchingRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);
            }
        }

        public void AddPlacedRevitRoom(string roomId, Models.RoomsRevit revitRoom)
        {
            foreach (var room in _rooms)
            {
                if (room.Id.Value == roomId)
                {
                    // add the placed room to the data model
                    room.AddMatchingRevitRoom(revitRoom);
                    // update the area designed value depending on number of placed rooms
                    if (room.MatchingRevitRooms.Count == 1)
                        room.AreaDesigned.Value = revitRoom.AreaDesigned;
                    else
                        room.AreaDesigned.Value = "Multiple";
                    break;
                }
            }
        }

        public RoomsDataModelContainer()
        {
            _rooms = new List<Models.RoomsDataModel>();
        }
    }
}
