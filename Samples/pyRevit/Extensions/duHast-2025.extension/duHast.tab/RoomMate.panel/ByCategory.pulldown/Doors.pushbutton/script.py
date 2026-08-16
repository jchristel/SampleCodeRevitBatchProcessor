"""
An extension to modify (show) grid bubbles at zero end. Zero end is starting point of the grid line when it was created.

Usage:

- Run this script in a view where you want to switch all bubbles at zero end on.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import grids and bubbles from library
from room_m.room_mate import doors_export_entry

# switches all bubbles in the active view off
doors_export_entry(doc, uiapp, output, forms)