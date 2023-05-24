"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing post processing script which runs outside the revit batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- runs at the very end of the flow
- processes log files ( did any exception occur?)
- deletes marker files

    - log marker files
    - revit work sharing monitor marker files
    
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

import utilAddRev as utilM  # sets up all commonly used variables and path locations!

# import log utils
from duHast.Utilities import batch_processor_log_utils as logUtils
from duHast.Utilities import worksharing_monitor_process as wsmp
from duHast.Utilities.console_out import output


# -------------
# main:
# -------------

PROCESSING_RESULTS = logUtils.process_log_files(utilM.LOG_MARKER_DIRECTORY)
output("Log results.... message(s): \n[{}]".format(PROCESSING_RESULTS.status))
output(PROCESSING_RESULTS.message)
# remove old log marker files
flag_delete_log_markers = logUtils.delete_log_data_files(utilM.LOG_MARKER_DIRECTORY)
output("Log marker deletion.: [{}]".format(flag_delete_log_markers))

# WSMP marker files clean up
cleanUpWSMFiles_ = wsmp.clean_up_wsm_data_files(utilM.WSM_MARKER_DIRECTORY)
output(
    "WSM files clean up.... status: [{}]\nWSM files clean up.... message: {}".format(
        cleanUpWSMFiles_.status, cleanUpWSMFiles_.message
    )
)
