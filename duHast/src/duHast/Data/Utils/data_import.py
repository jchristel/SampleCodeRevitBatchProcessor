"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage reader class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
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
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#


# import clr
# clr.AddReference("System.Core")
# from System import Linq
# clr.ImportExtensions(Linq)

import json

from duHast.Data.Objects import data_ceiling as dc
from duHast.Data.Objects import data_room as dr


class ReadDataFromFile:
    def __init__(self, file_path):
        """
        Class constructor.

        :param filePath: Fully qualified file path to json formatted data file.
        :type filePath: str
        """

        self.data_file_path = file_path
        self.data_type = ""
        self.data = []

    def _read_json_file(self, file_path):
        """
        Reads a json formatted text file into a dictionary.

        :param file_path: Fully qualified file path to json formatted data file.
        :type file_path: str

        :return: A dictionary.
        :rtype: {}
        """

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

    def _get_room_data_from_JSON(self, room_data):
        """
        Converts dictionary into data room objects.

        :param room_data: List of dictionaries describing rooms
        :type room_data:  [{var}]

        :return: List of data room objects.
        :rtype: [:class:`.DataRoom`]
        """

        all_rooms = []
        for d in room_data:
            p = dr.DataRoom(d)
            all_rooms.append(p)
        return all_rooms

    def _get_ceiling_data_from_JSON(self, ceiling_data):
        """
        Converts dictionary into data ceiling objects.

        :param ceiling_data: List of dictionaries describing ceilings
        :type ceiling_data: [{var}]

        :return: List of data ceiling objects.
        :rtype: [:class:`.DataCeiling`]
        """

        all_ceilings = []

        for d in ceiling_data:
            p = dc.DataCeiling(d)
            all_ceilings.append(p)
        return all_ceilings

    def load_data(self):
        """
        Load json formatted rows into data objects and stores them in this class.

        In the moment the following data objects are supported:

        - :class: `.DataRoom`
        - :class: `.DataCeiling`

        """

        data_objects = []
        data_json = self._read_json_file(self.data_file_path)

        if len(data_json) > 0:
            # load rooms {Root}.rooms
            room_json = self._get_room_data_from_JSON(data_json[dr.DataRoom.data_type])

            # add to global list
            for rj in room_json:
                data_objects.append(rj)

            # load ceiling at {Root}.ceilings
            ceiling_json = self._get_ceiling_data_from_JSON(
                data_json[dc.DataCeiling.data_type]
            )

            # add to global list
            for cj in ceiling_json:
                data_objects.append(cj)
        self.data = data_objects

    def get_data_by_level(self, level_name):
        """
        Returns all data objects where level name equals past in value.

        :param level_name: The building level name.
        :type level_name: str

        :return: A list of room and ceiling data objects
        :rtype: list [data objects]
        """

        return list(filter(lambda x: (x.level.name == level_name), self.data))

    def get_data_by_type(self, data_type):
        """
        Returns all data objects where type equals past in type name

        :param data_type: The data type name.
        :type data_type: str

        :return: A list of room and ceiling data objects
        :rtype: list [data objects]
        """

        return list(filter(lambda x: (x.data_type == data_type), self.data))

    def get_data_by_level_and_data_type(self, level_name, data_type):
        """
        Returns all data objects where level name and data type equal past in values.

        :param level_name: The building level name.
        :type level_name: str
        :param data_type: A string describing the data type\
            refer to property .dataType on data object class
        :type data_type: str

        :return: A list of data objects
        :rtype: list [data objects]
        """

        return list(
            filter(
                lambda x: (x.level.name == level_name and x.data_type == data_type),
                self.data,
            )
        )
