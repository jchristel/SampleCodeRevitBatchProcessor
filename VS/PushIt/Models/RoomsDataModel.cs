using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RoomsDataModel
    {
        public string Id { get; set; }
        public double AreaBriefed { get; set; }
        public double AreaDesigned { get; set; }
        public string NameShort { get; set; }
        public string Department { get; set; }
        public string SubDepartment { get; set; }

        public List<RoomsRevit> MatchingRevitRooms { get; set; }
        public RoomsDataModel(string id, double areaBriefed, double areaDesigned, string nameShort, string department, string subDepartment)
        {
            Id = id;
            AreaBriefed = areaBriefed;
            AreaDesigned = areaDesigned;
            NameShort = nameShort;
            Department = department;
            SubDepartment = subDepartment;

            // initialize the list of matching rooms
            MatchingRevitRooms = new List<RoomsRevit>();
        }

        public RoomsDataModel()
        {
            // initialize the list of matching rooms
            MatchingRevitRooms = new List<RoomsRevit>();
        }

    }
}
