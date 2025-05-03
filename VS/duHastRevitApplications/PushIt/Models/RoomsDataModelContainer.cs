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
using System.Linq;


namespace duHastNet.PushIt.Models
{
    public class RoomsDataModelContainer
    {
        public List<Models.RoomDataModel> _rooms;

        public void AddRoom(Models.RoomDataModel room)
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
        public List<Models.RoomDataModel> GetAllRooms()
        {
            return _rooms;
        }

        public void ClearRooms() 
        {
            _rooms = new List<Models.RoomDataModel>();
        }

        public void RemovePlacedRevitRoom(int revitElementId)
        {
            foreach (var room in _rooms)
            {
                // need to update the area designed value...
                // check if the room has the placed room
                if (room.MatchingRevitRooms.Any(x => x.RevitElementId == revitElementId))
                {
                    // remove the placed room from the data model
                    room.MatchingRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);

                    // update rooms read-only properties from revit room
                    room.UpdateReadProperties();

                    break;
                }
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
                    // update rooms read-only properties from revit room
                    room.UpdateReadProperties();
                }
            }
        }

        public RoomsDataModelContainer()
        {
            _rooms = new List<Models.RoomDataModel>();
        }
    }
}
