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
output('Writing file Data.... status: [{}]'.format(result_.status))