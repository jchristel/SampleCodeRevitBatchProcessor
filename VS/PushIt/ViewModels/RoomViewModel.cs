using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.ViewModels
{
    public class RoomViewModel
    {
        public Models.RoomsDataModel _room;
        public string Id => _room.Id.Value;

        public string AreaBriefed => _room.AreaBriefed.Value;
        public string AreaDesigned => _room.AreaDesigned.Value;
        public string NameShort => _room.NameShort.Value;
        public string Department => _room.Department.Value;
        public string SubDepartment => _room.SubDepartment.Value;

        public string Count => _room.MatchingRevitRooms.Count.ToString();

        public RoomViewModel(Models.RoomsDataModel room)
        {
            _room = room;
        }
    }
}
