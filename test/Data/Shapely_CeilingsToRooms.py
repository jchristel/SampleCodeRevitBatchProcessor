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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.Data import process_ceilings_to_rooms as magic
from duHast.Data.Utils import data_import as dReader
from duHast.Data.Utils.data_to_file import build_json_for_file
from duHast.Utilities.files_json import write_json_to_file

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

    dic = build_json_for_file(dic, MODEL_FILE_PATH)
    # write json objects back to file
    write_result = write_json_to_file(dic, DATA_OUT)
    
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

