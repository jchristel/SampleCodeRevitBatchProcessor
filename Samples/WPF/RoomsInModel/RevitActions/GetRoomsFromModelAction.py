from duHast.Utilities.Objects import base
from duHast.Revit.Rooms.rooms import get_all_placed_rooms
from duHast.Revit.Rooms.room_common_parameters import get_room_name, get_room_number, get_room_phase, get_room_level
from System.Collections.ObjectModel import ObservableCollection

from WPF.RoomsInModel.ViewModels.RoomViewModel import RoomViewModel
from WPF.RoomsInModel.Models.Room import Room
from WPF.RoomsInModel.Models.RoomId import RoomId


class GetRoomsFromModelAction(base.Base):
    
    
    def __init__(self):
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
        
        # current document
        doc=uiapp.ActiveUIDocument.Document

        # get the rooms from the revit model and display them
        all_placed_rooms = get_all_placed_rooms(doc=doc)

        # print("Found rooms: {}".format(len(all_placed_rooms)))
        try:
            for placed_room in all_placed_rooms:
                # add a few dummy rooms
                self.rooms.Add(
                    RoomViewModel(
                        room=Room(
                            room_id=RoomId(room_id_integer=placed_room.Id.IntegerValue),
                            room_name=get_room_name(room=placed_room),
                            room_number=get_room_number(room=placed_room),
                            phase=get_room_phase(rvt_doc=doc, room=placed_room),
                            level=get_room_level(rvt_doc=doc, room=placed_room),
                        )
                    )
                )
        except Exception as e:
            print("Exception occured when adding room: {}".format(e))
