"""
An extension to modify (toggle the visibility) level heads at one end. One end is the end point of the level line when it was created.

Usage:

- Run this script in a view where you want to toggle the level heads at one
- Select the levels you want to toggle the level heads visibility for.
- press "Finish" to toggle the level heads visibility.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import levels and headers from library
from levels_and_headers.levels import toggle_levels_at_1_end_by_selection

# toggle all headers at level end
toggle_levels_at_1_end_by_selection(doc, uiapp)
