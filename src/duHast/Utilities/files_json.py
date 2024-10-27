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

from duHast.Utilities.Objects import result as res

import codecs
import json

def _custom_default(o):
    """
    Encode string values to utf-8 for JSON formatted outputs.

    :param o: The value to be encoded if of type string.
    :return: Encoded string or the object's __dict__.
    """
    if isinstance(o, str):
        # Only encode if required
        if any(ord(char) > 127 for char in o):
            return o.encode("utf-8").decode("utf-8")  # Encoding and decoding to ensure the type is str
    return o.__dict__


def serialize(obj):
    """
    Serialize the object for JSON output, using to_json() if available.

    :param obj: The object to serialize.
    :return: A dictionary representation of the object.
    """
    if hasattr(obj, 'to_json') and callable(getattr(obj, 'to_json')):
        return json.loads(obj.to_json())  # Use the to_json method
    else:
        return _custom_default(obj)  # Fallback to custom default


def serialize_utf(obj):
    """
    Serialize the object for JSON output inluding utf 8, using to_json_utf() if available.

    :param obj: The object to serialize.
    :return: A dictionary representation of the object.
    """
    if hasattr(obj, 'to_json_utf') and callable(getattr(obj, 'to_json_utf')):
        return json.loads(obj.to_json())  # Use the to_json method
    else:
        return _custom_default(obj)  # Fallback to custom default


def write_json_to_file(json_data, data_output_file_path, enforce_utf8=True):
    """
    Writes collected data to a new JSON formatted file.

    :param json_data: A dictionary to be written to file.
    :param data_output_file_path: Fully qualified file path to JSON data file.
    :param enforce_utf8: Will encode any string value as UTF-8, Default is True (recommended!!).
    :return: Result class instance with status and message.
    """

    result = res.Result()

    try:
        json_object = None
        # Check if UTF-8 is to be enforced
        if enforce_utf8:
            json_object = json.dumps(
                json_data, indent=None, default=serialize_utf, ensure_ascii=False
            )
        else:
            json_object = json.dumps(
                json_data, indent=None, default=serialize, ensure_ascii=False
            )
        with codecs.open(data_output_file_path, "w", encoding="utf-8") as f:
            f.write(json_object)

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
        with open(file_path) as f:
            # returns JSON object as
            # a dictionary
            data = json.load(f)
            f.close()
    except Exception as e:
        pass
    return data
