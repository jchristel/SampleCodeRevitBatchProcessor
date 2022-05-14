#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import Result as res
import RevitRooms as rRoom

# import Autodesk
import Autodesk.Revit.DB as rdb

class RevitWarningsSolverRoomTagToRoom:

    def __init__(self):
        '''empty constructor this solver does not take any further arguments'''
        self.filterName = 'Room tag outside of room.'
        pass

    # --------------------------- room tag not in room ---------------------------
    GUID = '4f0bba25-e17f-480a-a763-d97d184be18a'
    
    # doc       current drevit document
    # warnings  list of warnings
    def SolveWarnings(self, doc, warnings):
        '''solver moving room tags to room location point'''
        returnvalue = res.Result()
        if(len(warnings) > 0 ):
            for warning in warnings:
                elementIds = warning.GetFailingElements()
                for elid in elementIds:
                    result = rRoom.MoveTagToRoom(doc, elid)
                    returnvalue.Update(result)
        else:
            returnvalue.UpdateSep(True,'No warnings of type: room tag outside of room in model.')
        return  returnvalue 
    
