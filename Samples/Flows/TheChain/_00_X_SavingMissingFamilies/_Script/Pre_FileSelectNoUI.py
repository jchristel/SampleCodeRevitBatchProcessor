"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains pre task function(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Writes out a task lists of files to be processed based on missing families host report

- Host report is located in /Users/Username/_Input directory
- Number of task files in specified in global variable.
- Task file location is specified in global varaible.

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

# --------------------------
# Imports
# --------------------------

import sys
import os

import settings as settings  # sets up all commonly used variables and path locations!

# import file list module
from duHast.UI.file_list import (
    write_file_list,
    get_files_from_csv_list_file,
    get_task_file_name,
    write_empty_task_list,
)
from duHast.Utilities.console_out import output
from duHast.Utilities.files_io import file_exist


# -------------
# my code here:
# -------------

# -------------
# main:
# -------------

# build file path to missing families host family report
PROCESS_PATH = os.path.join(
    settings.INPUT_DIRECTORY, settings.FILE_NAME_MISSING_FAMILIES_HOSTS_REPORT
)

if file_exist(PROCESS_PATH):
    # give user feed back
    output("Collecting files from: {}".format(PROCESS_PATH))

    # write out task lists
    result_ = write_file_list(
        PROCESS_PATH,
        settings.FILE_EXTENSION_OF_FILES_TO_PROCESS,
        settings.TASK_FILE_DIRECTORY,
        settings.NUMBER_OF_TASK_FILES,
        get_files_from_csv_list_file,
    )
    output("Wrote {} task file(s): [{}]".format(len(result_.result), result_.status))
    
    # check if any file to be processed where found!
    if result_.status and len(result_.result) == 0:
        # no file found...: write out empty task lists!
        for i in range(settings.NUMBER_OF_TASK_FILES):
            file_name = get_task_file_name(settings.TASK_FILE_DIRECTORY, i)
            result_empty_ = write_empty_task_list(file_name)
            result_.update(result_empty_)

    # give user feed back
    output(result_.message)
    output("Writing file Data.... status: {}".format(result_.status))
else:
    output("Missing families host report does not exist: {}".format(PROCESS_PATH))
    # exit with error
    sys.exit(2)
