"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script within the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is run as a pre process on the second and following batch processor session started in step one and two only!

- populates task list files for revit batch processor
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
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# this sample shows how to set up a dated folder as a pre - process

# --------------------------
# Imports
# --------------------------

import script_util

import settings as settings  # sets up all commonly used variables and path locations!

# import log utils
from duHast.Utilities import batch_processor_log_utils as logUtils
from duHast.Utilities import util_batch_p as uBP

# import WSM kill utils
from duHast.Utilities import worksharing_monitor_process as wsmp
from duHast.Utilities.console_out import output


# logfile marker creation status
status_marker_ = False

# logfile marker creation status
status_marker_ = logUtils.write_session_id_marker_file(
    settings.LOG_MARKER_DIRECTORY,
    uBP.adjust_session_id_for_file_name(script_util.GetSessionId()),
)

wsm_marker_ = wsmp.write_out_wsm_data_to_file(settings.WSM_MARKER_DIRECTORY)

# -------------
# my code here:
# -------------

output("Script directory: {}".format(settings.SCRIPT_DIRECTORY), script_util.Output)
output("flow directory: {}".format(settings.FLOW_DIRECTORY), script_util.Output)
output("duHast directory: {}".format(settings.DU_HAST_DIRECTORY), script_util.Output)

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
