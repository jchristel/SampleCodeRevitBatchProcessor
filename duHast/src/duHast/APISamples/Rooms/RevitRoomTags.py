'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit rooms tags. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Common import RevitTransaction as rTran
from duHast.Utilities import Result as res


def MoveTagToRoom(doc, tagId):
    '''
    Moves a room tag to the associated rooms location point.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tagId: The element id of the tag to be moved to the room.
    :type tagId: Autodesk.Revit.DB.ElementId
    :return: 
        Result class instance.
        - Tag moving status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name and number of the room.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain the name and number of the room and the exception message.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    rt = doc.GetElement(tagId)
    roomTagPoint = rt.Location.Point
    roomLocationPoint = rt.Room.Location.Point
    roomData = str(rt.Room.Number) + ' ' + str(rdb.Element.Name.GetValue(rt.Room))
    translation =  roomLocationPoint - roomTagPoint
    def action():
        actionReturnValue = res.Result()
        try:
            rt.Location.Move(translation)
            actionReturnValue.message = 'Moved tag to room ' + roomData
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed to move tag to room ' + roomData + ' with exception: ' + str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc, 'Moving room tag to room : ' + roomData)
    returnValue.Update(rTran.in_transaction(transaction, action))
    return returnValue