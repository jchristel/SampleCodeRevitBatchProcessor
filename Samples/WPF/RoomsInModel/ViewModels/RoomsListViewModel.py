import clr

clr.AddReference("System.Core")

from duHast.UI.Objects.ViewModelBase import ViewModelBase
from duHast.UI.Objects.CommandBase import CommandBase
from WPF.RoomsInModel.ViewModels.RoomViewModel import RoomViewModel
#from ViewModels.RoomViewModel import RoomViewModel
from WPF.RoomsInModel.Models.Room import Room
from WPF.RoomsInModel.Models.RoomId import RoomId
from WPF.RoomsInModel.Commands.RefreshRoomsInRevitModel import RefreshRoomsInRevitModelCommand

# from System.Collections.ObjectModel import ObservableCollection
from System.Collections.Specialized import (
    NotifyCollectionChangedEventArgs,
    NotifyCollectionChangedAction,
)


class RoomsListViewModel(ViewModelBase):

    def __init__(self, ext_event_refresh_rooms, action_refresh_room):
        """
        A view model for the rooms list view.

        :param ext_event_refresh_rooms: A Revit API external event which will be raised when the update rooms button is pressed
        :param action_refresh_room: a class containing the function the external event update rooms will call.
        """
        super(RoomsListViewModel, self).__init__()

        # store the event handler to refresh the rooms
        self.ext_event_refresh_rooms = ext_event_refresh_rooms
        # store the class containing the action the external event handler refresh rooms will execute
        # TODO: register observable collection watcher!
        self.action_refresh_room = action_refresh_room

        # set up commands of view model
        self.RefreshRoomsCommand = RefreshRoomsInRevitModelCommand(self.refresh_rooms)
        self.CancelCommand = CommandBase(self.cancel)

        # hook up list of rooms to action class property
        self.rooms = self.action_refresh_room.rooms
        # self.rooms = ObservableCollection[RoomViewModel]()

        # Subscribe to the CollectionChanged event
        self.rooms.CollectionChanged += self.on_rooms_collection_changed

        # add a few dummy rooms (debug only)
        self.add_dummy_rooms()

    @property
    def get_rooms(self):
        """
        Gets the rooms.

        :return: The rooms
        :rtype: ObservableCollection[RoomViewModel]
        """
        return self.rooms

    def refresh_rooms(self):
        # raise the external event through the Revit API
        # which will in turn trigger an update of the rooms retrieved from the Revit model
        self.ext_event_refresh_rooms.Raise()

    def cancel(self):
        pass

    def on_rooms_collection_changed(self, sender, e):
        """
        These functions are useful if th UI is meant to do any additional checking of the
        new room data...noty required if all I'm doing is displaying it

        Args:
            sender (_type_): _description_
            e (NotifyCollectionChangedEventArgs): _description_
        """
        # Handle the change in the collection here
        if e.Action == NotifyCollectionChangedAction.Add:
            # Items were added
            pass

        elif e.Action == NotifyCollectionChangedAction.Remove:
            # Items were removed
            pass

        elif e.Action == NotifyCollectionChangedAction.Replace:
            # Items were replaced
            pass

        elif e.Action == NotifyCollectionChangedAction.Reset:
            # The entire collection was cleared
            # print("Rooms collection cleared.")
            pass

    def add_dummy_rooms(self):
        self.rooms.Add(RoomViewModel(Room(RoomId(1), "Room 1", "1", "Phase 1", "Level 1")))
        self.rooms.Add(RoomViewModel(Room(RoomId(2), "Room 2", "2", "Phase 1", "Level 1")))
        self.rooms.Add(RoomViewModel(Room(RoomId(3), "Room 3", "3", "Phase 1", "Level 1")))
