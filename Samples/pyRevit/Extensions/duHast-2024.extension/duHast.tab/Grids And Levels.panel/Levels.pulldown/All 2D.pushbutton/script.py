"""
An extension to set both ends of a level lines two 2D.

Usage:

- Run this script in a view where you want to switch all level ends two 2D.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from levels_and_headers.levels import set_levels_in_view_to_2d

# switches all levels to 2D
set_levels_in_view_to_2d(doc)
