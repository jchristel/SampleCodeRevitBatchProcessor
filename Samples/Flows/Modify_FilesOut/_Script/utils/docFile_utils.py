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

import docFile as df

# import from library
from duHast.Utilities.files_csv import read_csv_file
from duHast.Revit.Views.sheets import get_sheet_rev_by_sheet_name
from duHast.Utilities.utility import pad_single_digit_numeric_string
from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_csv import write_report_data_as_csv

# --------------- read file -------------------

def read_current_file(revision_data_path):
    """
    Read the current revision data file list located in script location.

    :param revision_data_path: fully qualified file path to revision data file
    :type revision_data_path: str
    :return: a list containing current file data
    :rtype: [docFile]
    """

    reference_list = []
    try:
        rows = read_csv_file(revision_data_path)
        for row in rows:
            reference_list.append(df.docFile(row))
    except Exception as e:
        print(str(e))
        reference_list = []
    return reference_list


def build_default_file_list(
    doc,
    revision_data_file_path,
    revit_file_name,
    splash_screen_name,
    revit_file_extension
):
    """
    Reads file data from file and stores it in a global list. 

    This list contains: 

    - the current file name(s) 
    - the file name after the export.
    - document management system number and name

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_data_file_path: _description_
    :type revision_data_file_path: _type_
    :param revit_file_name: _description_
    :type revit_file_name: _type_
    :param splash_screen_name: _description_
    :type splash_screen_name: _type_
    :param revit_file_extension: _description_
    :type revit_file_extension: _type_

    :return:
        Result class instance.

        - Read status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message(s) in format: 'Copied: currentFullFileName to newFileName'
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.status will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # will contain the old file name and the new file name (with revision data)
    matched_file_data = []
    marker_file_data = None
    # get the revision from title sheet
    rev = get_sheet_rev_by_sheet_name(doc, splash_screen_name)
    match = False
    # read current files
    file_list = read_current_file(revision_data_file_path)
    if file_list is not None and len(file_list) > 0:
        # loop over file data objects and search for match
        return_value.append_message("looking for match:".format(revit_file_name))
        for file_data in file_list:
            return_value.append_message(
                "starts with {}".format(file_data.existing_file_name)
            )
            if (
                revit_file_name.startswith(file_data.existing_file_name)
                and file_data.file_extension == revit_file_extension
            ):
                return_value.append_message("Found match!")
                match = True
                file_data.revision = rev  # update with latest revision from sheet
                # pad revision out to two digits if required
                file_data.revision = pad_single_digit_numeric_string(file_data.revision)
                # store updated file data to be written to marker file
     
                marker_file_data = file_data.get_data()

                # get new file name for saving as
                new_file_name = file_data.get_new_file_name()

                # build revision file name
                row_default_new = []
                row_default_new.append(file_data.existing_file_name)
                row_default_new.append(new_file_name)
                matched_file_data.append(row_default_new)

        if match == False:
            # check whether we found a match
            return_value.update_sep(False, "No file name match found in file list.")
    else:
        return_value.update_sep(False, "File data list is empty!")
    return return_value, matched_file_data, marker_file_data


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
                nfd.existingFileName == cfd.existingFileName
                and nfd.fileExtension == cfd.fileExtension
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
        data.append(doc_file.getData())
    return data
