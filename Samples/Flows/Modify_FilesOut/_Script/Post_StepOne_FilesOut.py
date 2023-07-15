"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a post process script outside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is run after all batch processor sessions for step one have completed.

It:

    - creates a bim360 out directory in given location
    - copies Revit files created in step one into bim360 folder:

        - as files are copied into BIM360 folder, the revision information is stripped from the files so they can be uploaded to BIM360 directly


"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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

# --------------------------
# Imports
# --------------------------

import os
import settings as settings  # sets up all commonly used variables and path locations!
from utils.utils import create_bim360_out_folder, copy_exports
from duHast.Utilities.Objects import result as res
from duHast.Utilities.console_out import output
from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.files_get import get_files_with_filter

# -------------
# my code here:
# -------------


def get_revit_file_names(revit_file_directory):
    """
    Get Revit file data from output folder.

    :return:
        Result class instance.

        - False if no Revit files where found, otherwise True.
        - result.message will contain 'Got Revit files.'.
        - result.result will contain list of lists in format [[directory path, file name]]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # get revit files in folder
    revit_files = get_files_with_filter(revit_file_directory)

    copy_data = []
    if len(revit_files) > 0:
        for revit_file in revit_files:
            directory_path = get_directory_path_from_file_path(revit_file)
            row = [directory_path, revit_file[len(directory_path) + 1 :]]
            copy_data.append(row)
        return_value.update_sep(True, "Got Revit files.")
        return_value.result = copy_data
    else:
        return_value.update_sep(False, "Failed to get any Revit files.")
    return return_value


# -------------
# main:
# -------------

# store output here:
root_path_ = settings.ROOT_PATH
# build out directory location
root_path_ = os.path.join(root_path_, settings.MODEL_OUT_FOLDER_NAME)

# set up BIM 360 NWC folder
set_up_bim360_folder_flag_ = create_bim360_out_folder(
    root_path_, settings.BIM360_FOLDER_NAME
)
# if wqe have a BIM 360 folder copy revit files into it
if set_up_bim360_folder_flag_:
    # set up a result class object with data from marker files
    export_revit_status = get_revit_file_names(root_path_)
    # build the full folder path to where files are to be copied to
    revit_export_path = os.path.join(root_path_, settings.BIM360_FOLDER_NAME)
    # duplicate revit files (but strip their revision information)
    flag_copy_revit_ = copy_exports(
        export_status=export_revit_status,
        target_folder=os.path.join(root_path_, settings.BIM360_FOLDER_NAME),
        file_extension=settings.RVT_FILE_EXTENSION,
        revision_prefix=settings.REVISION_PREFIX,
        revision_suffix=settings.REVISION_SUFFIX,
    )
    output("{} :: [{}]".format(flag_copy_revit_.message, flag_copy_revit_.status))
else:
    output("failed to set up BIM 360 out folder")
