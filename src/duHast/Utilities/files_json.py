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

import traceback

from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_get import get_files_single_directory

import codecs
import json
import os


def serialize(obj):
    """
    Serialize the object for JSON output, using to_json() if available.

    :param obj: The object to serialize.
    :return: A dictionary representation of the object.
    """
    if hasattr(obj, "class_to_dict") and callable(getattr(obj, "class_to_dict")):
        return json.loads(
            json.dumps(obj.class_to_dict(), indent=None)
        )  # Use the class_to_dict method
    else:
        return obj.__dict__  # Fallback to default


def serialize_utf(obj):
    """
    Serialize the object for JSON output including utf 8, using to_json_utf() if available.

    :param obj: The object to serialize.
    :return: A dictionary representation of the object.
    """
    if hasattr(obj, "to_json_utf") and callable(getattr(obj, "to_json_utf")):
        return json.loads(obj.to_json_utf())  # Use the to_json_utf method
    else:
        return obj.__dict__  # Fallback to default


def write_json_to_file(json_data, data_output_file_path, enforce_utf8=True):
    """
    Writes collected data to a new JSON formatted file.

    :param json_data: A dictionary to be written to file.
    :param data_output_file_path: Fully qualified file path to JSON data file.
    :param enforce_utf8: Will encode any string value as UTF-8, Default is True (recommended!!).

    :return:
        Result class instance.

        - result.status (bool) True if file was written without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be a single entry list containing json data as string.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
         result.result be an empty list
    :rtype: :class:`.Result`
    """

    result = res.Result()
    # file placeholder
    f = None
    try:

        json_string = None
        # Check if UTF-8 is to be enforced
        if enforce_utf8:

            json_string = json.dumps(
                json_data, indent=None, default=serialize_utf, ensure_ascii=False
            )
            # write data with codecs to ensure utf-8 encoding (slow)
            with codecs.open(data_output_file_path, "w", encoding="utf-8") as f:
                f.write(json_string)

        else:
            json_string = json.dumps(json_data, indent=None, default=serialize)

            # write data without codecs (fast)?
            with open(data_output_file_path, "w") as f:
                f.write(json_string)

        result.update_sep(
            True, "Data written to file: {}".format(data_output_file_path)
        )

        result.result.append(json_string)
    except Exception as e:
        tb = traceback.format_exc().strip().split("\n")
        result.update_sep(
            False,
            "Failed to write data to file with exception: {}. Trace back: {}".format(
                e, "::".join(tb)
            ),
        )
    finally:
        # make sure to close the file
        if f is not None:
            f.close()
    return result


def read_json_data_from_file(file_path):
    """
    Reads json from file in utf-8 encoded format.

    :param file_path: Fully qualified file path of json file to read.
    :type file_path: str

    :return:
        Result class instance.

        - result.status (bool) True if file was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a dictionary with the data read from the file.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
         result.result be an empty list
    :rtype: :class:`.Result`
    """

    result = res.Result()
    data = {}
    try:
        # Opening JSON file as utf-8
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            # returns JSON object as
            # a dictionary
            data = json.load(f)
            f.close()

        # store the data in the result object
        result.result.append(data)
        result.update_sep(True, "Data read from file: {}".format(file_path))

    except Exception as e:
        result.update_sep(
            False, "Failed to read data to file with exception: {}".format(e)
        )
    return result


def combine_files_json(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.txt",
    file_getter=get_files_single_directory,
):
    """
    Combines multiple json formatted text files into a single json list formatted file, where each file is a list entry.
    Assumes:

    - each file can contain a single line json formatted string

    The new file will be saved into the same folder as the original files.

    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param out_put_file_name: The file name of the combined file, defaults to 'result.txt'
    :type out_put_file_name: str, optional
    :param file_getter: Function returning list of files to be combined, defaults to GetFilesSingleFolder
    :type file_getter: func(folder_path, file_prefix, file_suffix, file_extension), optional

    :return:
        Result class instance.

        - result.status (bool) True if file where combined without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a dictionaries with the data read from the file(s).

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
         result.result be an empty list
    :rtype: :class:`.Result`

    """

    result = res.Result()
    try:
        # get all files to be combined
        file_list = file_getter(folder_path, file_prefix, file_suffix, file_extension)

        # read json data into a list of json objects
        json_objects = []
        for file in file_list:
            read_result = read_json_data_from_file(file_path=file)
            result.update(read_result)
            if read_result.status == False:
                return result
            json_objects.append(read_result.result[0])

        # write json data out
        result_write = write_json_to_file(
            json_data=json_objects,
            data_output_file_path=os.path.join(folder_path, output_file_name),
        )
        result.update(result_write)
    except Exception as e:
        result.update_sep(False, "Failed to combine files with exception: {}".format(e))

    return result
