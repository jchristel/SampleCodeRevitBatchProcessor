"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions writing / reading json objects to/ from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

from duHast.Utilities import result as res

import codecs
import json


def write_json_to_file(json_data, data_output_file_path):
    """
    Writes collected data to a new json formatted file.

    :param json_data: A dictionary to be written to file.
    :type json_data: json object (dictionary)
    :param data_output_file_path: Fully qualified file path to json data file.
    :type data_output_file_path: str
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
    """

    result = res.Result()

    try:
        json_object = json.dumps(json_data, indent=None, default=lambda o: o.__dict__)
        with codecs.open(data_output_file_path, "w", encoding="utf-8") as f:
            f.write(json_object)
            f.close()

        result.update_sep(
            True, "Data written to file: {}".format(data_output_file_path)
        )
    except Exception as e:
        result.update_sep(
            False, "Failed to write data to file with exception: {}".format(e)
        )
    return result

def read_json_data_from_file(file_path):
    """
    Reads json from file

    :param revit_file_path: Fully qualified file path of report file.
    :type file_path: str
    :return: json object
    :rtype: {}
    """

    data = {}
    try:
        # Opening JSON file
        with open (file_path) as f:
            # returns JSON object as
            # a dictionary
            data = json.load(f)
            f.close()
    except Exception as e:
        pass
    return data
