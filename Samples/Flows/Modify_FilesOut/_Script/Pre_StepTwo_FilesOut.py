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

# --------------------------
# default file path locations
# --------------------------

import utilModifyBVN as utilM # sets up all commonly used variables and path locations!
# import common library (in this case the post lib since it got the methods we are after)
from duHast.Utilities import Utility as util
# import log utils
from duHast.Utilities import BatchProcessorLogUtils as logutils
from duHast.Utilities import UtilBatchP as uBP
# import file list module
from duHast.UI import FileList as fl

# flag whether this runs in debug or not
debug_ = False

#logfile marker creation status
status_marker_ = False

# Add batch processor scripting references
if not debug_:
    import script_util
    status_marker_ = logutils.WriteSessionIdMarkerFile(utilM.LOG_MARKER_DIRECTORY , uBP.AdjustSessionIdForFileName(script_util.GetSessionId()))
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

# store output here:
root_path_ = utilM.ROOT_PATH

root_path_ = root_path_ + '\\' + utilM.MODEL_OUT_FOLDER_NAME
Output ('Collecting files from: {}'.format(root_path_))
# get file data
Output('Writing file Data.... start')
result_ = fl.WriteFileList(
    root_path_ ,
    utilM.FILE_EXTENSION_OF_FILES_TO_PROCESS, 
    utilM.ROOT_PATH_EXPORT, 
    utilM.TASK_FILE_NO, 
    fl.getRevitFiles
    )
Output (result_.message)
Output('Writing file Data.... status: {}'.format(result_.status))