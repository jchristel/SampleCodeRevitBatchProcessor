"""
An extension to remove any prior applied highlight to room separation lines in the active view which no longer have warnings associated with them.

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
from solvers.warnings_highlighting import remove_highlight_from_room_lines_without_warnings_in_current_view

remove_highlight_from_room_lines_without_warnings_in_current_view(doc=doc, output=output, forms=forms)