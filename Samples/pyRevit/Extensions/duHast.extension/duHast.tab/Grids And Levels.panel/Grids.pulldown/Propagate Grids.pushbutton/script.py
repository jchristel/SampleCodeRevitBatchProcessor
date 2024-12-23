"""
An extension to propagate the visibility, extend and grid bubble visibility of all grids in the active view to other views.

Usage:

- Run this script in a plan view from which you want to propagate grid settings from.
- select the views you want to propagate the grid settings to in the dialog that pops up.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import grids and bubbles from library
from grids_and_bubbles.grids_propagate import propagate_grids_to_views

# switches all bubbles in the active view off
propagate_grids_to_views(doc, forms)
