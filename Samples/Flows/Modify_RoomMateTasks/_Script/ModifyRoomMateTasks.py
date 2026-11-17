"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit Batch Processor task script: run the RoomMate room tasks queued for each model, with nobody asked.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The RoomMate Tasks button without the window: every queued task of the open model (populate and update tasks place
items, create RLS tasks make room layout sheets) is claimed from the RoomMate server, checked, written one task per
transaction group, and reported back. RoomMate does all of that (room_m.room_mate.tasks_unattended); this script
only opens the door and saves.

- needs the RoomMate pyRevit extension installed on this machine (see settings.py)
- warned tasks are aborted unless PROCEED_WITH_WARNINGS is set
- incomplete RLS settings in a model abort its create RLS tasks: fix them with the RLS settings button
- the model is synchronised (or saved) only when a task was written
- every step is also written to RoomMate.log, in the RoomMate folder of the application data

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

import clr
import os

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Revit.Common.file_io import sync_file, save_file
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.console_out import output

# -------------
# my code here:
# -------------

# the server for every model of this run, when the settings name one (else the model's own, as the buttons do)
if settings.ROOMMATE_SERVER:
    os.environ["ROOMMATE_SERVER"] = settings.ROOMMATE_SERVER

from room_m.room_mate import tasks_unattended


def say(message):
    """Print a line to the Revit Batch Processor log (or the console when debugging)."""
    output(message, revit_script_util.Output)


def model_id_of(doc, revit_file_path):
    """The id the model's tasks are queued under (see MODEL_ID_FROM_FILE_NAME in settings.py)."""
    if settings.MODEL_ID_FROM_FILE_NAME and revit_file_path:
        return get_file_name_without_ext(revit_file_path)
    return doc.Title


def save(doc):
    """Synchronise a workshared model with central, save any other."""
    if doc.IsWorkshared:
        say("Syncing to Central: start")
        result = sync_file(doc)
    else:
        say("Saving: start")
        result = save_file(doc)
    say("{} [{}]".format(result.message, result.status))
    return result.status


# ---------------------------------- main ----------------------------------

# debug mode revit project file name
DEBUG = __name__ == "__main__"

if DEBUG:
    # outside of Revit Batch Processor: nothing to open a model with
    output("This script runs in Revit Batch Processor; nothing to do outside it.")
else:
    import revit_script_util

    doc = revit_script_util.GetScriptDocument()
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()

    say("RoomMate tasks.... start: {}".format(REVIT_FILE_PATH))
    model_id = model_id_of(doc, REVIT_FILE_PATH)
    result = tasks_unattended(
        doc,
        settings.ROOMMATE_PROJECT_ID,
        proceed_with_warnings=settings.PROCEED_WITH_WARNINGS,
        say=say,
        model_id=model_id,
    )
    outcome = result.result[0] if result.result else {"claimed": 0, "written": 0}
    say("Tasks claimed: {}, written: {} [{}]".format(outcome["claimed"], outcome["written"], result.status))

    if outcome["written"] and settings.SAVE_WHEN_CHANGED:
        save(doc)
    elif outcome["written"]:
        say("Not saved (SAVE_WHEN_CHANGED is off): the changes are discarded when the model closes.")
    else:
        say("Nothing written: model not saved.")

    say("RoomMate tasks.... finished")
