"""
An extension to modify, switch off, all grid bubbles of grids.

Usage:

- Run this script in a view where you want to switch off all grid bubbles.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import grids and bubbles from library
from grids_and_bubbles.grids import switch_all_bubbles_off_in_view

# switches all bubbles in the active view off
switch_all_bubbles_off_in_view(doc)
