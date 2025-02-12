using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RoomsRevit
    {
        public string Id { get; set; }
        public string AreaBriefed { get; set; }
        public string AreaDesigned { get; set; }
        public string RoomNameShort { get; set; }
        public string Department { get; set; }
        public string SubDepartment { get; set; }

        public RoomsRevit() { }

        public RoomsRevit(string id, string areaBriefed, string areaDesigned, string roomNameShort, string department, string subDepartment)
        {
            Id = id;
            AreaBriefed = areaBriefed;
            AreaDesigned = areaDesigned;
            RoomNameShort = roomNameShort;
            Department = department;
            SubDepartment = subDepartment;
        }
    }
}
