"""
An extension to modify, switch off, all level heads in a view.

Usage:

- Run this script in a view where you want to switch off all level heads.
"""

# pyrevit stuff
from pyrevit import revit, script

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from levels_and_headers.levels import switch_all_headers_off_in_view

# switches all level headers in the active view off
switch_all_headers_off_in_view(doc)
