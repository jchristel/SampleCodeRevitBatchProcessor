
from PushIt.Models.Room import Room
from PushIt.Exceptions.RoomConflictException import RoomsConflictException

from duHast.Utilities.Objects.base import Base

class RoomsContainer (Base):
    
    def __init__(self):
        
        super(RoomsContainer, self).__init__()
        
        # ini list
        self._rooms = []
    
    
    def get_all_rooms(self):
        
        return self._rooms
    
    
    def add_room(self, room_instance):
    
        # type checking
        if(isinstance(room_instance,Room)==False):
            raise TypeError ("room_instance needs to be of type Room, got {} instead".format(type(room_instance)))
        
        # check if any reservations conflicts with the new one
        for existing_room in self._rooms:
            if(existing_room.Conflicts(room_instance)):
                raise RoomsConflictException(
                    message="New room conflicts existing room",
                    existing_room=existing_room, 
                    new_room=room_instance
                )
        
        self._rooms.append(room_instance)