'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Room tag not in room warnings solver class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
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

from duHast.Utilities import Result as res
from duHast.APISamples import RevitRooms as rRoom

# import Autodesk
import Autodesk.Revit.DB as rdb
from duHast.Utilities import Base

class RevitWarningsSolverRoomTagToRoom(Base.Base):

    def __init__(self):
        '''
        Empty constructor this solver does not take any further arguments.
        '''

        # ini super class to allow multi inheritance in children!
        super(RevitWarningsSolverRoomTagToRoom, self).__init__() 
        self.filterName = 'Room tag outside of room.'

    # --------------------------- room tag not in room ---------------------------
    #: guid identifying this specific warning
    GUID = '4f0bba25-e17f-480a-a763-d97d184be18a'
    
    def solve_warnings(self, doc, warnings):
        '''
        Solver moving room tags to room location point.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param warnings: List of warnings to be solved.
        :type warnings: Autodesk.Revit.DB.FailureMessage

        :return: 
            Result class instance.
            
            - .result = True if all room tags within warnings could be moved to room location point. Otherwise False.
            - .message will be 'moved tag to room xyz'
        
        :rtype: :class:`.Result`
        '''

        return_value = res.Result()
        if(len(warnings) > 0 ):
            for warning in warnings:
                element_ids = warning.GetFailingElements()
                for el_id in element_ids:
                    result = rRoom.MoveTagToRoom(doc, el_id)
                    return_value.update(result)
        else:
            return_value.update_sep(True,'No warnings of type: room tag outside of room in model.')
        return  return_value 
    
