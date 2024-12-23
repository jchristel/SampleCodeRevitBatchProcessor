"""
An extension to solve area lines overlap warnings by shortening the longer of the two overlapping lines to the extend of the smaller of the two lines.

Usage:

- Run this script
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


# area lines overlap -> short
from solvers.warnings_solvers import solve_duplicate_area_separation_lines_short

solve_duplicate_area_separation_lines_short(doc=doc, output=output, forms=forms)
