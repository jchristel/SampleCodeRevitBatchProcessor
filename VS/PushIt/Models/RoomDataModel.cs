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
        private List<RoomsRevit> _matchingRevitRooms;

        public RoomDataProperty Id { get; set; }
        public RoomDataProperty AreaBriefed { get; set; }
        public RoomDataProperty AreaDesigned { get; set; }
        public RoomDataProperty NameShort { get; set; }
        public RoomDataProperty Department { get; set; }
        public RoomDataProperty SubDepartment { get; set; }

        public List<RoomsRevit> MatchingRevitRooms { get => _matchingRevitRooms; set => _matchingRevitRooms = value; }

        public void ClearMatchingRevitRooms()
        {
            _matchingRevitRooms.Clear();
        }

        public void AddMatchingRevitRoom(RoomsRevit revitRoom)
        {
            _matchingRevitRooms.Add(revitRoom);
        }

        public void UpdateAreaDesigned(string areaDesigned)
        {
            AreaDesigned = new RoomDataProperty("Area Designed", "", "", areaDesigned);
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
    }
}
