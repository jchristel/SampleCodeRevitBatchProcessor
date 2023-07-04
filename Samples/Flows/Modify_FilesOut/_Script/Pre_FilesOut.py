#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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
import utilModifyBVN as utilM # sets up all commonly used variables and path locations!
# import common library (in this case the post lib since it got the methods we are after)
from duHast.Utilities import Utility as util
# import log utils
from duHast.Utilities import BatchProcessorLogUtils as logutils
# import WSM kill utils
from duHast.Utilities import WorksharingMonitorProcess as wsmp
from duHast.Utilities import UtilBatchP as uBP


# flag whether this runs in debug or not
debug_ = False

#logfile marker creation status
status_marker_ = False

#logfile marker creation status
wsm_marker_ = False

# Add batch processor scripting references
if not debug_:
    import script_util
    status_marker_ = logutils.WriteSessionIdMarkerFile(utilM.LOG_MARKER_DIRECTORY , uBP.AdjustSessionIdForFileName(script_util.GetSessionId()))
    wsm_marker_ = wsmp.WriteOutWSMDataToFile(utilM.WSM_MARKER_DIRECTORY)
# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------
# show log marker status
Output('Wrote log marker: ....[{}]'.format(status_marker_))
# show WSM marker status
Output('WSM marker result: {} :: [{}]'.format(wsm_marker_.message , wsm_marker_.status))

# store output here:
root_path_ = utilM.ROOT_PATH

#create Model out folder
Output('Creating model out folder.... start')
result_ = util.CreateTargetFolder(root_path_, utilM.MODEL_OUT_FOLDER_NAME)
Output('Creating model out folder.... status: {}'.format(result_))