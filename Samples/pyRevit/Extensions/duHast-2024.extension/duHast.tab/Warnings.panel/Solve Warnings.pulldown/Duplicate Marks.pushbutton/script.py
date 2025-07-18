"""
An extension to solve duplicate mark warnings by clearing the mark value of the affected element instances

Note:

- This can be extended by providing a filter to only clear the mark value of the affected element instances that meet the filter criteria.

Usage:

- Run this script
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


from solvers.warnings_solvers import solve_duplicate_mark_warnings

solve_duplicate_mark_warnings(doc=doc, output=output, forms=forms)
