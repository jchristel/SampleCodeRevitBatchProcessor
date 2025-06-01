

from duHast.Utilities.Objects import base

class wall_storage(base.Base):
    """
    A class to represent a wall storage object in Revit.
    """
    
    def __init__(self, room_number, room_id, segment_length):
        super(wall_storage,self).__init__()

        self.room_number = room_number
        self.room_id = room_id
        self.segment_length = segment_length
       
