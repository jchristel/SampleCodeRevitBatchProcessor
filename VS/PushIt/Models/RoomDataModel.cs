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

namespace duHast.PushIt.Models
{
    public class RoomDataModel
    {
        /// <summary>
        /// List of matching rooms
        /// </summary>
        private List<RoomsRevit> _matchingRevitRooms;

        /// <summary>
        /// Room ID, must be unique
        /// </summary>
        public RoomDataProperty Id { get; set; }

        /// <summary>
        /// Any other data model properties
        /// </summary>
        List<RoomDataProperty> _properties = new List<RoomDataProperty>();

        public List<RoomsRevit> MatchingRevitRooms { get => _matchingRevitRooms; set => _matchingRevitRooms = value; }

        public void ClearMatchingRevitRooms()
        {
            _matchingRevitRooms.Clear();
        }

        public void AddMatchingRevitRoom(RoomsRevit revitRoom)
        {
            _matchingRevitRooms.Add(revitRoom);
        }

        /// <summary>
        /// Update a read property
        /// </summary>
        /// <param name="propertyName"></param>
        /// <param name="value"></param>
        public void UpdateReadProperty(string propertyName, string value)
        {
            foreach (var property in _properties)
            {
                if (property.Name == propertyName && property.IsReadOnly)
                {
                    property.Value = value;
                    break;
                }
            }
        }

        /// <summary>
        /// Check if room conflicts by id value
        /// </summary>
        /// <param name="other"></param>
        /// <returns></returns>
        public bool Conflicts(RoomDataModel other)
        {
            if (other == null) return false;
            else if (other.Id.Value != Id.Value) { return false; }
            else
            {
                return true;
            }
        }

        public RoomDataModel()
        {
            // initialize the list of matching rooms
            _matchingRevitRooms = new List<RoomsRevit>();
        }

        public RoomDataModel(RoomDataProperty id, List<RoomDataProperty> otherProperties)
        {
            // set the id and other properties
            Id = id;
            _properties = otherProperties;

            // initialize the list of matching rooms
            _matchingRevitRooms = new List<RoomsRevit>();
        }
    }
}
