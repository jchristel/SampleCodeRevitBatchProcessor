"""
An extension to solve room tags that are outside of rooms by moving the tag to the room reference point.

Usage:

- Run this script
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


from solvers.warnings_solvers import solve_warning_room_tag_outside_of_room

solve_warning_room_tag_outside_of_room(doc=doc, output=output, forms=forms)
