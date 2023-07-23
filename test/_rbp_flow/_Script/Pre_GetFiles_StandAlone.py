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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
