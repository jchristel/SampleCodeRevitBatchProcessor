"""
An extension to purge selected line patterns.

Note:

- This script implements a try and roll back pattern to identify any line patterns nominated to be purged that are in use. If a line pattern is in use, it will not be purged.

Usage:

- Run this script
- Select the line patterns to be purged.
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge line patterns by selection
from purge.purge_patterns_and_styles import purge_line_patterns_by_selection

purge_line_patterns_by_selection(doc=doc, output=output, forms=forms)
