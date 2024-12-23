"""
An extension to modify (show) grid bubbles at one end. One end is th end point of the grid line when it was created.

Usage:

- Run this script in a view where you want to switch all bubbles at one end on.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import grids and bubbles from library
from grids_and_bubbles.grids import switch_1_end_bubbles_on_in_view

# switches all bubbles in the active view off
switch_1_end_bubbles_on_in_view(doc)
