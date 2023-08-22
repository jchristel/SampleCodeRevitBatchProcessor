"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the Revit view report functionality.
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

from duHast.Revit.Views.Objects.view_graphics_settings import ViewGraphicsSettings
from duHast.Utilities.files_json import write_json_to_file, read_json_data_from_file
from duHast.Revit.Views.Reporting.view_reports_json_props import (
    PROP_FILE_NAME,
    PROP_VIEW_DATA,
)


def write_graphics_settings_report(revit_file_name, file_path, data):
    """
    Write view graphic settings to file.

    :param revit_file_name: The revit file name (without path or file extension)
    :type revit_file_name: str
    :param file_path: Fully qualified file path
    :type file_path: str
    :param data: json dictionary to be written to file
    :type data: {str:Any}

    :return:
        Result class instance.

        - result.status False if file failed to write, otherwise True.
        - result.message will contain file name of file written.
        - result.result: empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result: will be an empty list

    :rtype: :class:`.Result`
    """

    # wrap data to include file name
    json_data = {PROP_FILE_NAME: revit_file_name, PROP_VIEW_DATA: data}

    result = write_json_to_file(json_data=json_data, data_output_file_path=file_path)
    return result


def read_view_data_from_file(file_path):
    """
    Reads a view data report file into a list of view graphic setting instances

    :param file_path: Fully qualified file path of report file.
    :type file_path: str
    :raises ValueError: If data node is missing from file

    :return: list of settings if files was read successfully otherwise an exception will be raised.
    :rtype: :class:`.ViewGraphicsSettings`
    """

    data_views = []
    # read json file
    data_read = read_json_data_from_file(file_path=file_path)

    # check if this is a list of data view items
    if isinstance(data_read, list):
        for data_entry in data_read:
            # check it got the required property node
            if (PROP_VIEW_DATA) in data_entry:
                # convert node entries into class instances
                for entry in data_entry[PROP_VIEW_DATA]:
                    data_view = ViewGraphicsSettings(j=entry)
                    data_views.append(data_view)
    elif isinstance(data_read, dict):
        # check it got the required property node
        if (PROP_VIEW_DATA) in data_read:
            # convert node entries into class instances
            for entry in data_read[PROP_VIEW_DATA]:
                data_view = ViewGraphicsSettings(j=entry)
                data_views.append(data_view)
    else:
        # missing node...raise an exception
        raise ValueError("Data does not contain a {} node".format(PROP_VIEW_DATA))

    return data_views
