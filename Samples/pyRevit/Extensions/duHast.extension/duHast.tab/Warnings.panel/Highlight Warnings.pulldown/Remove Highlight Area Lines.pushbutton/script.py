"""
An extension to remove any prior applied highlight to area lines in the active view which no longer have warnings associated with them.

Note:

- Active view needs to be an area plan view.


Usage:
- Run this script

"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# remove highlight from any area lines without warnings in view
from solvers.warnings_highlighting import (
    remove_highlight_area_lines_with_warnings_in_current_view,
)

remove_highlight_area_lines_with_warnings_in_current_view(
    doc=doc, output=output, forms=forms
)
