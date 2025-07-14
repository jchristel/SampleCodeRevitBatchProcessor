"""
An extension to highlight any area lines in the active view which have warnings associated with them.

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

# highlight area lines with warnings in view
from solvers.warnings_highlighting import (
    highlight_area_lines_with_warnings_in_current_view,
)

highlight_area_lines_with_warnings_in_current_view(doc=doc, output=output, forms=forms)
