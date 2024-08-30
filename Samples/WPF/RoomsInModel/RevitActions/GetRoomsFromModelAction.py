from duHast.Utilities.Objects import base
from duHast.Revit.Rooms.rooms import get_all_placed_rooms
from duHast.Revit.Rooms.room_common_parameters import get_room_name, get_room_number, get_room_phase, get_room_level
from System.Collections.ObjectModel import ObservableCollection

from WPF.RoomsInModel.ViewModels.RoomViewModel import RoomViewModel
from WPF.RoomsInModel.Models.Room import Room
from WPF.RoomsInModel.Models.RoomId import RoomId

from Autodesk.Revit.DB import ElementId
class GetRoomsFromModelAction(base.Base):
    
    
    def __init__(self):
        """
        A class which contains the function to be executed when Revit raises an external event.
        
        Function executed will update an IObservable collection
        
        """
        super(GetRoomsFromModelAction, self).__init__()
        
        # set up list of rooms
        self.rooms = ObservableCollection[RoomViewModel]()
        

    def get_rooms_from_model(self, doc):
        """
        Returns the rooms from the model depending on the active view.

        If the view is not a plan view all rooms will be returned. Otherwise just rooms placed on the same level
        as the active plan view.

        """
        # set up a rooms container
        all_placed_rooms = get_all_placed_rooms(doc=doc)

        view_level_id = ElementId.InvalidElementId
        try:
            view_level_id = doc.ActiveView.GenLevel.Id
        except Exception:
            pass

        # depending on whether this is a plan view or not get the rooms
        if(view_level_id != ElementId.InvalidElementId):
            filtered_rooms_by_level = []
            # get the rooms on the current level only
            for room_placed in all_placed_rooms:
                if(room_placed.LevelId == view_level_id):
                    filtered_rooms_by_level.append(room_placed)

            # reset rooms placed collection to the filtered one
            all_placed_rooms = filtered_rooms_by_level
        
        return all_placed_rooms


    def execute_at_event_raised_sample_refresh_rooms(self, uiapp):
        """
        This function gets called from Revit when an external event is raised by pressing the refresh button in the UI

        It will populate the UI with rooms from the model depending on the active view.

        """
        # clear the current list
        self.rooms.Clear()
        
        # current document
        doc=uiapp.ActiveUIDocument.Document

        # set up a rooms container
        all_placed_rooms = self.get_rooms_from_model(doc=doc)

        # convert room objects to fit WPF view model
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
