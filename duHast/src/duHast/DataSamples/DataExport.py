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
# Copyright (c) 2022  Jan Christel
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

from duHast.APISamples import Utility as util
from duHast.APISamples import RevitCeilings as rCeil
from duHast.APISamples import RevitRooms as rRoom
from duHast.APISamples import Result as res


# dataIn         
def ConvertDataToListJson(dataIn):
    '''
    Converts lists of data classes into a single list of list of Json string representing the data class

    :param dataIn: list of data class instances
    :type dataIn: [data class]

    :return: list of list of Json string
    :rtype: [[str]]
    '''

    dataJsonAll = []
    for dataList in dataIn:
        for d in dataList:
            dataRow = []
            dataRow.append(d.to_json())
            dataJsonAll.append(dataRow)
    return dataJsonAll

# -------------------------------- write data to file -------------------------------------------------------

def WriteJsonDataToFile (doc, dataOutPutFileName):
    '''
    Collects geometry data and writes it to a new json formatted file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
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
    # get data
    allRoomData = rRoom.GetAllRoomData(doc)
    allCeilingData = rCeil.GetAllCeilingData(doc)
    # convert data to json string
    data = ConvertDataToListJson(
        [
            allRoomData, 
            allCeilingData
        ])
    try:
        util.writeReportData(dataOutPutFileName, [], data)
        result.UpdateSep(True, 'Data written to file: ' + dataOutPutFileName)
    except  Exception as e:
        result.UpdateSep(False, 'Failed to write data to file with exception: ' + str(e))
    return result