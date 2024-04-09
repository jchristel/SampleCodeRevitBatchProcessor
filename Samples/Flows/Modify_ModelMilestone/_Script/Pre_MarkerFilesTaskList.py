"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the flow pre execution script.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script runs inside Revit Batch Processor Environment as a pre execution script. It is used to:

- write out marker files for WSM and logs
- write out file list of files to be processed

Its attached to the first batch processor task in the flow.

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
# Copyright 2024, Jan Christel
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


# set path to common library
import settings as settings

# import libraries
from duHast.UI import file_list as fl
from duHast.Utilities.console_out import output
# import WSM kill utils
from duHast.Utilities import worksharing_monitor_process as wsmp
# import log utils
from duHast.Utilities import batch_processor_log_utils as logutils
from duHast.Utilities import util_batch_p as uBP

import script_util

# logfile marker creation status
status_marker_ = False

# logfile marker creation status
status_marker_ = logutils.write_session_id_marker_file(
    settings.LOG_MARKER_DIRECTORY,
    uBP.adjust_session_id_for_file_name(script_util.GetSessionId()),
)

wsm_marker_ = wsmp.write_out_wsm_data_to_file(settings.WSM_MARKER_DIRECTORY)

# -------------
# my code here:
# -------------

output("Script directory: {}".format(settings.SCRIPT_DIRECTORY), script_util.Output)
output("flow directory: {}".format(settings.FLOW_DIRECTORY), script_util.Output)
if settings._use_dev_du_hast:
    output(
        "duHast directory: {}".format(settings.DU_HAST_DIRECTORY_DEV_LOCAL),
        script_util.Output,
    )
else:
    output( "duHast directory: {}".format(settings.DU_HAST_DIRECTORY_DEV_NETWORK),
        script_util.Output,
    )


# -------------
# main:
# -------------

# show WSM marker status
output(
    "Wrote WSM marker:.... status: [{}]\n\tWrote WSM marker:.... message: {}".format(
        wsm_marker_.status, wsm_marker_.message
    ),
    script_util.Output,
)

# show log marker status
output(
    "Wrote log marker: ....[{}]".format(status_marker_),
    script_util.Output,
)

# get file data
output("Writing file Data.... start")
try:
    RESULT = fl.write_file_list(
        settings.PATH_TO_FILES_TO_PROCESS,
        settings.FILE_EXTENSION_OF_FILES_TO_PROCESS,
        settings.TASK_LIST_DIRECTORY,
        settings.NO_OF_TASK_LIST_FILES,
        fl.get_revit_files,
    )
    output(RESULT.message)
    output(
        "Writing file Data.... status: [{}]".format(RESULT.status), script_util.Output
    )
except Exception as e:
    output("Failed to write file list with exception: {}".format(e), script_util.Output)
