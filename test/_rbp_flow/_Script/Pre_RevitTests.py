"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script within the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- populates task list files for revit batch processor

    - note: does not filter out back up files!!
    
- writes marker files to identify log files used in this process
- writes revit work sharing marker files identifying Revit work sharing monitor sessions running
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
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# --------------------------
# Imports
# --------------------------

import script_util

import settings as settings  # sets up all commonly used variables and path locations!

# import common library (in this case the post lib since it got the methods we are after)
# import log utils
from duHast.Utilities import batch_processor_log_utils as logUtils
from duHast.Utilities import util_batch_p as uBP
from duHast.Utilities.files_get import get_files
from duHast.Utilities.console_out import output

# import WSM kill utils
from duHast.Utilities import worksharing_monitor_process as wsmp


# logfile marker creation status
status_marker_ = logUtils.write_session_id_marker_file(
    settings.LOG_MARKER_DIRECTORY,
    uBP.adjust_session_id_for_file_name(script_util.GetSessionId()),
)

wsm_marker_ = wsmp.write_out_wsm_data_to_file(settings.WSM_MARKER_DIRECTORY)

# -------------
# my code here:
# -------------


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
            f = open(settings.FULL_TASK_FILE_PATH, "w")
            for file in files:
                # only collect revit 2022 files
                if "Revit_2022" in file:
                    f.write(file + "\n")
            f.close()
    except Exception as e:
        status = False
        output(
            "Failed to save file list with exception: {}".format(e), script_util.Output
        )
    return status


# -------------
# main:
# -------------

output("Script directory: {}".format(settings.SCRIPT_DIRECTORY), script_util.Output)
output("flow directory: {}".format(settings.FLOW_DIRECTORY), script_util.Output)
output("duHast directory: {}".format(settings.DU_HAST_DIRECTORY), script_util.Output)
output(
    "duHast test directory: {}".format(settings.DU_HAST_TEST_DIRECTORY), script_util.Output
)

'''
output("Writing file Data.... start", script_util.Output)
result_ = write_file_list(settings.SAMPLE_FILES_DIRECTORY)
output("Writing file Data.... status: [{}]".format(result_), script_util.Output)
'''
# show WSM marker status
output(
    "Wrote WSM marker:.... status: [{}]\nWrote WSM marker:.... message: \n\t{}".format(
        wsm_marker_.status, wsm_marker_.message
    ),
    script_util.Output,
)

# show log marker status
output("Wrote log marker: ....[{}]".format(status_marker_), script_util.Output)
