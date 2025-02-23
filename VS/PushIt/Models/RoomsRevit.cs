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

namespace duHast.PushIt.Models
{
    public class RoomsRevit
    {
        string _id;
        string _areaBriefed;
        string _areaDesigned;
        string _roomNameShort;
        string _department;
        string _subDepartment;
        string _designSet;
        string _designOption;
        bool _designOptionIsPrimary;
        int _revitElementId;

        public string Id { get => _id; set => _id = value; }
        public string AreaBriefed { get => _areaBriefed; set => _areaBriefed = value; }
        public string AreaDesigned { get => _areaDesigned; set => _areaDesigned = value; }
        public string RoomNameShort { get => _roomNameShort; set => _roomNameShort = value; }
        public string Department { get => _department; set => _department = value; }
        public string SubDepartment { get => _subDepartment; set => _subDepartment = value; }
        public string DesignSet { get => _designSet; set => _designSet = value; }
        public string DesignOption { get => _designOption; set => _designOption = value; }
        public bool DesignOptionIsPrimary { get => _designOptionIsPrimary; set => _designOptionIsPrimary = value; }
        public int RevitElementId { get => _revitElementId; set => _revitElementId = value; }

        public RoomsRevit() { }

        public RoomsRevit(string id,
                          string areaBriefed,
                          string areaDesigned,
                          string roomNameShort,
                          string department,
                          string subDepartment,
                          string designSet,
                            string designOption,
                            bool designOptionIsPrimary,
                          int revitElementId)
        {
            _id = id;
            _areaBriefed = areaBriefed;
            _areaDesigned = areaDesigned;
            _roomNameShort = roomNameShort;
            _department = department;
            _subDepartment = subDepartment;
            _designSet = designSet;
            _designOption = designOption;
            _designOptionIsPrimary = designOptionIsPrimary;
            _revitElementId = revitElementId;
        }
    }
}
