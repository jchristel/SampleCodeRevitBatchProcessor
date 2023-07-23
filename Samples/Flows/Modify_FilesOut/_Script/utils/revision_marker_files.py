"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing revision marker files related functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These files are used to rename exports (ifc , nwc) with the right revision information.
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import os
import docFile as df

from duHast.Utilities.files_get import get_files
from duHast.Utilities.files_csv import read_csv_file, write_report_data_as_csv
from duHast.Utilities.Objects import result as res


def read_marker_files_from_revit_processed(marker_dir_path, marker_file_extension):
    """
    Reads marker files into docfile objects.

    :param marker_dir_path: Fully qualified directory path containing marker files.
    :type marker_dir_path: str
    :param marker_file_extension: marker file extension in format ".ext"
    :type marker_file_extension: str

    :return:
        Result class instance.

        - Read status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain 'Read marker file(s)'.
        - result.result will contain list of docFile objects

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    marker_file_data = []
    # get all text files in location
    marker_files = get_files(marker_dir_path, marker_file_extension)
    if len(marker_files) > 0:
        try:
            for mf in marker_files:
                rows = read_csv_file(mf)
                for row in rows:  # each row is a list
                    # read information into class
                    marker_file_data.append(df.docFile(row))
        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to read marker file from Revit export with exception: {}".format(
                    e
                ),
            )
    return_value.update_sep(True, "Read marker file(s)")
    return_value.result = marker_file_data
    return return_value


def write_rev_marker_file_writer(fully_qualified_path, file_data):
    """
    Writes out revision marker file

    :param fully_qualified_path: Fully qualified file path of revision marker file.
    :type fully_qualified_path: str
    :param file_data: File data to be written to file.
    :type file_data: [str]

    :return:
        Result class instance.

        - Write status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message(s) in format: 'Successfully wrote marker file: marker file name'
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.status will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    if len(file_data) > 0:
        try:
            write_report_data_as_csv(fully_qualified_path, [], [file_data])
            return_value.append_message = "Successfully wrote marker file: {}".format(
                fully_qualified_path
            )
        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to write data file! {} with exception: {}".format(
                    fully_qualified_path, e
                ),
            )
    return return_value


def write_rev_marker_file(
    file_data, root_path, revit_file_name, revit_file_extension, marker_file_extension
):
    """
    Writes out a revision marker file containing the new file revision.

    :return:
        Result class instance.

        - Write status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message(s) in format: 'Successfully wrote marker file: marker file name'
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.status will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    if file_data != None and len(file_data) > 0:
        # add revit file extension to marker file name
        file_name = os.path.join(
            root_path, revit_file_name + revit_file_extension + marker_file_extension
        )
        status = write_rev_marker_file_writer(file_name, file_data)
        return_value.update(status)

    else:
        return_value.update_sep(
            False,
            "Failed to write marker file: No file data found for: {}".format(
                revit_file_name
            ),
        )
    return return_value
