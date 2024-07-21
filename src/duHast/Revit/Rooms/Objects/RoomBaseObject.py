from duHast.Revit.Rooms.room_common_parameters import (
    get_room_num_name_comb,
    get_room_name,
    get_room_number,
    get_room_phase,
)
from duHast.Utilities.Objects.base import Base


class RoomBaseObj(Base):
    def __init__(self, rvt_doc, room, *args, **kwargs):
        super(RoomBaseObj, self).__init__(*args, **kwargs)
        self.room = room
        self.number = get_room_number(room)
        self.name = get_room_name(room)
        self.number_name_comb = get_room_num_name_comb(room)
        self.level = room.Level
        self.phase = get_room_phase(rvt_doc, room)
