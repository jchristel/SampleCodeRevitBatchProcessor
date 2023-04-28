#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#License:
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

import utilAddRevBVN as utilM # sets up all commonly used variables and path locations!

# import log utils
from duHast.Utilities import batch_processor_log_utils as logutils
from duHast.Utilities import worksharing_monitor_process as wsmp
from duHast.Utilities.console_out import output


# -------------
# main:
# -------------

# process logs
PROCESSING_RESULTS = logutils.process_log_file(utilM.LOG_MARKER_DIRECTORY)
output('Log results.... message(s): \n[{}]'.format(PROCESSING_RESULTS))

# WSMP marker files clean up
cleanUpWSMFiles_ = wsmp.clean_up_wsm_data_files(utilM.WSM_MARKER_DIRECTORY)
output('WSM files clean up.... status: {}\nWSM files clean up.... message: {}'.format(cleanUpWSMFiles_.status, cleanUpWSMFiles_.message))