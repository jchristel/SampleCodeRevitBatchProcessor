from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase


from PushIt.Objects.match_status_names import MatchStatusNames
from PushIt.Models.Room import Room

class RoomViewModel(ViewModelBase):
    
    def __init__(self, room):
        super(RoomViewModel, self).__init__()
        
        
        if not (isinstance(room, Room)):
            raise ValueError("room needs to be of type Room, got {} instead.".format(type(room)))
        
        self._room = room

        self._match_status = MatchStatusNames.NO_MATCH.value
        self._is_selected = False


    @property
    def IsSelected(self):
        return self._is_selected
    
    @IsSelected.setter
    def IsSelected(self, value):
        self._is_selected = value

    @property
    def RoomId(self):
        return self._room.id.id

    @property
    def AreaBriefed(self):
        return self._room.area_briefed.value

    @property
    def AreaDesigned(self):
        return self._room.area_designed.value
    
    @property
    def MatchStatus(self):
        return self._match_status
    
    @MatchStatus.setter
    def MatchStatus(self, value):
        self._match_status = value
