import sys

# setup duHast
DU_HAST_PATH = r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\Samples\WPF\RoomsInModel\Views\rooms_in_model.xaml"

# insert duHast dev version at the beginning of path in case a prod version is in path
sys.path.insert(0, DU_HAST_PATH)


# settings:

# test XAML path
XAML_PATH = r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\Samples\WPF\RoomsInModel\Views\rooms_in_model.xaml"


# imports

from duHast.Revit.UI.Objects.ExernalEventHandler import ExternalEventHandler

from Autodesk.Revit.UI import (
    ExternalEvent,
)

from Models.RevitModel import RevitModel
from Models.Room import Room
from Models.RoomId import RoomId

from ViewModels.RoomsListViewModel import RoomsListViewModel
from MyWindow import MyWindow



# main code

def execute_at_event_raised_sample_refresh_rooms(uiapp):
    
    # create a dummy list and return it
    test_list = [
        {"room_id": 1, "room_name": "Room 1", "room_number": "1", "phase": "Phase 1", "level": "Level 1"},
        {"room_id": 2, "room_name": "Room 2", "room_number": "2", "phase": "Phase 2", "level": "Level 2"},
    ]

    return test_list


def wpf_sample():

    # set up a model
    revit_model = RevitModel("Revit Model")

    # add some dummy rooms
    revit_model.add_room(Room(RoomId(1), "Room 1", "Level 1", "Phase 1", "test level 01"))
    revit_model.add_room(Room(RoomId(2), "Room 2", "Level 2", "Phase 2", "test level 01"))

    # set up an external event handler
    ex_event_handler_refresh_rooms = ExternalEventHandler(
        execute_at_event_raised=execute_at_event_raised_sample_refresh_rooms
    )

    # create and hook up the ExternalEvent
    ext_event = ExternalEvent.Create(ex_event_handler_refresh_rooms)

    # set up a view model
    # TODO: pass in rooms?
    view_model_test = RoomsListViewModel()

    # set up a window and show it modeless
    test = MyWindow(
        xaml_path=XAML_PATH,
        view_model=view_model_test,
        external_event=ext_event,
        external_event_handler=ex_event_handler_refresh_rooms,
    )
    test.Show()
