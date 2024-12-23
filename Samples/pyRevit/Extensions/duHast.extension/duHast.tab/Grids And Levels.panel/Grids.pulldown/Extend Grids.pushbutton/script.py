"""
An extension to modify, extend, all grids to the view crop.

Note:

- The view needs to have the crop enabled.

Usage:

- Run this script in a plan view where you want to extend all grids to the view crop.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import grids and bubbles from library
from grids_and_bubbles.grids import extend_grids_to_view_crop

# switches all bubbles in the active view off
extend_grids_to_view_crop(doc)
