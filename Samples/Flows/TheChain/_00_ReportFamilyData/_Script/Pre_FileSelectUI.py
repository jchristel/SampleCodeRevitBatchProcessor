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
from duHast.UI.script import main

# import utility modules
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
    if directory_exists(PROCESS_PATH) == False:
        output("Error: Invalid directory path passed in: {}".format(PROCESS_PATH))
        output("Exiting...")
        sys.exit(1)
        PROCESS_PATH = settings.REVIT_LIBRARY_PATH
    else:
        PROCESS_PATH = settings.REVIT_LIBRARY_PATH
else:
    PROCESS_PATH = settings.REVIT_LIBRARY_PATH

try:
    main(["-s", "-i {}".format(PROCESS_PATH), "-o {}".format(settings.TASK_FILE_DIRECTORY), "-n {}".format(settings.NUMBER_OF_TASK_FILES),"-e {}".format(".rfa")])
    sys.exit(0)
except  Exception as e:
    output("Error: {}".format(e))
    sys.exit(1)

