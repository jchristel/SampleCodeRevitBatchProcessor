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
        public string Id => _room.Id;

        public string AreaBriefed => _room.AreaBriefed.ToString();
        public string AreaDesigned => _room.AreaDesigned.ToString();
        public string NameShort => _room.NameShort;
        public string Department => _room.Department;
        public string SubDepartment => _room.SubDepartment;

        public string Count => _room.MatchingRevitRooms.Count.ToString();

        public RoomViewModel(Models.RoomsDataModel room)
        {
            _room = room;
        }
    }
}
