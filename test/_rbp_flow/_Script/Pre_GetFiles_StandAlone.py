"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script outside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- this module writes task files depending on the revit version past in.

    - sample: "Revit_2022"

- if task file creation fails it will terminate with an exit code greater than 0, indicating to the powershell script to terminate

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
#

# this sample shows how to write out a number of task files using bucket distribution

# --------------------------
# default file path locations
# --------------------------
import sys, os
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.files_get import get_files
from duHast.Utilities.console_out import output

# -------------
# my code here:
# ------------_


def write_file_list(source_directory):
    """
    Write file list for Revit 2022

    :param source_path: Directory containing Revit sample files.
    :type source_path: str
    :return: True if task list was written successfully, otherwise False
    :rtype: bool
    """

    status = True
    try:
        files = get_files(source_directory)
        if files != None and len(files) > 0:
            f = open(
                os.path.join(
                    settings.TASK_LIST_DIRECTORY, REVIT_VERSION + ".txt"
                ),
                "w",
            )
            for file in files:
                # only collect revit version specific files
                if REVIT_VERSION in file:
                    f.write(file + "\n")
            f.close()
    except Exception as e:
        status = False
        output("Failed to save file list with exception: {}".format(e))
    return status


# -------------
# main:
# -------------

#: contains the revit version. this is used to identify which files to process
REVIT_VERSION = settings.DEFAULT_REVIT_VERSION
# check if a folder path was past in from calling powershell script...otherwise go with default
if len(sys.argv) == 2:
    # build file path
    REVIT_VERSION = sys.argv[1]
    # give user feed back on default version
    output("Using Revit version: {}".format(REVIT_VERSION))
else:
    # give user feed back on default version
    output("Setting Revit version to default value: {}".format(REVIT_VERSION))

# write task file list
output("Collecting files from: {}".format(settings.SAMPLE_FILES_DIRECTORY))
status_write_tasks = write_file_list(settings.SAMPLE_FILES_DIRECTORY)
output("Collecting files completed with status: {}".format(status_write_tasks))

# make sure the calling powershell script knows if something went wrong
if status_write_tasks:
    sys.exit(0)
else:
    sys.exit(1)
