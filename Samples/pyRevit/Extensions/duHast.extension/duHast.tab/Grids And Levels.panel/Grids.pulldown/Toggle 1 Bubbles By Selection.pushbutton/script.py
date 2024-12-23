"""
An extension to modify (toggle the visibility) grid bubbles at one end. One end is the end point of the grid line when it was created.

Usage:

- Run this script in a view where you want to toggle the bubbles at one
- Select the grids you want to toggle the bubbles for.
- press "Finish" to toggle the bubbles.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import grids and bubbles from library
from grids_and_bubbles.grids import toggle_grids_at_1_end_by_selection

# switches all bubbles in the active view off
toggle_grids_at_1_end_by_selection(doc, uiapp)
