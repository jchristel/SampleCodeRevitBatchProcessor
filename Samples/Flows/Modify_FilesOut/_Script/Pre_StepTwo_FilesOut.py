"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script inside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is only run as a pre process on the first batch processor session (TwoA) started in step two!

It:

    - creates a new set of task files containing the revit files created in step one

"""

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

import os
import script_util
import settings as settings # sets up all commonly used variables and path locations!

from duHast.UI import file_list as fl
from duHast.Utilities.console_out import output
from duHast.Utilities import batch_processor_log_utils as logUtils
from duHast.Utilities import util_batch_p as uBP


# -------------
# my code here:
# -------------


# -------------
# main:
# -------------


#logfile marker creation status
status_marker_ = False

# logfile marker creation status
status_marker_ = logUtils.write_session_id_marker_file(
    settings.LOG_MARKER_DIRECTORY,
    uBP.adjust_session_id_for_file_name(script_util.GetSessionId()),
)

# show log marker status
output("Wrote log marker: ....[{}]".format(status_marker_))

# store output here:
root_path_ = settings.ROOT_PATH
root_path_ = os.path.join(root_path_ , settings.MODEL_OUT_FOLDER_NAME)
output ('Collecting files from: {}'.format(root_path_))

# get file data
output('Writing file Data.... start')
result_ = fl.write_file_list(
    directory_path=root_path_ ,
    file_extension=settings.FILE_EXTENSION_OF_FILES_TO_PROCESS, 
    task_list_directory=settings.OUTPUT_FOLDER, 
    task_files_number=settings.NO_OF_TASK_LIST_FILES, 
    file_getter=fl.get_revit_files
    )
output (result_.message)
output('Writing file Data.... status: {}'.format(result_.status))