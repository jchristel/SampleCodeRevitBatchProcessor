using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RoomsDataModel
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
        public bool Conflicts(RoomsDataModel other)
        {
            if (other == null) return false;
            else if (other.Id.Value != Id.Value) { return false; }
            else
            {
                return true;
            }
        }

        public RoomsDataModel()
        {
            // initialize the list of matching rooms
            _matchingRevitRooms = new List<RoomsRevit>();
        }
    }
}
