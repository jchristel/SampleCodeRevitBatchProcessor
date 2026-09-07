"""
An extension to export window data to room mate

Usage:

- Run this script in a view where you want to export window data to room mate.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import grids and bubbles from library
from room_m.room_mate import windows_export_entry

# exports all windows in the active view to room mate
result = windows_export_entry(doc, uiapp, output, forms)

