"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a post process script within the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- kills all running revit work sharing monitor sessions

"""
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

# import script_util
import script_util
from duHast.Utilities.console_out import output

# -------------
# my code here:
# -------------

# -------------
# main:
# -------------

# kill off all WSM sessions
statusWSMKill_ = wsmp.die_wsm_die(utilM.WSM_MARKER_DIRECTORY, True)

# show WSM kill status
output(
    "WSM Kill status: ....{} [{}]".format(
        statusWSMKill_.message, statusWSMKill_.status
    ),
    script_util.Output,
)
