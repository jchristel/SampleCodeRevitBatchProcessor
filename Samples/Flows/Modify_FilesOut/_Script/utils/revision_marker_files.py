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
# Copyright (c) 2020  Jan Christel
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
        status, message_marker = write_rev_marker_file(file_name, file_data[0])
        return_value.update_sep(status, message_marker)

    else:
        return_value.update_sep(
            False,
            "Failed to write marker file: No file data found for: {}".format(
                revit_file_name
            ),
        )
    return return_value
