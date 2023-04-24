'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test functions for data objects.
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

import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.Data import process_ceilings_to_rooms as magic
from duHast.Data.Utils import data_import as dReader
from duHast.Data.Utils import data_to_file as dFile

from duHast.Data.Objects import data_ceiling as dc
from duHast.Data.Objects import data_room as dr

#: input file path for data exported from model previously
DATA_IN = r"C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\jsonFromModel.json"
#: output file path for data read from file to be written back to file
DATA_OUT = r"C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\jsonFromFile.json"
#: output file path for intersection ceilings to rooms report
REPORT_OUT = r'C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\ceilingsByRoom.csv'
#: model sample name
MODEL_FILE_PATH = r'C:\temp\test.rvt'


# test one: read and write data back to disc
def read_and_write():
    '''
    Read data from file, convert to json and write back to file.
    Input and output file should be identical!
    '''

    # read json file and convert into data objects
    dataReader = dReader.ReadDataFromFile(DATA_IN)
    dataReader.load_data()

    # get objects by type
    allRoomData = dataReader.get_data_by_type(dr.DataRoom.data_type)
    allCeilingData = dataReader.get_data_by_type(dc.DataCeiling.data_type)

    dic = {
        dr.DataRoom.data_type: allRoomData,
        dc.DataCeiling.data_type: allCeilingData,
    }

    dic = dFile.build_json_for_file(dic, MODEL_FILE_PATH)
    # write json objects back to file
    write_result = dFile.write_json_to_file(dic, DATA_OUT)
    
    print(write_result)

def ceilings_by_room():
    '''
    Reads exported rooms  and ceilings data from a file and does an intersection check.
    The result of that check will be written to file.

    Data on file is stored at: DATA_IN
    Intersection results are written to: REPORT_OUT
    '''

    print('Getting data from {}'.format(DATA_IN))
    ceilings_by_room = magic.get_ceilings_by_room(DATA_IN)
    print(ceilings_by_room.message)
    print('writing data to file')
    data_to_file = magic.write_data_to_file(
        ceilings_by_room.result, 
        REPORT_OUT, room_instance_property_keys= ['Number', 'Name'], 
        ceiling_type_property_keys = ['Type Mark'], 
        ceiling_instance_property_keys =['Height Offset From Level'] )

    print(data_to_file.message)

if __name__ == "__main__":
    read_and_write()
    ceilings_by_room()

