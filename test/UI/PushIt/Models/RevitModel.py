from duHast.Utilities.Objects.base import Base

from test.UI.PushIt.Models.Room import Room
from test.UI.PushIt.Models.RoomsContainer import RoomsContainer
from Objects.Settings import Settings

class RevitModel(Base):
    
    def __init__(self):
        
        super(RevitModel, self).__init__()
        
        self._rooms_container = RoomsContainer()
        self._settings = Settings()
    
    @property
    def settings(self):
        return self._settings
    
    @settings.setter
    def settings(self, value):
        if not(isinstance (value,Settings)):
            raise ValueError("Value must be of type Setting, got {} instead.".format(type(value)))
        self._settings = value
    
    def get_all_rooms(self):
        return self._rooms_container.get_all_rooms()
    

    def add_room(self, room_model):
        # check type
        if(isinstance(room_model,Room)==False):
            raise TypeError ("room_model needs to be of type Room, got {} instead".format(type(room_model)))
        
        # add the room to the container and check for conflicts
        self._rooms_container.add_room(room_model)


    def push_data(self, families):
        for fam in families:
            # check type
            if(isinstance(fam,Room)==False):
                raise TypeError ("family needs to be of type Room, got {} instead".format(type( fam)))
        
            # reload ...