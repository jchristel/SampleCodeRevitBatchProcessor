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

# this sample shows how to set up a dated folder as a pre - process

# --------------------------
# Imports
# --------------------------


# import flow specific utils
import utilAddRev as utilM # sets up all commonly used variables and path locations!
# import common library (in this case the post lib since it got the methods we are after)
# import log utils
from duHast.Utilities import batch_processor_log_utils as logutils
from duHast.Utilities import util_batch_p as uBP
# import WSM kill utils
from duHast.Utilities import worksharing_monitor_process as wsmp

# flag whether this runs in debug or not
debug_ = False

#logfile marker creation status
statusMarker_ = False

# Add batch processor scripting references
if not debug_:
    import script_util
    statusMarker_ = logutils.write_session_id_marker_file(
        utilM.LOG_MARKER_DIRECTORY , 
        uBP.adjust_session_id_for_file_name(script_util.GetSessionId())
    )
    wsmMarker_ = wsmp.write_out_wsm_data_to_file(utilM.WSM_MARKER_DIRECTORY)
# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def output(message = ''):
    if not debug_:
        script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------

# show WSM marker status
output('Wrote WSM marker:.... status: {}\nWrote WSM marker:.... message: {}'.format(wsmMarker_.status, wsmMarker_.message))

# show log marker status
output('Wrote log marker: ....[{}]'.format(statusMarker_))