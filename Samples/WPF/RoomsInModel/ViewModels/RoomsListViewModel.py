from duHast.UI.Objects.ViewModelBase import ViewModelBase
from duHast.UI.Objects.Command import Command
from ViewModels.RoomViewModel import RoomViewModel
from Models.Room import Room
from Models.RoomId import RoomId
from System.Collection.ObjectModel import ObservableCollection


class RoomsListViewModel(ViewModelBase):

    def __init__(self):
        """
        A view model for the rooms list view.

        """
        super(RoomsListViewModel, self).__init__()

        # set up commands of view model
        self.RefreshRoomsCommand = Command(self.refresh_rooms)
        self.CancelCommand = Command(self.cancel)

        # set up list of rooms
        self.rooms = ObservableCollection[RoomViewModel]()

        # add a few dummy rooms
        self.rooms.Add(
            RoomViewModel(
                room=Room(
                    room_id=RoomId(room_id_integer=1),
                    room_name="Room 1",
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
                    room_name="Room 2",
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
                    room_name="Room 3",
                    room_number="3",
                    phase="Phase 1",
                    level="Level 1",
                )
            )
        )

    @property
    def get_rooms(self):
        """
        Gets the rooms.

        :return: The rooms
        :rtype: ObservableCollection[RoomViewModel]
        """
        return self.rooms

    def refresh_rooms(self):
        pass

    def cancel(self):
        pass
