"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing cleanup functions functions used in post step 2 script.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deletes temp files in

- temp output location
- model export directory


"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# --------------------------
# Imports
# --------------------------

# import settings
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.Objects import result as res
from duHast.Utilities.directory_io import (
    get_child_directories,
    directory_delete,
)
from duHast.Utilities.files_get import get_files_with_filter
from duHast.Utilities.files_io import file_delete


# deletes back up folders and revit project files
def clean_up_export_folder(model_export_directory):
    """
    Cleans up any log, marker, revit files no longer required in temp location as well as in model export location.

    :param model_export_directory: Fully qualified directory to where exported models are located.
    :type model_export_directory: str

    :return:
        Result class instance.

        - Cleanup status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain messages for each file/directory deleted.
        - result.result will be an empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # delete sub directories
    try:
        sub_dirs = get_child_directories(settings.OUTPUT_FOLDER)
        if len(sub_dirs) > 0:
            for d in sub_dirs:
                delete_dir_flag = directory_delete(d)
                return_value.update_sep(
                    delete_dir_flag,
                    "Deleted directory {} with status [{}]".format(d, delete_dir_flag),
                )
        else:
            return_value.append_message(
                "No sub directories found in: {}".format(settings.OUTPUT_FOLDER)
            )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to delete sub directory with exception {}".format(e)
        )

    try:
        # delete rvt files
        revit_files = get_files_with_filter(settings.OUTPUT_FOLDER)
        if len(revit_files) > 0:
            for f in revit_files:
                delete_revit_file_flag = file_delete(f)
                return_value.update_sep(
                    delete_revit_file_flag,
                    "Deleted Revit file {} with status [{}]".format(
                        f, delete_revit_file_flag
                    ),
                )
        else:
            return_value.append_message(
                "No Revit files found in directory: {}".format(settings.OUTPUT_FOLDER)
            )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to delete file with exception {}".format(e)
        )

    try:
        # delete txt marker files
        text_files = get_files_with_filter(
            model_export_directory, settings.MARKER_FILE_EXTENSION, "*"
        )
        if len(text_files) > 0:
            for f in text_files:
                delete_marker_file_flag = file_delete(f)
                return_value.update_sep(
                    delete_revit_file_flag,
                    "Deleted text marker file {} with status [{}]".format(
                        f, delete_marker_file_flag
                    ),
                )
        else:
            return_value.append_message(
                "No text marker files found in directory: {}".format(
                    model_export_directory
                )
            )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to delete marker file with exception {}".format(e)
        )

    try:
        # delete log files
        text_files = get_files_with_filter(model_export_directory, ".log", "*")
        if len(text_files) > 0:
            for f in text_files:
                delete_log_file_flag = file_delete(f)
                return_value.update_sep(
                    delete_log_file_flag,
                    "Deleted log file {} with status [{}]".format(
                        f, delete_log_file_flag
                    ),
                )
        else:
            return_value.append_message(
                "No log files found in directory: {}".format(model_export_directory)
            )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to delete log file with exception {}".format(e)
        )

    return return_value
