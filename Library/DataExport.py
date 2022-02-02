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

import Utility as util
import RevitCeilings as rCeil
import RevitRooms as rRoom
import Result as res


# dataIn         list of data class instances
def ConvertDataToListJson(dataIn):
    '''
    convertes lists of data classes into a single list of list of Json string representing the data class
    '''
    dataJsonAll = []
    for dataList in dataIn:
        for d in dataList:
            dataRow = []
            dataRow.append(d.to_json())
            dataJsonAll.append(dataRow)
    return dataJsonAll

# -------------------------------- write data to file -------------------------------------------------------

# doc       current model document
# dataOutPutFileName    fully qualified file path to data out put file
def WriteJsonDataToFile (doc, dataOutPutFileName):
    '''
    collects geometry data and writes it to a new json formatted file
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