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

# this sample moves revit link instances onto a workset specified in list

# --------------------------
# Imports
# --------------------------

import clr
import System
import datetime

import utilRevitTests as utilM  # sets up all commonly used variables and path locations!

# required in lambda expressions!
clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

import Autodesk.Revit.DB as rdb

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util

    clr.AddReference("RevitAPI")
    clr.AddReference("RevitAPIUI")
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    REVIT_FILE_PATH = utilM.DEBUG_REVIT_FILE_NAME

# -------------
# my code here:
# -------------


def output(message=""):
    """
    prints message to console or rbp log console

    :param message: the message, defaults to ''
    :type message: str, optional
    """

    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print(message)


output("Executing tests.... start")


output("Executing tests.... finished ")
