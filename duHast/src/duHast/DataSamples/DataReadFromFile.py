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



#import clr
#clr.AddReference("System.Core")
#from System import Linq
#clr.ImportExtensions(Linq)

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

    def _read_json_file(self, file_path):
        '''
        Reads a json formatted text file into a dictionary.

        :param file_path: Fully qualified file path to json formatted data file.
        :type file_path: str

        :return: A dictionary.
        :rtype: {}
        '''

        data = {}
        try:
            # Opening JSON file
            f = open(file_path)
            # returns JSON object as
            # a dictionary
            data = json.load(f)
        except Exception as e:
            pass
        return data


    def _get_room_data_from_JSON(self,room_data):
        '''
        Converts dictionary into data room objects.

        :param room_data: List of dictionaries describing rooms
        :type room_data:  [{var}]

        :return: List of data room objects.
        :rtype: [:class:`.DataRoom`]
        '''

        all_rooms =[]
        for d in room_data:
            p = dr.DataRoom(d)
            all_rooms.append(p)
        return all_rooms 

    def _get_ceiling_data_from_JSON(self,ceiling_data):
        '''
        Converts dictionary into data ceiling objects.

        :param ceiling_data: List of dictionaries describing ceilings
        :type ceiling_data: [{var}]

        :return: List of data ceiling objects.
        :rtype: [:class:`.DataCeiling`]
        '''
         
        all_ceilings =[]

        for d in ceiling_data:
            p = dc.DataCeiling(d)
            all_ceilings.append(p)
        return all_ceilings 
    
    def load_data(self):
        '''
        Load json formatted rows into data objects and stores them in this class.

        In the moment the following data objects are supported:

        - :class: `.DataRoom`
        - :class: `.DataCeiling`

        '''

        data_objects = []
        data_json = self._read_json_file(self.dataFilePath)

        if(len(data_json) > 0):
            # load rooms {Root}.rooms
            room_json = self._get_room_data_from_JSON(data_json[dr.DataRoom.dataType])

            # add to global list
            for rj in room_json:
                data_objects.append(rj)

            #load ceiling at {Root}.ceilings
            ceiling_json = self._get_ceiling_data_from_JSON(data_json[dc.DataCeiling.dataType])
        
            # add to global list
            for cj in ceiling_json:
                data_objects.append(cj)
        
        self.data = data_objects
    
    def get_data_by_level(self, level_name):
        '''
        Returns all data objects where level name equals past in value.

        :param level_name: The building level name.
        :type level_name: str

        :return: A list of room and ceiling data objects
        :rtype: list [data objects]
        '''

        return (list(filter(lambda x: (x.level.levelName == level_name ) , self.data)))
    
    def get_data_by_type(self, data_type):
        '''
        Returns all data objects where type equals past in type name

        :param data_type: The data type name.
        :type data_type: str

        :return: A list of room and ceiling data objects
        :rtype: list [data objects]
        '''

        return (list(filter(lambda x: (x.dataType == data_type ) , self.data)))
    
    def get_data_by_level_and_data_type(self, level_name, data_type):
        '''
        Returns all data objects where level name and data type equal past in values.

        :param level_name: The building level name.
        :type level_name: str
        :param data_type: A string describing the data type\
            refer to property .dataType on data object class
        :type data_type: str

        :return: A list of data objects
        :rtype: list [data objects]
        '''

        return (list(filter(lambda x: (x.level.levelName == level_name and x.dataType == data_type), self.data)))

