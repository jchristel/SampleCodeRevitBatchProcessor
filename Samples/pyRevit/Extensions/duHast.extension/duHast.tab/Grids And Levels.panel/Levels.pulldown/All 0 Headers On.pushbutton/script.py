"""
An extension to modify (show) level heads at zero end. Zero end is starting point of the level line when it was created.

Usage:

- Run this script in a view where you want to switch all level heads at zero end on.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from levels_and_headers.levels import switch_0_end_headers_on_in_view

# switches all headers at level start on
switch_0_end_headers_on_in_view(doc)
