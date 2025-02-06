from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase


from PushIt_v2.Models.Room import Room
class RoomViewModel(ViewModelBase):
    
    def __init__(self, room):
        super(RoomViewModel, self).__init__()
        
        
        if not (isinstance(room, Room)):
            raise ValueError("room needs to be of type Room, got {} instead.".format(type(room)))
        
        self._room = room

    @property
    def RoomId(self):
        try:
            return self._room.id.id
        except Exception as e:
            return "{error}".format(error=e)
    
    @property
    def RoomNameShort(self):
        try:
            return self._room.room_name_short.value
        except Exception as e:
            return "{error}".format(error=e)

    @property
    def AreaBriefed(self):
        try:
            return self._room.area_briefed.value
        except Exception as e:
            return "{error}".format(error=e)
    
    @property
    def AreaDesigned(self):
        try:
            return self._room.area_designed.value
        except Exception as e:
            return "{error}".format(error=e)
    
    @AreaDesigned.setter
    def AreaDesigned(self, value):
        try:
            self._room.area_designed.value = value
        except Exception as e:
            print("{error} in room view model are designed setter".format(error=e))

    @property
    def Department(self):
        try:
            return self._room.department.value
        except Exception as e:
                return "{error}".format(error=e)
    
    @property
    def SubDepartment(self):
        try:
            return self._room.sub_department.value
        except Exception as e:
            return "{error}".format(error=e)
    
    @property
    def PlacedRoomCount(self):
        try:
            matching_fams = self._room.get_revit_matches()
            if matching_fams:
                return len(matching_fams)
            else:
                return 0
        except Exception as e:
            return "{error}".format(error=e)