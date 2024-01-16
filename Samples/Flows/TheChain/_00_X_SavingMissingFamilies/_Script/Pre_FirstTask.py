'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains pre task function for the first revit batch process to run only.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Writes out a log marker files to directory specified in global variable.

These files are used in the post process to get log files for this run from local user app data folder.

'''
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

import clr
import System

import utilDataBVN as utilData # sets up all commonly used variables and path locations!
# import log utils
import BatchProcessorLogUtils as logutils
import UtilBatchP as uBP

# flag whether this runs in debug or not
debug_ = False

#logfile marker creation status
statusMarker_ = False

# Add batch processor scripting references
if not debug_:
    import script_util
    statusMarker_ = logutils.WriteSessionIdMarkerFile(
        utilData.LOG_MARKER_DIRECTORY , 
        uBP.AdjustSessionIdForFileName(script_util.GetSessionId())
        )

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    '''
    Prints message either to revit batch processor console or sceen. (Depends on global debug_ flag)
    To batch processor (debug = False) or console (debug = True)

    :param message: The message to be printed, defaults to ''
    :type message: str, optional
    '''

    if not debug_:
        script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------

# show log marker status
Output('Wrote log marker: ....[' + str(statusMarker_) + ']')