"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script within the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- writes marker files to identify log files used in this process
- writes Revit work sharing marker files identifying Revit work sharing monitor sessions running
"""

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


# --------------------------
# Imports
# --------------------------

import script_util

# import flow specific utils
import settings as settings  # sets up all commonly used variables and path locations!

# import common library (in this case the post lib since it got the methods we are after)
# import log utils
from duHast.Utilities import batch_processor_log_utils as logUtils
from duHast.Utilities import util_batch_p as uBP
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


# -------------
# main:
# -------------

output("Script directory: {}".format(settings.SCRIPT_DIRECTORY), script_util.Output)
output("flow directory: {}".format(settings.FLOW_DIRECTORY), script_util.Output)
output("duHast directory: {}".format(settings.DU_HAST_DIRECTORY), script_util.Output)

# show WSM marker status
output(
    "Wrote WSM marker:.... status: [{}]\nWrote WSM marker:.... message: \n\t{}".format(
        wsm_marker_.status, wsm_marker_.message
    ),
    script_util.Output,
)

# show log marker status
output("Wrote log marker: ....[{}]".format(status_marker_), script_util.Output)
