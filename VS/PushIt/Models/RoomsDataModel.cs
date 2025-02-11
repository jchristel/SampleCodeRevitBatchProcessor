using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RoomsDataModel
    {
        public RoomDataProperty Id { get; set; }
        public RoomDataProperty AreaBriefed { get; set; }
        public RoomDataProperty AreaDesigned { get; set; }
        public RoomDataProperty NameShort { get; set; }
        public RoomDataProperty Department { get; set; }
        public RoomDataProperty SubDepartment { get; set; }

        public List<RoomsRevit> MatchingRevitRooms { get; set; }
        

        public RoomsDataModel()
        {
            // initialize the list of matching rooms
            MatchingRevitRooms = new List<RoomsRevit>();
        }

    }
}
