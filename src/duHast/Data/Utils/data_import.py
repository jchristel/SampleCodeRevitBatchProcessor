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
# Copyright 2023, Jan Christel
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

from duHast.Data.Objects import data_ceiling as dc
from duHast.Data.Objects import data_room as dr
from duHast.Data.Utils.data_to_file import CONSTANT_DATA_FIELDS
from duHast.Utilities.files_json import read_json_data_from_file


class ReadDataFromFile:
    """
    Class to read data from a json formatted file and store it in data objects.

    The class supports the following data types:

    - :class: `.DataRoom`
    - :class: `.DataCeiling`

    """

    def __init__(self, file_path):
        """
        Class constructor.

        :param filePath: Fully qualified file path to json formatted data file.
        :type filePath: str
        """

        self.data_file_path = file_path
        self.data_type = ""
        self.data = []
        self.data_by_type = {}
        self.debug_messages = []

    # list of data types supported by this class
    SUPPORTED_DATA_TYPES = {
        dr.DataRoom.data_type: dr.DataRoom,
        dc.DataCeiling.data_type: dc.DataCeiling,
    }

    def _load_data_type(self, json_object, data_type_name):
        """
        Load data type from json object.

        :param json_object: Dictionary containing data type.
        :type json_object: dict
        :param data_type: The data type name.
        :type data_type: str
        """

        if data_type_name in json_object:
            data_type_class = self.SUPPORTED_DATA_TYPES.get(data_type_name)
            # check if supported data type
            if data_type_class is None:
                self.debug_messages.append(
                    "Data type not supported: {}".format(data_type_name)
                )
                raise ValueError("Data type not supported: {}".format(data_type_name))

            # load data
            for d in json_object[data_type_name]:
                # self.debug_messages.append("Loading data type: {}".format(data_type_name))
                p = data_type_class(d)
                # append to data by type dictionary
                if data_type_name in self.data_by_type:
                    self.data_by_type[data_type_name].append(p)
                else:
                    self.data_by_type[data_type_name] = [p]
                # append to overall data list
                self.data.append(p)

        else:
            pass
            # not all data types are always present in the json object!

    def add_debug_message_from_load(self, json):
        """
        Returns a list of debug messages from the load process.

        :return: A list of debug messages.
        :rtype: list
        """
        # debug message values
        # get fixed values
        file_name = "not set"
        date_processed = "not set"
        if CONSTANT_DATA_FIELDS["file name"] in json:
            file_name = json[CONSTANT_DATA_FIELDS["file name"]]
        if CONSTANT_DATA_FIELDS["date processed"] in json:
            date_processed = json[CONSTANT_DATA_FIELDS["date processed"]]
        # get other keys
        other_key_values = []
        other_keys = list(json.keys())
        for data_type_name in self.SUPPORTED_DATA_TYPES:
            if data_type_name in other_keys:
                other_key_values.append(
                    "{} :{} values".format(data_type_name, len(json[data_type_name]))
                )

        # build debug message
        self.debug_messages.append(
            "...Loading data from dictionary.  \n......File name: {}\n......Date processed: {}\n......{}".format(
                file_name, date_processed, "\n......".join(other_key_values)
            )
        )

    def load_data(self):
        """
        Load json formatted rows into data objects and stores them in this class.

        In the moment the following data objects are supported:

        - :class: `.DataRoom`
        - :class: `.DataCeiling`

        """

        # load json from file
        data_json = read_json_data_from_file(self.data_file_path)

        # this data can com in two different formats:
        # 1. a list of dictionaries as per item 2. below
        # 2. a dictionary with 4 keys: 'date processed', 'room', 'ceiling', 'file name'.'room'  and 'ceiling' are lists of dictionaries as  values
        # the first format is the result of multiple exported files , i.e. one per level being merged into one report file ie. for the entire building

        if len(data_json) > 0:
            # check type of data
            if isinstance(data_json, list):
                self.debug_messages.append(
                    "Data format: list of dictionaries with: {} list entries".format(
                        len(data_json)
                    )
                )
                # we have a list of dictionaries
                for entry in data_json:
                    # add debug message for this json entry
                    self.add_debug_message_from_load(entry)

                    # load each  data type
                    for data_type_name in self.SUPPORTED_DATA_TYPES:
                        self._load_data_type(
                            json_object=entry,
                            data_type_name=data_type_name,
                        )

            elif isinstance(data_json, dict):
                self.debug_messages.append(
                    "Data format: Single dictionary with: {} keys".format(
                        len(data_json)
                    )
                )
                # add debug message for this json entry
                self.add_debug_message_from_load(data_json)

                # we have a dictionary
                # load each  data type
                for data_type_name in self.SUPPORTED_DATA_TYPES:
                    self._load_data_type(
                        json_object=data_json,
                        data_type_name=data_type_name,
                    )
            else:
                raise TypeError("Data format not supported: {}".format(type(data_json)))

        else:
            self.debug_messages.append(
                "No data found in file: {}".format(self.data_file_path)
            )

        # final load stats
        self.debug_messages.append(
            "Data loaded: {} data objects".format(len(self.data))
        )
        for data_type_name in self.SUPPORTED_DATA_TYPES:
            if data_type_name in self.data_by_type:
                self.debug_messages.append(
                    "...Data type {} has: {} entries".format(
                        data_type_name, len(self.data_by_type[data_type_name])
                    )
                )
            else:
                self.debug_messages.append(
                    "...Data type {} has: 0 entries".format(data_type_name)
                )

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
