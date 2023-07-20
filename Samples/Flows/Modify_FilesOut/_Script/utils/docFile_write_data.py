"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a custom helper functions for marker files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- bim 360 folder
- export file name
- copy export files
- read the current file list in docFile objects

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

# import settings
import settings as settings  # sets up all commonly used variables and path locations!

# import from library
from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_csv import write_report_data_as_csv

# --------------- write file -------------------

# writes out the document data file back in the script folder
# with updated revision information retrieved from marker files
def write_new_file_data(doc_files, marker_file_data):
    """
    _summary_

    :param doc_files: _description_
    :type doc_files: _type_
    :param marker_file_data: _description_
    :type marker_file_data: _type_
    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    flag = False
    # compare lists
    doc_files_sorted = []
    for cfd in doc_files:
        match = False
        for nfd in marker_file_data:
            if (
                nfd.existing_file_name == cfd.existing_file_name
                and nfd.file_extension == cfd.file_extension
            ):
                match = True
                doc_files_sorted.append(nfd)
                break
        if match == False:
            doc_files_sorted.append(cfd)
    data = convert_class_to_string(doc_files_sorted)
    flag = write_new_data(settings.REVISION_DATA_FILEPATH, data)
    return_value.update(flag)
    return_value.result.append(doc_files_sorted)
    return return_value


# write new revision data out to file
def write_new_data(path, data):
    """
    _summary_

    :param path: _description_
    :type path: _type_
    :param data: _description_
    :type data: _type_
    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    try:
        write_report_data_as_csv(path, [], data)
        return_value.append_message("Wrote new meta data file to: {}".format(path))
    except Exception as e:
        return_value.update_sep(False,"Failed to write data file: {} with exception: {}".format(path, e))
    return return_value


def convert_class_to_string(doc_files):
    """
    _summary_

    :param doc_files: _description_
    :type doc_files: _type_
    :return: _description_
    :rtype: _type_
    """
    
    data = []
    for doc_file in doc_files:
        data.append(doc_file.get_data())
    return data
