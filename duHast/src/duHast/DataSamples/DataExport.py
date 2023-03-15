'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions writing revit geometry data to file.
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

from duHast.Utilities import Utility as util
from duHast.APISamples import RevitCeilings as rCeil
from duHast.APISamples import RevitRooms as rRoom
from duHast.Utilities import Result as res

from duHast.DataSamples import DataCeiling as dc
from duHast.DataSamples import DataRoom as dr

import json
import codecs

# -------------------------------- write data to file -------------------------------------------------------

def get_data_from_model(doc):
    '''
    Gets element data from the model. This is currently limited to

    - rooms
    - ceilings

    :param doc: The current model document.
    :type doc: Autodeks.Revit.DB.Document

    :return: A dictionary in format {file name: str, date processed : str, room:[], ceiling:[]}
    :rtype: {}
    '''

    # get data
    allRoomData = rRoom.GetAllRoomData(doc)
    allCeilingData = rCeil.GetAllCeilingData(doc)

    data_json = {
        "file name": doc.Title,
        "date processed": util.GetDateStamp(util.FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC),
        dr.DataRoom.dataType: allRoomData,
        dc.DataCeiling.dataType: allCeilingData
    }

    return data_json


def write_json_to_file (json_data, dataOutPutFileName):
    '''
    Writes collected data to a new json formatted file.

    :param json_data: A dictionary to be written to file.
    :type json_data: json object (dictionary)
    :param dataOutPutFileName: Fully qualified file path to json data file.
    :type dataOutPutFileName: str

    :return: 
        Result class instance.
        
        - result.status. True if json data file was written successfully, otherwise False.
        - result.message will confirm path of json data file.
        - result.result empty list

        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    result = res.Result()
   

    try:
        json_object = json.dumps(json_data, indent = None, default=lambda o: o.__dict__)
        with codecs.open(dataOutPutFileName, 'w', encoding='utf-8') as f:
            f.write(json_object)
            f.close()

        result.UpdateSep(True, 'Data written to file: ' + dataOutPutFileName)
    except  Exception as e:
        result.UpdateSep(False, 'Failed to write data to file with exception: ' + str(e))
    return result