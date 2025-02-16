using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PushIt.Models;

namespace PushIt.Exceptions
{
    public class RoomConflictException:Exception
    {
        public RoomsDataModel ExistingRoom { get; }
        public RoomsDataModel IncomingRoom { get; }

        public RoomConflictException(RoomsDataModel existingRoom, RoomsDataModel incomingRoom)
        {
            ExistingRoom = existingRoom;
            IncomingRoom = incomingRoom;
        }

        public RoomConflictException(string message, RoomsDataModel existingRoom, RoomsDataModel incomingRoom) : base(message)
        {
            ExistingRoom = existingRoom;
            IncomingRoom = incomingRoom;
        }

        public RoomConflictException(string message, Exception innerException, RoomsDataModel existingRoom, RoomsDataModel incomingRoom) : base(message, innerException)
        {
            ExistingRoom = existingRoom;
            IncomingRoom = incomingRoom;
        }
    }
}
