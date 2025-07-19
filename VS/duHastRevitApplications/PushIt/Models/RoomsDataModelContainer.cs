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
                if (existingRoom.ConflictsById(room))
                {
                    // throw an exception
                    throw new Exceptions.RoomConflictException(
                        existingRoom, room);

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
            return [.. _rooms, .. _newRooms];
        }

        /// <summary>
        /// Clears the list of rooms from the Schedule Of Accomodation
        /// </summary>
        public void ClearRooms()
        {
            _rooms = [];
        }

        /// <summary>
        /// Clears the list of new rooms added through the Push It UI
        /// </summary>
        public void ClearNewRooms()
        {
            _newRooms = [];
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
        public void RemovePlacedRevitRoom(long revitElementId)
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
                else if (room.MatchingSplitRevitRooms.Any(x => x.RevitElementId == revitElementId))
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
        /// <param name="revitElemntId">The element Id of the family representing this room</param>
        public void RemoveNewPlacedRevitRoom(string roomId, long revitElementId)
        {
            //flag indicating whether the new room has no matching Revit room after removing the placed room
            bool removeRoomFromDataModel = false;
            RoomDataModel roomToRemove = null;
            foreach (var room in _newRooms)
            {
                if (room.Id.Value == roomId)
                {
                    // remove the placed room from the data model
                    room.MatchingRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);
                    // update rooms read-only properties from revit room
                    room.UpdateReadProperties();

                    // check if the room has no matching Revit room
                    if (room.MatchingRevitRooms.Count == 0)
                    {
                        // set the flag to true
                        removeRoomFromDataModel = true;
                        // set the room to remove
                        roomToRemove = room;
                    }
                    break;
                }
            }

            // if the room has no matching Revit room, remove it from the data model
            if (removeRoomFromDataModel)
            {
                // remove the room from the data model
                _newRooms.Remove(roomToRemove);
            }
        }

        /// <summary>
        /// Adds the placed room to the list of rooms from the Schedule Of Accomodation
        /// </summary>
        /// <param name="roomId"></param>
        /// <param name="revitRoom"></param>
        public void AddPlacedRevitRoom(string roomId, Models.RoomRevit revitRoom)
        {
            //get the room id without the split mode indicator
            string roomIdWithoutSplit = Utilities.PushModeUtils.GetIdWithoutSplitModeIndicator(roomId);

            foreach (var room in _rooms)
            {
                // check if the room id is the same as the one in the data model
                if (room.Id.Value == roomIdWithoutSplit)
                {
                    //check if this is a standard room ( room id is the same as the id without split mode indicator)
                    if (roomId == roomIdWithoutSplit)
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
        public void AddPlacedNewRevitRoom(string roomId, Models.RoomRevit revitRoom)
        {
            bool roomFound = false;

            // the lieklyhood of this happening is very low, but just in case since the id contains a time stamp down to the milisecond
            foreach (var room in _newRooms)
            {
                if (room.Id.Value == roomId)
                {
                    // add the placed room to the data model
                    room.AddMatchingRevitRoom(revitRoom);
                    // update rooms read-only properties from revit room
                    room.UpdateReadProperties();

                    // set the room found flag to true
                    roomFound = true;
                }
            }

            //if nor matching room was found...which is likely add a new room
            if (!roomFound)
            {

                List<Models.RoomDataProperty> properties = [];
                //get the properties
                foreach (var property in revitRoom.Properties)
                {
                    // add the property to the new room
                    properties.Add(new Models.RoomDataProperty(
                        name: property.Name, 
                        parameterGUID: property.ParameterGUID,
                        parameterName: property.ParameterName, 
                        value: property.Value, 
                        showInUI: property.ShowInUI,
                        isReadOnly: property.IsReadOnly,
                        isUniqueId: property.IsUniqueId)
                    );
                }

                Models.RoomDataProperty idProperty = new(
                    name: revitRoom.Id.Name, 
                    parameterGUID: revitRoom.Id.ParameterGUID,
                    parameterName: revitRoom.Id.ParameterName, 
                    value: revitRoom.Id.Value, 
                    showInUI: revitRoom.Id.ShowInUI,
                    isReadOnly: revitRoom.Id.IsReadOnly, 
                    isUniqueId: true); //unique id

                // add the placed room to the data model
                Models.RoomDataModel newRoom = new(
                    id: idProperty,
                    otherProperties: properties);


                // add the placed room to the data model
                newRoom.AddMatchingRevitRoom(revitRoom);
                newRoom.UpdateReadProperties();

                // add the new room to the data model
                _newRooms.Add(newRoom);
            }
        }

        public RoomsDataModelContainer()
        {
            _rooms = [];
            _newRooms = [];
        }
    }
}
