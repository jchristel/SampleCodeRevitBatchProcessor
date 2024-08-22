
from Models.RevitModel import RevitModel
from Models.Room import Room
from Models.RoomId import RoomId


def main():
    

    revit_model = RevitModel("Revit Model")

    # add some dummy rooms
    revit_model.add_room(
        Room(
            RoomId(1),
            "Room 1",
            "Level 1",
            "Phase 1"
        )
    )

    revit_model.add_room(
        Room(
            RoomId(2),
            "Room 2",
            "Level 2",
            "Phase 2"
        )
    )