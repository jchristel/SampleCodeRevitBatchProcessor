"""
An extension to solve area lines overlap warnings by extending the longer of the two overlapping lines to the extend of the smaller of the two lines and then deleting the smaller line.

Usage:

- Run this script
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# area lines overlap -> long
from solvers.warnings_solvers import solve_duplicate_area_separation_lines_long

solve_duplicate_area_separation_lines_long(doc=doc, output=output, forms=forms)
