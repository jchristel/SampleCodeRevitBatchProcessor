"""
An extension to highlight any room separation lines in the active view which have warnings associated with them.

Note:

- Active view needs to be a plan view.


Usage:
- Run this script

"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# room lines reporting
from solvers.warnings_highlighting import (
    highlight_room_lines_with_warnings_in_current_view,
)

highlight_room_lines_with_warnings_in_current_view(doc=doc, output=output, forms=forms)
