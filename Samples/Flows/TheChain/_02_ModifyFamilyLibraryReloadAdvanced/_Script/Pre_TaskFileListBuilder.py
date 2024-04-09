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
# default file path locations1
# --------------------------

import sys, os

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output
from duHast.UI.file_list import (
    get_revit_files_for_processing,
    get_file_size,
    write_revit_task_file,
    bucket_to_task_list_file_system,
)
from duHast.UI.workloader import distribute_workload

# -------------
# my code here:
# -------------

# -------------
# main:
# -------------
output("Python pre process script: Task list builder start ...")
# check if a folder path was past in...otherwise go with default
if len(sys.argv) == 3:
    _root_path = sys.argv[1]
    _file_name = sys.argv[2]
    output("Using past in path: {}".format(_root_path))
    output("Using past in file name: {}".format(_file_name))

    # get files to be processed
    _revit_files = get_revit_files_for_processing(
        os.path.join(_root_path, _file_name),
        False,
        settings.FILE_EXTENSION_OF_FILES_TO_PROCESS,
    )

    if len(_revit_files) > 0:
        # for rf in revitFiles:
        #    Output(rf.name + ' :: ' + str(rf.size))

        # build bucket list
        buckets = distribute_workload(
            settings.TASK_FILE_NO, _revit_files, get_file_size
        )

        # write out file lists
        counter = 0
        for bucket in buckets:
            fileName = os.path.join(
                settings.TASK_FILE_DIRECTORY, "Tasklist_{}.txt".format(counter)
            )
            statusWrite = write_revit_task_file(
                fileName, bucket, bucket_to_task_list_file_system
            )
            output(statusWrite.message)
            counter += 1
        output("Finished writing out task files")
        sys.exit(0)
    else:
        # do nothing...
        output("No files selected!")
        sys.exit(2)
else:
    rootPath_ = r"C:\Users\jchristel\Documents\DebugRevitBP\FamReload"
    output("Aborted with default file path: {}".format(rootPath_))
    sys.exit(2)
