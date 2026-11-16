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


# --------------------------
# default file path locations1
# --------------------------

import sys, os

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output
from duHast.Revit.Family.Data.family_base_data_reload_advanced import build_work_lists


# -------------
# my code here:
# -------------


# -------------
# main:
# -------------

output("Python pre process script: Reload list builder start ...")
# check if a folder path was past in...otherwise go with default
if len(sys.argv) == 2:
    _root_path = sys.argv[1]
    output("Using past in path: {}".format(_root_path))
    result = build_work_lists(
        _root_path,  # change list file path
        settings.FAMILY_BASE_DATA_REPORT_FILE_PATH,  # report data file path ( may need refresh prior run!!)
        settings.RELOAD_LIST_OUTPUT_DIRECTORY,  # output folder
    )
    output("[{}]".format(result.status))
    output(result.message)

    if result.status:
        sys.exit(0)
    else:
        sys.exit(2)
else:
    _root_path = r"C:\Users\jchristel\Documents\DebugRevitBP\FamReload"
    output("Aborted with default file path: {}".format(_root_path))
    sys.exit(2)
