"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as a pre process script outside the batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- this module writes Revit files to task lists.

"""

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

# this sample shows how to write out a number of task files using bucket distribution

import sys

import settings as settings # sets up all commonly used variables and path locations!
# import file list module
from duHast.UI import file_list as fl
from duHast.Utilities.console_out import output

# -------------
# my code here:
# -------------

# -------------
# main:
# -------------

output ('Collecting files from: {}'.format(settings.PATH_TO_FILES_TO_PROCESS))
# get file data
output('Writing file Data.... start')
result_ = fl.write_file_list(
    settings.PATH_TO_FILES_TO_PROCESS ,
    settings.FILE_EXTENSION_OF_FILES_TO_PROCESS, 
    settings.TASK_LIST_DIRECTORY, 
    settings.NO_OF_TASK_LIST_FILES, 
    fl.get_revit_files
    )

output (result_.message)
output('Writing file Data.... status: [{}]'.format(result_.status))

# make sure the calling powershell script knows if something went wrong
if (result_.status):
    sys.exit(0)
else:
    sys.exit(1)