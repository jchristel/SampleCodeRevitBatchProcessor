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

        /// <summary>
        /// Rooms added through the Push It UI which are the result of a split operation.
        /// Each entry is a standalone RoomDataModel with a split-suffixed ID
        /// ({parentId}::SPLIT::{counter}). Revit is the source of truth after the first push.
        /// </summary>
        public List<Models.RoomDataModel> _splitRooms;

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
        /// Returns all rooms from the Schedule Of Accomodation, all new rooms, and all split rooms.
        /// </summary>
        public List<Models.RoomDataModel> GetAllRoomsCombined()
        {
            return [.. _rooms, .. _newRooms, .. _splitRooms];
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
        /// Clears the list of split rooms
        /// </summary>
        public void ClearSplitRooms()
        {
            _splitRooms = [];
        }

        /// <summary>
        /// Clears all room lists: SoA rooms, new rooms, and split rooms.
        /// </summary>
        public void ClearAllRooms()
        {
            ClearRooms();
            ClearNewRooms();
            ClearSplitRooms();
        }

        /// <summary>
        /// Removes the placed room from the list of rooms from the Schedule Of Accomodation
        /// </summary>
        public void RemovePlacedRevitRoom(long revitElementId)
        {
            foreach (var room in _rooms)
            {
                if (room.MatchingRevitRooms.Any(x => x.RevitElementId == revitElementId))
                {
                    room.MatchingRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);
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
        /// Adds the placed room to the list of rooms from the Schedule Of Accomodation.
        /// Only handles standard (non-split, non-new) room IDs.
        /// </summary>
        public void AddPlacedRevitRoom(string roomId, Models.RoomRevit revitRoom)
        {
            foreach (var room in _rooms)
            {
                if (room.Id.Value == roomId)
                {
                    room.AddMatchingRevitRoom(revitRoom);
                    room.UpdateReadProperties();
                }
            }
        }

        /// <summary>
        /// Adds or updates a split room entry in _splitRooms from a Revit read-back.
        /// If a split room with the given splitRoomId already exists, its MatchingRevitRooms
        /// list is updated. Otherwise a new RoomDataModel is created and added.
        /// </summary>
        public void AddPlacedSplitRevitRoom(string splitRoomId, Models.RoomRevit revitRoom)
        {
            // look for an existing split room entry with this exact split ID
            var existing = _splitRooms.Find(r => r.Id.Value == splitRoomId);
            if (existing != null)
            {
                existing.AddMatchingRevitRoom(revitRoom);
                existing.UpdateReadProperties();
            }
            else
            {
                // build a new standalone RoomDataModel from the Revit read-back
                List<Models.RoomDataProperty> properties = [];
                foreach (var property in revitRoom.Properties)
                {
                    properties.Add(new Models.RoomDataProperty(
                        name: property.Name,
                        parameterGUID: property.ParameterGUID,
                        parameterName: property.ParameterName,
                        value: property.Value,
                        showInUI: property.ShowInUI,
                        isReadOnly: property.IsReadOnly,
                        isUniqueId: property.IsUniqueId,
                        revitTakesPrecedenceAfterInitialPush: property.RevitTakesPrecedenceAfterInitialPush
                    ));
                }

                Models.RoomDataProperty idProperty = new(
                    name: revitRoom.Id.Name,
                    parameterGUID: revitRoom.Id.ParameterGUID,
                    parameterName: revitRoom.Id.ParameterName,
                    value: revitRoom.Id.Value,
                    showInUI: revitRoom.Id.ShowInUI,
                    isReadOnly: revitRoom.Id.IsReadOnly,
                    isUniqueId: true);

                Models.RoomDataModel splitRoom = new(id: idProperty, otherProperties: properties);
                splitRoom.AddMatchingRevitRoom(revitRoom);
                splitRoom.UpdateReadProperties();

                _splitRooms.Add(splitRoom);
            }
        }

        /// <summary>
        /// Removes a split room from _splitRooms when its Revit family instance has been wiped.
        /// If the split room has no remaining MatchingRevitRooms after removal, the entry is deleted.
        /// </summary>
        public void RemovePlacedSplitRevitRoom(string splitRoomId, long revitElementId)
        {
            bool removeSplitRoom = false;
            RoomDataModel roomToRemove = null;

            foreach (var room in _splitRooms)
            {
                if (room.Id.Value == splitRoomId)
                {
                    room.MatchingRevitRooms.RemoveAll(x => x.RevitElementId == revitElementId);
                    room.UpdateReadProperties();

                    if (room.MatchingRevitRooms.Count == 0)
                    {
                        removeSplitRoom = true;
                        roomToRemove = room;
                    }
                    break;
                }
            }

            if (removeSplitRoom)
                _splitRooms.Remove(roomToRemove);
        }

        /// <summary>
        /// Adds a new split room to _splitRooms with ID-conflict checking.
        /// </summary>
        public void AddSplitRoom(Models.RoomDataModel room)
        {
            foreach (var existingRoom in _splitRooms)
            {
                if (existingRoom.ConflictsById(room))
                {
                    throw new Exceptions.RoomConflictException(existingRoom, room);
                }
            }
            _splitRooms.Add(room);
        }

        /// <summary>
        /// Returns all split rooms.
        /// </summary>
        public List<Models.RoomDataModel> GetAllSplitRooms()
        {
            return _splitRooms;
        }

        /// <summary>
        /// Returns the next available split counter for the given parent room ID.
        /// Scans _splitRooms for existing splits of the same parent and returns max + 1.
        /// </summary>
        public int GetNextSplitCounter(string parentRoomId)
        {
            // Always work from the base (non-split) ID so that selecting a split
            // room and splitting again still finds all siblings correctly.
            string baseParentId = Utilities.PushModeUtils.GetIdWithoutSplitModeIndicator(parentRoomId);

            int max = 0;
            foreach (var room in _splitRooms)
            {
                string baseId = Utilities.PushModeUtils.GetIdWithoutSplitModeIndicator(room.Id.Value);
                if (baseId == baseParentId)
                {
                    int counter = Utilities.PushModeUtils.GetSplitCounterFromId(room.Id.Value);
                    if (counter > max) max = counter;
                }
            }
            return max + 1;
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
            _splitRooms = [];
        }
    }
}
