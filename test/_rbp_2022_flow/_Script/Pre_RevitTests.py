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

# this sample shows how to set up a dated folder as a pre - process

# --------------------------
# Imports
# --------------------------

import os

# import flow specific utils
import utilRevitTests as utilM  # sets up all commonly used variables and path locations!

# import common library (in this case the post lib since it got the methods we are after)
# import log utils
from duHast.Utilities import batch_processor_log_utils as logutils
from duHast.Utilities import util_batch_p as uBP
from duHast.Utilities.files_get import get_files

# import WSM kill utils
from duHast.Utilities import worksharing_monitor_process as wsmp

# flag whether this runs in debug or not
debug_ = False

# logfile marker creation status
status_marker_ = False

# Add batch processor scripting references
if not debug_:
    import script_util

    status_marker_ = logutils.write_session_id_marker_file(
        utilM.LOG_MARKER_DIRECTORY,
        uBP.adjust_session_id_for_file_name(script_util.GetSessionId()),
    )
    wsm_marker_ = wsmp.write_out_wsm_data_to_file(utilM.WSM_MARKER_DIRECTORY)
# -------------
# my code here:
# -------------


# output messages either to batch processor (debug = False) or console (debug = True)
def output(message=""):
    if not debug_:
        script_util.Output(str(message))
    else:
        print(message)


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
            f = open(utilM.FULL_TASK_FILE_PATH, "w")
            for file in files:
                # only collect revit 2022 files
                if "Revit_2022" in file:
                    f.write(file + "\n")
            f.close()
    except Exception as e:
        status = False
        output("Failed to save file list with exception: {}".format(e))
    return status


# -------------
# main:
# -------------

output("Writing file Data.... start")
result_ = write_file_list(utilM.SAMPLE_FILES_DIRECTORY)
output("Writing file Data.... status: {}".format(result_))

# show WSM marker status
output(
    "Wrote WSM marker:.... status: {}\nWrote WSM marker:.... message: {}".format(
        wsm_marker_.status, wsm_marker_.message
    )
)

# show log marker status
output("Wrote log marker: ....[{}]".format(status_marker_))
