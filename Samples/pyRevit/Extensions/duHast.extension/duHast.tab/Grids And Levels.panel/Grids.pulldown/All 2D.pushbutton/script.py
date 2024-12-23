"""
An extension to set both ends of a grid lines two 2D.

Usage:

- Run this script in a view where you want to switch all grid ends two 2D.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import grids and bubbles from library
from grids_and_bubbles.grids import set_grids_in_view_to_2d

# switches all bubbles in the active view off
set_grids_in_view_to_2d(doc)
