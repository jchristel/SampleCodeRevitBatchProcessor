"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script outside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- this module writes Revit files to task lists.

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
# Copyright 2023, Jan Christel
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

# this sample shows how to write out a number of task files using bucket distribution

import sys
import os

import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res

# import file list module
from duHast.UI.file_list import (
    write_file_list,
    bucket_to_task_list_bim_360,
    get_revit_files,
)
from duHast.Revit.BIM360.util_bim_360 import get_bim_360_revit_files_from_file_list
from duHast.Utilities.console_out import output
from duHast.Utilities.directory_io import directory_exists
from duHast.Utilities.files_io import file_exist

# -------------
# my code here:
# -------------

# -------------
# main:
# -------------

# will contain either a folder path of where to collect files from or a fully qualified file path to
# process exceptions file which will contain list of files to process again
PROCESS_PATH = ""

# check if a folder path was past in...otherwise go with default
if len(sys.argv) == 2:
    # build file path
    PROCESS_PATH = sys.argv[1]
    # check for valid path
    if directory_exists(PROCESS_PATH) == True:
        PROCESS_PATH = os.path.join(
            PROCESS_PATH, settings.FILE_NAME_SECOND_PROCESS_FAMILIES_REPORT
        )
        # TODO: check if file exists and if not write out empty task files!
        if file_exist(PROCESS_PATH) == False:
            output("No task file present in input folder: {}".format(PROCESS_PATH))
            # exit with an error status
            sys.exit(2)
    else:
        PROCESS_PATH = settings.REVIT_LIBRARY_PATH
else:
    PROCESS_PATH = settings.REVIT_LIBRARY_PATH


output("Collecting files from: {}".format(PROCESS_PATH))
# get file data
output("Writing file Data.... start")
result_ = res.Result()

# check if cloud vs file based models
if settings.IS_CLOUD_PROJECT == False:
    # get files from a network server
    result_ = write_file_list(
        directory_path=PROCESS_PATH,
        file_extension=settings.FILE_EXTENSION_OF_FILES_TO_PROCESS,
        task_list_directory=settings.TASK_FILE_DIRECTORY,
        task_files_number=settings.NUMBER_OF_TASK_FILES,
        file_getter=get_revit_files,
    )
else:
    # get files from a csv file list containing cloud based model data
    result_ = write_file_list(
        directory_path=PROCESS_PATH,
        file_extension=settings.FILE_EXTENSION_OF_FILES_TO_PROCESS,
        task_list_directory=settings.TASK_FILE_DIRECTORY,
        task_files_number=settings.NUMBER_OF_TASK_FILES,
        file_getter=get_bim_360_revit_files_from_file_list,
        file_data_processor=bucket_to_task_list_bim_360,
    )

output(result_.message)
output("Writing file Data.... status: [{}]".format(result_.status))

# make sure the calling powershell script knows if something went wrong
if result_.status:
    sys.exit(0)
else:
    sys.exit(1)
