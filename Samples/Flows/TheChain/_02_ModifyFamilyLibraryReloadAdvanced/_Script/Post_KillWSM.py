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
# default file path locations
# --------------------------


#import clr
#import System
#from System.IO import Path

import utilReloadBVN as utilR # sets up all commonly used variables and path locations!
# import WSM kill utils
import WorksharingMonitorProcess as wsmp

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import script_util

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

# kill off all WSM sessions, no directory path required since we want to kill all WSM sessions
statusWSMKill_ = wsmp.DieWSMDie('', True)

# show WSM kill status
Output('WSM Kill status: ....' + str(statusWSMKill_.message) + ' [' + str(statusWSMKill_.status) + ']')