'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage reader class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import codecs
import csv
import json

from duHast.DataSamples import DataCeiling as dc
from duHast.DataSamples import DataRoom as dr


class ReadDataFromFile:
    def __init__(self, filePath):
        '''
        Class constructor.

        :param filePath: Fully qualified file path to json formatted data file.
        :type filePath: str
        '''

        self.dataFilePath = filePath
        self.dataType = ''
        self.data = []

    def _read_tab_separated_file(self, filePath):
        '''
        Read a tab delimited files into a list of rows

        :param filePath: Fully qualified file path to tab separated file.
        :type filePath: str

        :return: List of List [str] representing rows and columns in text file.
        :rtype: list[list[str]]
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
        Load json formatted rows into data objects and stores them in this class.

        In the moment the following data objects are supported:

        - :class: `.DataRoom`
        - :class: `.DataCeiling`

        '''

        dataJson = self._read_tab_separated_file(self.dataFilePath)
        dataObjects = []
        for d in dataJson:
            p = None
            #load json string into dic and check what the data type is
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
        Returns all data objects where level name equals past in value.

        :param levelName: The building level name.
        :type levelName: str

        :return: A list of room and ceiling data objects
        :rtype: list [data objects]
        '''

        return (list(filter(lambda x: (x.levelName == levelName ) , self.data)))
    
    def get_data_by_level_and_dataType(self, levelName, dataType):
        '''
        Returns all data objects where level name and data type equal past in values.

        :param levelName: The building level name.
        :type levelName: str
        :param dataType: A string describing the data type\
            refer to property .dataType on data object class
        :type dataType: str

        :return: A list of data objects
        :rtype: list [data objects]
        '''

        return (list(filter(lambda x: (x.levelName == levelName and x.dataType == dataType), self.data)))

