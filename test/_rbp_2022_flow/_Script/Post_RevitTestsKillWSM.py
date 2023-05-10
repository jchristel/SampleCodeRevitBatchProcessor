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

import utilRevitTests as utilM  # sets up all commonly used variables and path locations!

# import WSM kill utils
from duHast.Utilities import worksharing_monitor_process as wsmp

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import script_util

# -------------
# my code here:
# -------------


# output messages either to batch processor (debug = False) or console (debug = True)
def output(message=""):
    if not debug_:
        script_util.Output(str(message))
    else:
        print(message)


# -------------
# main:
# -------------

# kill off all WSM sessions
statusWSMKill_ = wsmp.die_wsm_die(utilM.WSM_MARKER_DIRECTORY, True)

# show WSM kill status
output(
    "WSM Kill status: ....{} [{}]".format(statusWSMKill_.message, statusWSMKill_.status)
)
