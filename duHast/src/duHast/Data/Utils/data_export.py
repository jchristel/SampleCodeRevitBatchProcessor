'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions exporting revit geometry to data objects.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Ceilings.Export import to_data_ceiling as rCeil
from duHast.Revit.Rooms.Export import to_data_room as rRoom

from duHast.Data.Objects import data_ceiling as dc
from duHast.Data.Objects import data_room as dr


# -------------------------------- write data to file -------------------------------------------------------

def get_data_from_model(doc):
    '''
    Gets element data from the model. This is currently limited to

    - rooms
    - ceilings

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary in format {file name: str, date processed : str, room:[], ceiling:[]}
    :rtype: {}
    '''

    # get data
    allRoomData = rRoom.get_all_room_data(doc)
    allCeilingData = rCeil.get_all_ceiling_data(doc)

    dic = {
        dr.DataRoom.data_type: allRoomData,
        dc.DataCeiling.data_type: allCeilingData,
    }

    return dic