from duHast.Utilities.Objects import base
from System.Collections.ObjectModel import ObservableCollection

from ViewModels.RoomViewModel import RoomViewModel
from Models.Room import Room
from Models.RoomId import RoomId


class GetRoomsFromModelAction(base.Base):
    
    
    def __init__(self, ):
        """
        A class which contains the function to be executed when Revit raises an external event.
        
        Function executed will update an IObservable collection
        
        """
        super(GetRoomsFromModelAction, self).__init__()
        
        # set up list of rooms
        self.rooms = ObservableCollection[RoomViewModel]()
        
        
    def execute_at_event_raised_sample_refresh_rooms(self, uiapp):
        
        # clear the current list
        self.rooms.Clear()
        
        # add a few dummy rooms
        self.rooms.Add(
            RoomViewModel(
                room=Room(
                    room_id=RoomId(room_id_integer=1),
                    room_name="Room 10",
                    room_number="1",
                    phase="Phase 1",
                    level="Level 1",
                )
            )
        )

        self.rooms.Add(
            RoomViewModel(
                room=Room(
                    room_id=RoomId(room_id_integer=2),
                    room_name="Room 20",
                    room_number="2",
                    phase="Phase 1",
                    level="Level 1",
                )
            )
        )

        self.rooms.Add(
            RoomViewModel(
                room=Room(
                    room_id=RoomId(room_id_integer=3),
                    room_name="Room 30",
                    room_number="3",
                    phase="Phase 1",
                    level="Level 1",
                )
            )
        )
