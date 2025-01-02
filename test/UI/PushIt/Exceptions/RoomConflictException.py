# Define a custom exception by subclassing Exception
from PushIt.Models.Room import Room

class RoomsConflictException(Exception):
    def __init__(self, message, existing_room, new_room):
        
        if(isinstance(existing_room, Room)==False):
            raise TypeError ("existing_room need to be of type Room. Got {} instead.".format(type(existing_room)))
        self.existing_room = existing_room
        
        if(isinstance(new_room, Room)==False):
            raise TypeError ("new_room need to be of type Room. Got {} instead.".format(type(new_room)))
        self.new_room = new_room
        
        # Call the base class constructor with the message
        super(RoomsConflictException, self).__init__(message, existing_room, new_room)
        

    def __str__(self):
        # Custom string representation of the exception
        return "RoomsConflictException: {}".format(self.args[0])