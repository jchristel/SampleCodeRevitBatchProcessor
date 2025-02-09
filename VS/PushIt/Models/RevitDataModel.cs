using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RevitDataModel
    {

        public List<Models.RoomsDataModel> rooms;

        public RevitDataModel()
        {
            rooms = new List<Models.RoomsDataModel>();
        }

        public void AddRoom(Models.RoomsDataModel room)
        {
            rooms.Add(room);
        }

        public List<Models.RoomsDataModel> GetAllRooms()
        {
            return rooms;
        }

    }
}
