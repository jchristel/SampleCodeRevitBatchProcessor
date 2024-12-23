"""
An extension to modify (show) level heads at one end. One end is the end point of the level line when it was created.

Usage:

- Run this script in a view where you want to switch all level heads at one end on.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from levels_and_headers.levels import switch_1_end_headers_on_in_view

# switches all headers at level end on
switch_1_end_headers_on_in_view(doc)
