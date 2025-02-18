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

namespace PushIt.ViewModels
{
    public class RoomViewModel
    {
        public Models.RoomDataModel _room;
        public string Id => _room.Id.Value;

        public string AreaBriefed => _room.AreaBriefed.Value;
        public string AreaDesigned => _room.AreaDesigned.Value;
        public string NameShort => _room.NameShort.Value;
        public string Department => _room.Department.Value;
        public string SubDepartment => _room.SubDepartment.Value;

        public string Count => _room.MatchingRevitRooms.Count.ToString();

        public RoomViewModel(Models.RoomDataModel room)
        {
            _room = room;
        }
    }
}
