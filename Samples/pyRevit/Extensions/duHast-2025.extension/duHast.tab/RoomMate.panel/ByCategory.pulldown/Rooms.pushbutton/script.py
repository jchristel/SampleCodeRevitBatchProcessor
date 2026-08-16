"""
Exports ROOMS ONLY from the selected model(s) and pushes them to Room Mate.

Doors already on the server are left untouched -- use the panel's combined
"Export" button when both halves should go up together.

Usage:

- Run this script and pick the model(s), the target project, and the phase.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import the rooms-only export entry point from the library
from room_m.room_mate import rooms_only_export_entry

# push rooms, and only rooms
rooms_only_export_entry(doc, uiapp, output, forms)
