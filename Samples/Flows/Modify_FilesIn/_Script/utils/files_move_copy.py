"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a file location helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- move files
- copy files

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

# required for list.Where...lambda
import clr
import System

clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)
# --------------------------
# default file path locations
# --------------------------
import os

import settings as settings

from utils.file_data import get_file_data_by_name
from duHast.Utilities.files_get import get_file_name_without_ext, get_files_with_filter
from duHast.Utilities.files_io import copy_file, file_move
from duHast.Utilities.date_stamps import (
    get_folder_date_stamp,
)
from duHast.Utilities.directory_io import directory_exists, create_target_directory


# ------------------------------------------------------------- COPY FILES -------------------------------------------------------------


def get_target_file_name(current_file_name, filtered_file_data, output):
    """
    Get the new file name from file data instance for the provided old file name.

    :param current_file_name: current file name
    :type current_file_name: str
    :param filtered_file_data: list of docExFile class objects
    :type filtered_file_data: list
    :param output: output function
    :type output: function
    :return: new file name
    :rtype: str
    """

    return_value = current_file_name
    found_match = False
    try:
        fd = get_file_data_by_name(filtered_file_data, current_file_name)
        if fd != None:
            found_match = True
            return_value = fd.new_file_name
    except Exception as e:
        output(
            "Failed to find match for {} with exception: {}".format(
                current_file_name, e
            )
        )
        return return_value
    if found_match:
        output(
            "Found match for:  {} New file name: {}".format(
                current_file_name, return_value
            )
        )
    else:
        output("Found no match for:  {}".format(current_file_name))
    return return_value


def copy_other_files(file_data, file_extension, output):
    """
    Copy files with the provided extension into the designated folder(s)

    Get all file data instances with the provided extension and copies any matching files from the source location into the designated folder(s).

    :param file_data: list of docExFile class objects
    :type file_data: list
    :param file_extension: file extension
    :type file_extension: str
    :param output: output function
    :type output: function
    :return: True if successful, otherwise False
    :rtype: bool
    """

    status = True
    try:
        # filter out files matching the provided extension
        filtered_file_data = file_data.Where(
            lambda x: x.file_extension == file_extension
        ).ToList()

        # check if any matches were found
        if filtered_file_data != None and len(filtered_file_data) > 0:
            # check whether any files match the filter
            for fd in filtered_file_data:
                files_matching = get_files_with_filter(
                    settings.PATH_TO_FILES_TO_PROCESS,
                    fd.file_extension,
                    fd.existing_file_name + "*",
                )
                if files_matching != None and len(files_matching) > 0:
                    for file in files_matching:
                        try:
                            # extract file name only
                            current_file_name = get_file_name_without_ext(file)
                            # source_path = os.path.join(_sourcePath , current_file_name+ file_extension)

                            destination_file_name = get_target_file_name(
                                current_file_name, filtered_file_data, output
                            )
                            destination_path = os.path.join(
                                fd.save_as_location, destination_file_name + file_extension
                            )
                            status_copy = copy_file(file, destination_path)
                            status = status & status_copy
                            if status_copy == False:
                                output(
                                    "Failed to copy file from:\n{}\nto:\n{}".format(
                                        file, destination_path
                                    )
                                )
                            else:
                                output(
                                    "Copied file from:\n...{}\nto:\n...{}".format(
                                        file, destination_path
                                    )
                                )
                        except Exception as e:
                            output(
                                "Failed to copy file from:\n{}\nto:\n{} with exception: {}".format(
                                    file, destination_path, e
                                )
                            )
                            status = False
                else:
                    output(
                        "No files with extension {} are matching filter: {} in source location: {}".format(
                            file_extension,
                            fd.existing_file_name,
                            settings.PATH_TO_FILES_TO_PROCESS,
                        )
                    )
        else:
            output(
                "Found no files with extension {} to copy into the designated folder(s)".format(
                    file_extension
                )
            )
    except Exception as e:
        output(
            "Failed to copy files with extension {} into the designated folder(s) with exception: {}".format(
                file_extension, e
            )
        )
        status = False
    return status


# ------------------------------------------------------------- MOVE FILES -------------------------------------------------------------


def move_files_to_filing_location(file_data, output):
    """
    Move files into the designated folder(s)

    Loops over the file data and attempts to find matches for each instance in the source location, and if found, moves the file into the designated folder(s).

    :param file_data: list of docExFile class objects
    :type file_data: list
    :param output: output function
    :type output: function
    :return: True if successful, otherwise False
    :rtype: bool
    """

    status = True
    try:
        # get the date stamp
        folder_name = get_folder_date_stamp() + settings.MODEL_IN_FILING_FOLDER_NAME
        # move all files into consultant in
        for file_data_instance in file_data:
            # check if target root path still exists
            if directory_exists(file_data_instance.file_in_filing):
                # check whether any files in source location match the filter
                files_matching = get_files_with_filter(
                    settings.PATH_TO_FILES_TO_PROCESS,
                    file_data_instance.file_extension,
                    file_data_instance.existing_file_name + "*",
                )
                # move any matching files into file in location
                if files_matching != None and len(files_matching) > 0:
                    flag_got_directory = create_target_directory(
                        file_data_instance.file_in_filing, folder_name
                    )
                    if flag_got_directory:
                        # move files
                        for file in files_matching:
                            try:
                                # extract file name only
                                file_name = get_file_name_without_ext(file)
                                # src = _sourcePath + "\\" + file_name

                                destination_path = os.path.join(
                                    file_data_instance.file_in_filing,
                                    folder_name,
                                    file_name + file_data_instance.file_extension,
                                )

                                status_move = file_move(file, destination_path)
                                status = status & status_move

                                if status_move == False:
                                    output(
                                        "Failed to move file from:\n{}\nto:\n{}".format(
                                            file, destination_path
                                        )
                                    )
                                else:
                                    output(
                                        "Moved file from:\n{}\nto:\n{}".format(
                                            file, destination_path
                                        )
                                    )

                            except Exception as e:
                                output(
                                    "Failed to move file from:\n{}\nto:\n{} with exception: {}".format(
                                        file, destination_path, e
                                    )
                                )
                                status = False
                    else:
                        output(
                            "Failed to create target folder: {}".format(
                                os.path.join(file_data_instance.file_in_filing, folder_name)
                            )
                        )
                else:
                    output(
                        "No files matching filter {} in source location: {}".format(
                            file_data_instance.existing_file_name,
                            settings.PATH_TO_FILES_TO_PROCESS,
                        )
                    )
            else:
                output("{} no longer exists!".format(file_data_instance.file_in_filing))
                status = False
    except Exception as e:
        output(
            "Failed to move files into the designated folder(s) with exception: {}".format(
                e
            )
        )
        status = False
    return status
