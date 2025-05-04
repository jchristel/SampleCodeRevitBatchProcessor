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
        /// <summary>
        /// Rooms added throught the Schedule Of Accomodation load process
        /// </summary> 
        public List<Models.RoomDataModel> _rooms;

        /// <summary>
        /// Rooms added through the Push It UI which are in addition to the rooms from the Schedule Of Accomodation
        /// These rooms have as ID the word "New"
        /// The room ID is not unique, but the combined values of room properties marked as write are unique
        /// </summary>
        public List<Models.RoomDataModel> _newRooms;

        public void AddRoom(Models.RoomDataModel room)
        {
            //check if rooms are conflicting by id value
            foreach (var existingRoom in _rooms)
            {
                if (existingRoom.ConflictsById(room))
                {
                    // throw an exception
                    throw new Exceptions.RoomConflictException(
                        existingRoom, room);
                }
            }
                
            _rooms.Add(room);
                
        }

        /// <summary>
        /// Adds a new room to the list of new rooms if the properties are not conflicting with any other new room
        /// </summary>
        /// <param name="room"></param>
        public void AddNewRoom(Models.RoomDataModel room)
        {
            //check if rooms are conflicting by id value
            foreach (var existingRoom in _newRooms)
            {
                if (existingRoom.ConflictsByProperties(room))
                {
                    // there is a good chance that the room is already in the list
                    // if that is the case ignore the duplicate
                    return;

                }
            }
            _newRooms.Add(room);
        }

        /// <summary>
        /// Returns all rooms from the Schedule Of Accomodation
        /// </summary>
        /// <returns></returns>
        public List<Models.RoomDataModel> GetAllRooms()
        {
            return _rooms;
        }

        /// <summary>
        /// returns all new rooms added through the Push It UI
        /// </summary>
        public List<Models.RoomDataModel> GetAllNewRooms()
        {
            return _newRooms;
        }

        /// <summary>
        /// Returns all rooms from the Schedule Of Accomodation and all new rooms added through the Push It UI
        /// </summary>
        public List<Models.RoomDataModel> GetAllRoomsCombined()
        {
            return _rooms.Concat(_newRooms).ToList();
        }

        /// <summary>
        /// Clears the list of rooms from the Schedule Of Accomodation
        /// </summary>
        public void ClearRooms() 
        {
            _rooms = new List<Models.RoomDataModel>();
        }

        /// <summary>
        /// Clears the list of new rooms added through the Push It UI
        /// </summary>
        public void ClearNewRooms()
        {
            _newRooms = new List<Models.RoomDataModel>();
        }

        /// <summary>
        /// Clears the list of new rooms added through the Push It UI and the list of rooms from the Schedule Of Accomodation
        /// </summary>
        public void ClearAllRooms()
        {
            ClearRooms();
            ClearNewRooms();
        }

        /// <summary>
        /// Removes the placed room from the list of rooms from the Schedule Of Accomodation
        /// </summary>
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
                //check if any matching split rooms...
                else if ( room.MatchingSplitRevitRooms.Any(x=>x.RevitElementId == revitElementId))
                {
                    // remove the placed room from the data model
                    room.MatchingSplitRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);

                    // update rooms read-only properties from revit room
                    room.UpdateReadProperties();

                    break;
                }
            }
        }

        /// <summary>
        /// Removes the placed room from the list of new rooms added through the Push It UI
        /// </summary>
        /// <param name="propertyComparison">All write properties and their values in a string</param>
        /// <param name="revitElementId">The element Id of the family representing this room</param>
        public void RemoveNewPlacedRevitRoom(string propertyComparison, int revitElementId)
        {
            foreach (var room in _newRooms)
            {
                if (room.GetWritePropertiesAsString() == propertyComparison)
                {
                    // remove the placed room from the data model
                    room.MatchingRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);
                    // update rooms read-only properties from revit room
                    room.UpdateReadProperties();
                    break;
                }
            }
        }

        /// <summary>
        /// Adds the placed room to the list of rooms from the Schedule Of Accomodation
        /// </summary>
        /// <param name="roomId"></param>
        /// <param name="revitRoom"></param>
        public void AddPlacedRevitRoom(string roomId, Models.RoomsRevit revitRoom)
        {
            //get the room id without the split mode indicator
            string roomIdWithoutSplit = Utilities.PushModeUtils.GetIdWithoutSplitModeIndicator(roomId);

            foreach (var room in _rooms)
            {
                // check if the room id is the same as the one in the data model
                if (room.Id.Value == roomIdWithoutSplit)
                {
                    //check if this is a standard room ( room id is the same as the id without split mode indicator)
                    if (roomId==roomIdWithoutSplit)
                    {
                        // add the placed room to the data model
                        room.AddMatchingRevitRoom(revitRoom);
                    }
                    else
                    {
                        //must be a split room
                        // add the placed room to the data model
                        room.AddMatchingSplitRevitRoom(revitRoom);
                    }

                    // update rooms read-only properties from revit room
                    room.UpdateReadProperties();
                }
            }
        }

        /// <summary>
        /// Adds the placed room to the list of new rooms added through the Push It UI
        /// </summary>
        public void AddPlacedNewRevitRoom(string propertyComparison, Models.RoomsRevit revitRoom)
        {
            foreach (var room in _newRooms)
            {
                if (room.GetWritePropertiesAsString() == propertyComparison)
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
