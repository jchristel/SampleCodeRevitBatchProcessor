from Models.Room import Room
from duHast.UI.Objects.ViewModelBase import ViewModelBase


class RoomViewModel(ViewModelBase):
    """
    A view model for the rooms.
    """

    def __init__(self, room):
        super(RoomViewModel, self).__init__()

        if not isinstance(room, Room):
            raise TypeError("room must be of type Room")

        # store the room
        self.room = room

        # store the room properties
        self.room_id = str(room.room_id.room_id_integer)
        self.room_name = room.room_name
        self.room_number = room.room_number
        self.phase = room.phase
        self.level = room.level
