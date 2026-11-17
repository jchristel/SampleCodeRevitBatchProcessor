"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the flows global settings.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- duHast and room_m are loaded from the installed RoomMate pyRevit extension, not from this repository:
  RoomMate ships the duHast it was built and tested against, and that copy decides what a task does.

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
# Copyright 2026, Jan Christel
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

import sys
import os

# The installed RoomMate extension (the RoomMate installer, or build-extension.ps1 -Deploy). Its lib folder holds
# room_m and the duHast RoomMate pins. It goes FIRST on the path so that copy of duHast is the one imported.
ROOMMATE_EXTENSION_LIB = os.path.join(
    os.environ.get("APPDATA", ""), r"pyRevit\Extensions\RoomMate.extension\lib"
)
sys.path.insert(0, ROOMMATE_EXTENSION_LIB)

from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.directory_io import get_parent_directory

# --------------------------------------------- flow directories ---------------------------------------------

SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
sys.path += [SCRIPT_DIRECTORY]
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)

# log marker and work sharing monitor marker files
LOG_MARKER_DIRECTORY = os.path.join(FLOW_DIRECTORY, r"_LogMarker")
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

# task lists: one per Revit Batch Processor session (one settings file each in _settings)
TASK_LIST_DIRECTORY = os.path.join(FLOW_DIRECTORY, r"_TaskList")
NO_OF_TASK_LIST_FILES = 1

# --------------------------------------------- files to process ---------------------------------------------

FILE_EXTENSION_OF_FILES_TO_PROCESS = ".rvt"
IS_CLOUD_PROJECT = False
PATH_TO_FILES_TO_PROCESS = r"\path\to\source\files"

# a file to run the script against outside of Revit Batch Processor (debug)
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

# --------------------------------------------- RoomMate ---------------------------------------------

# The RoomMate project the models belong to (its id, as the server's project list shows it).
ROOMMATE_PROJECT_ID = "House A"

# The RoomMate server. Empty: the address kept in each model (Server button), then the ROOMMATE_SERVER
# environment variable, then %APPDATA%\RoomMate\server.json, as the buttons use.
# Set: used for every model of this run, e.g. "http://192.168.0.97:5151".
ROOMMATE_SERVER = ""

# Write tasks the plug-in warns about (a missing room tag, an elevation it could not place, ...)?
# False: they are reported aborted with their warnings, and a person looks at them first.
PROCEED_WITH_WARNINGS = False

# Which id the tasks are queued under. Tasks are kept per model id, which is the model's title when it was
# exported. Revit Batch Processor opens a NEW LOCAL copy of a central model (see the settings file), whose
# title can differ from the central's. True: ask for the central file's name (without .rvt), which is what an
# export from a normal local copy sends in most setups. False: ask for the open document's title.
MODEL_ID_FROM_FILE_NAME = True

# After the tasks: synchronise a workshared model with central (or save a non workshared one), only when at
# least one task was written. False: the changes are discarded when Revit Batch Processor closes the model.
SAVE_WHEN_CHANGED = True
