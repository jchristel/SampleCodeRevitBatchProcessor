from duHast.Utilities.Objects import base

class room_storage(base.Base):
    """
    A class to represent a wall storage object in Revit.
    """
    
    def __init__(self, room_number, room_id):
        super(room_storage,self).__init__()

        self.room_number = room_number
        self.room_id = room_id
       
        # store wall id and length of curve from wall (int) : (float)
        # each wall id should only appear once
        self.wall_id_and_length = {}
