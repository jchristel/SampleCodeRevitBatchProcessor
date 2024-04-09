"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a revision tracker related helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

import os
import settings as settings
from utils.file_data import get_file_data_by_name_and_extension
from duHast.Utilities.files_get import get_files, get_file_name_without_ext
from duHast.Utilities.files_io import get_file_extension

from duHast.Utilities.date_stamps import (
    get_date_stamp,
    FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC,
)

from duHast.Utilities.files_csv import write_report_data_as_csv


# saves out a file where each row contains the dates a file was received last
# this reads the file and only overwrites the date of files a match was found for
def save_files_received_list(current_document_data, output):
    """
    Save the files received list.

    - received files data is saved to a csv file
    - if the file does not exist, it is created
    - if the file exists, the data is appended to the file

    :param current_document_data: current document data
    :type current_document_data: list
    :param output: output function
    :type output: function
    :return: status
    :rtype: bool
    """

    status = True
    # received file data as docFileReport objects
    received_file_data = get_received_files_data(current_document_data, output)

    output("received Issue data: {}".format(len(received_file_data)))
    if len(received_file_data) > 0:
        try:
            write_report_data_as_csv(
                file_name=os.path.join(
                    settings.PATH_TO_FILES_TO_PROCESS, settings.REVISION_TRACKER_FILE_NAME
                ),
                header=[],
                data=received_file_data,
                write_type="a",
            )
        except Exception as e:
            status = False
            output(
                "Failed to save received files data to file: {} with exception: {}".format(
                    settings.REVISION_TRACKER_FILE_NAME, e
                )
            )
    else:
        status = False
        output("No received files data to save!")
    return status


# retrieves revision information from files received and matches it up with file reference data
def get_received_files_data(current_document_data, output):
    """
    Get the received files data in list of list format.

    - list contains the following data:

    - date received
    - file name (new)
    - file extension
    - revision

    :return: list of list containing received files data
    :rtype: list
    """
    files = []
    # loop over current doc data and update revision to matches found
    # get files in folder
    files_received = get_files(settings.PATH_TO_FILES_TO_PROCESS, ".*")
    if files_received != None and len(files_received) > 0:
        # shorten file information
        for f in files_received:
            # attempt to get file information
            file_name_short = get_file_name_without_ext(f)
            # make sure extension is lower case
            file_extension = get_file_extension(f).lower()
            file_match = get_file_data_by_name_and_extension(
                current_document_data, file_name_short, file_extension
            )

            if file_match != None:
                # get revision from file
                rev = get_revision(file_name_short)
                files.append(
                    [
                        get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC),
                        file_match.new_file_name,
                        file_match.file_extension,
                        rev,
                    ]
                )
            else:
                output("Failed to find match in file data for file: {}".format(f))
    return files


def get_revision(file_name):
    """
    Get the revision from the file name.

    - if no revision is found, return "-"
    - if revision is found, return the revision

    :param file_name: file name
    :type file_name: str
    :return: revision
    :rtype: str
    """

    return_value = "-"
    for rev_start in settings.REVISION_SEPARATORS_START:
        # check if file contains any of these
        start_index = file_name.find(rev_start)
        if start_index > 0:
            end_index = start_index + 1
            # look for end of revision
            for rev_end in settings.REVISION_SEPARATORS_END:
                end_index = file_name.find(rev_end)
                if end_index > 0:
                    break
            return_value = file_name[start_index + 1 : end_index]
            break
    return return_value
