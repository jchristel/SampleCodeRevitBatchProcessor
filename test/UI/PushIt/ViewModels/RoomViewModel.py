# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase


from PushIt.Models.Room import Room

class RoomViewModel(ViewModelBase):
    
    def __init__(self, room):
        super(RoomViewModel, self).__init__()
        
        
        if not (isinstance(room, Room)):
            raise ValueError("room needs to be of type Room, got {} instead.".format(type(room)))
        
        self._room = room
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
