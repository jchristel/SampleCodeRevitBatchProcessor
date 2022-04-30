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

import codecs
import csv
import json

import DataCeiling as dc
import DataRoom as dr


class ReadDataFromFile:
    def __init__(self, filePath):
        self.dataFilePath = filePath
        self.dataType = ''
        self.data = []

    # filePath      fully qualified file path to tab separated file
    def _read_tab_separated_file(self, filePath):
        '''
        read a tab delimited files into a list of rows
        '''
        rowList = []
        try:
            with codecs.open (filePath,'r',encoding='utf-8') as f:
                reader = csv.reader(f, dialect='excel-tab')
                for row in reader: # each row is a list
                    rowList.append(row)
                f.close()
        except Exception as e:
            print (str(e))
            rowList = []
        return rowList

    def load_Data(self):
        '''
        load json formatted rows into data objects
        '''
        dataJson = self._read_tab_separated_file(self.dataFilePath)
        dataObjects = []
        for d in dataJson:
            p = None
            #load json string into dic and check whjat the data type is
            dummy = json.loads(d[0])
            if('dataType' in dummy):
                if(dummy['dataType'] == dr.DataRoom.dataType):
                    p = dr.DataRoom(d[0])
                    self.dataType = p.dataType
                elif(dummy['dataType'] == dc.DataCeiling.dataType):
                    dic = json.loads(d[0])
                    json_data = json.dumps(dic, default=lambda o: o.__dict__, indent=None)
                    p = dc.DataCeiling(json_data)
                    self.dataType = p.dataType
            dataObjects.append(p)
        self.data = dataObjects
    
    def get_data_by_level(self, levelName):
        '''
        returns all data objects where level name equals passt in value
        '''
        return (list(filter(lambda x: (x.levelName == levelName ) , self.data)))
    
    def get_data_by_level_and_dataType(self, levelName, dataType):
        '''
        returns all data objects where level name and datattype equal passt in values
        '''
        return (list(filter(lambda x: (x.levelName == levelName and x.dataType == dataType), self.data)))

