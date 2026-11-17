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
# BSD License
# Copyright 2023, Jan Christel
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
#

# --------------------------
# Imports
# --------------------------

import settings as settings  # sets up all commonly used variables and path locations!

# import log utils
from duHast.Utilities import batch_processor_log_utils as logUtils
from duHast.Utilities import worksharing_monitor_process as wsmp
from duHast.Utilities.console_out import output


# -------------
# main:
# -------------

PROCESSING_RESULTS = logUtils.process_log_files(settings.LOG_MARKER_DIRECTORY)
output("Log results.... message(s): \n[{}]".format(PROCESSING_RESULTS.status))
output(PROCESSING_RESULTS.message)
# remove old log marker files
flag_delete_log_markers = logUtils.delete_log_data_files(settings.LOG_MARKER_DIRECTORY)
output("Log marker deletion.: [{}]".format(flag_delete_log_markers))

# WSMP marker files clean up
cleanUpWSMFiles_ = wsmp.clean_up_wsm_data_files(settings.WSM_MARKER_DIRECTORY)
output(
    "WSM files clean up.... status: [{}]\nWSM files clean up.... message: {}".format(
        cleanUpWSMFiles_.status, cleanUpWSMFiles_.message
    )
)