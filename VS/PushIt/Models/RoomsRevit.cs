using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RoomsRevit
    {
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
                          int revitElementId)
        {
            _id = id;
            _areaBriefed = areaBriefed;
            _areaDesigned = areaDesigned;
            _roomNameShort = roomNameShort;
            _department = department;
            _subDepartment = subDepartment;
            _revitElementId = revitElementId;
        }
    }
}
